import os
from typing import Optional

import click
from jinja2 import Environment
from streamingcli.Config import PROFILE_ENV_VARIABLE_NAME
from streamingcli.platform.ververica.deployment_adapter import \
    DeploymentAdapter
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
    def deploy_project(profile: Optional[str] = None,
                        ververica_url: Optional[str] = None,
                        ververica_namespace: Optional[str] = None,
                        ververica_deployment_target_name: Optional[str] = None,
                        ververica_webtoken_secret: Optional[str] = None,
                        docker_registry_url: Optional[str] = None,
                        docker_image_tag: Optional[str] = None,
                        overrides_from_yaml: Optional[str] = None):
        profile_name = ProjectDeployer.get_profile_name(profile_name=profile)

        # TODO Use ScliProfile dataclass instead
        profile_data = {}

        # TODO Load profile data for {profile_name}
        # Load platform ConfigMap


        # Explicitly defined parameters will override profile ones
        if ververica_url is not None:
            profile_data["ververica_url"] = ververica_url
        if ververica_namespace is not None:
            profile_data["ververica_namespace"] = ververica_namespace
        if ververica_deployment_target_name is not None:
            profile_data["ververica_deployment_target_name"] = ververica_deployment_target_name
        if ververica_webtoken_secret is not None:
            profile_data["ververica_webtoken_secret"] = ververica_webtoken_secret
        if docker_registry_url is not None:
            profile_data["docker_registry_url"] = docker_registry_url
        if docker_image_tag is not None:
            profile_data["docker_image_tag"] = docker_image_tag

        # Load local project config
        local_project_config = LocalProjectConfigIO.load_project_config()

        # Generate deployment YAML
        deployment_yml = ProjectDeployer.generate_project_template(
            project_name=local_project_config.project_name,
            docker_registry_url=profile_data["docker_registry_url"],
            docker_image_tag=profile_data["docker_image_tag"],
            deployment_target_name=profile_data["ververica_deployment_target_name"]
        )
        if overrides_from_yaml:
            deployment_yml = YamlMerger.merge_two_yaml(deployment_yml, overrides_from_yaml)
        click.echo(f"Deploying streaming project: {local_project_config.project_name} ...")

        deployment_name = DeploymentAdapter.deploy(
            deployment_yml=deployment_yml,
            ververica_url=profile_data["ververica_url"],
            ververica_namespace=profile_data["ververica_namespace"],
            auth_token=profile_data["ververica_webtoken_secret"]
        )
        click.echo(f"Created deployment: "
                    f"{profile_data['ververica_url']}/app/#/namespaces/"
                    f"{profile_data['ververica_namespace']}/deployments/{deployment_name}")

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
