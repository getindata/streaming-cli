import os
from dataclasses import replace
from typing import Optional

import click
from jinja2 import Environment
from streamingcli.Config import PROFILE_ENV_VARIABLE_NAME
from streamingcli.platform.ververica.deployment_adapter import \
    DeploymentAdapter
from streamingcli.profile.profile_command import ProfileCommand, ScliProfile
from streamingcli.project.local_project_config import LocalProjectConfigIO
from streamingcli.project.template_loader import TemplateLoader
from streamingcli.project.yaml_merger import YamlMerger


class ProjectDeployer:
    @staticmethod
    def get_profile_name(profile_name: Optional[str]) -> Optional[str]:
        if profile_name is not None:
            return profile_name
        else:
            return os.getenv(PROFILE_ENV_VARIABLE_NAME)

    @staticmethod
    def deploy_project(docker_image_tag: str,
                       profile: Optional[str] = None,
                       ververica_url: Optional[str] = None,
                       ververica_namespace: Optional[str] = None,
                       ververica_deployment_target_name: Optional[str] = None,
                       ververica_webtoken_secret: Optional[str] = None,
                       docker_registry_url: Optional[str] = None,
                       overrides_from_yaml: Optional[str] = None):

        local_project_config = LocalProjectConfigIO.load_project_config()

        profile_name = ProjectDeployer.get_profile_name(profile_name=profile)

        if profile_name is not None:
            profile_data = ProfileCommand.get_profile(profile_name=profile_name)
        else:
            profile_data = ScliProfile(profile_name="temporary")

        profile_data = ProjectDeployer.update_profile_data(
            profile_data=profile_data,
            ververica_url=ververica_url,
            ververica_namespace=ververica_namespace,
            ververica_deployment_target_name=ververica_deployment_target_name,
            ververica_webtoken_secret=ververica_webtoken_secret,
            docker_registry_url=docker_registry_url
        )
        ProjectDeployer.validate_profile_data(profile_data=profile_data, docker_image_tag=docker_image_tag)

        # Generate deployment YAML
        deployment_yml = ProjectDeployer.generate_project_template(
            project_name=local_project_config.project_name,
            docker_registry_url=profile_data.docker_registry_url,
            docker_image_tag=docker_image_tag,
            deployment_target_name=profile_data.ververica_deployment_target
        )
        if overrides_from_yaml:
            deployment_yml = YamlMerger.merge_two_yaml(deployment_yml, overrides_from_yaml)
        click.echo(f"Deploying streaming project: {local_project_config.project_name} ...")

        deployment_name = DeploymentAdapter.deploy(
            deployment_yml=deployment_yml,
            ververica_url=profile_data.ververica_url,
            ververica_namespace=profile_data.ververica_namespace,
            auth_token=profile_data.ververica_api_token
        )
        click.echo(f"Created deployment: "
                   f"{profile_data.ververica_url}/app/#/namespaces/"
                   f"{profile_data.ververica_namespace}/deployments/{deployment_name}")

    @staticmethod
    def update_profile_data(profile_data, ververica_url, ververica_namespace, ververica_deployment_target_name,
                            ververica_webtoken_secret, docker_registry_url):
        deployment_params = {
            'ververica_url': ververica_url,
            'ververica_namespace': ververica_namespace,
            'ververica_deployment_target_name': ververica_deployment_target_name,
            'ververica_api_token': ververica_webtoken_secret,
            'docker_registry_url': docker_registry_url
        }

        non_empty_deployment_params = {
            key: value for (key, value) in deployment_params.items() if value is not None
        }

        profile_data = replace(profile_data, **non_empty_deployment_params)
        click.echo(profile_data)
        return profile_data

    @staticmethod
    def validate_profile_data(profile_data: ScliProfile, docker_image_tag: str):
        if profile_data.ververica_url is None:
            raise click.ClickException("Missing Ververica URL attribute or profile")
        if profile_data.ververica_namespace is None:
            raise click.ClickException("Missing Ververica Namespace attribute or profile")
        if profile_data.ververica_deployment_target is None:
            raise click.ClickException("Missing Ververica Deployment Target Name attribute or profile")
        if profile_data.ververica_api_token is None:
            raise click.ClickException("Missing Ververica APIToken secret attribute or profile")
        if profile_data.docker_registry_url is None:
            raise click.ClickException("Missing Docker repository URL attribute or profile")
        if docker_image_tag is None or len(docker_image_tag) == 0:
            raise click.ClickException("Missing Docker image tag attribute")

    @staticmethod
    def generate_project_template(
            project_name: str,
            docker_registry_url: str,
            docker_image_tag: str,
            deployment_target_name: str
    ) -> str:
        template = TemplateLoader.load_project_template("flink_deployment.yml")
        return Environment().from_string(template).render(
            project_name=project_name,
            docker_registry_url=docker_registry_url,
            docker_image_tag=docker_image_tag,
            deployment_target_id=deployment_target_name
        )
