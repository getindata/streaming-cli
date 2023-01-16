import os
from typing import Any, Optional

import click

from streamingcli.config import PROFILE_ENV_VARIABLE_NAME
from streamingcli.platform.deployment_adapter import DeploymentAdapter
from streamingcli.platform.k8s.deployment_adapter import K8SDeploymentAdapter
from streamingcli.platform.ververica.deployment_adapter import (
    VervericaDeploymentAdapter,
)
from streamingcli.profile.profile_adapter import (
    DeploymentMode,
    ProfileAdapter,
    ScliProfile,
)
from streamingcli.project.local_project_config import LocalProjectConfigIO
from streamingcli.project.yaml_merger import YamlMerger


class ProjectDeployer:
    @staticmethod
    def get_profile_name(profile_name: Optional[str]) -> Optional[str]:
        if profile_name is not None:
            return profile_name
        else:
            return os.getenv(PROFILE_ENV_VARIABLE_NAME)

    @staticmethod
    def deploy_project(
        docker_image_tag: str,
        docker_registry_url: Optional[str] = None,
        docker_image_repository: Optional[str] = None,
        profile: Optional[str] = None,
        deployment_mode: Optional[DeploymentMode] = None,
        ververica_url: Optional[str] = None,
        ververica_namespace: Optional[str] = None,
        ververica_deployment_target_name: Optional[str] = None,
        ververica_webtoken_secret: Optional[str] = None,
        k8s_namespace: Optional[str] = None,
        overrides_from_yaml: Optional[str] = None,
    ) -> None:

        profile_name = ProjectDeployer.get_profile_name(profile_name=profile)
        if profile_name is None:
            profile_data = ScliProfile(profile_name="temporary")
        else:
            profile_data = ProfileAdapter.get_profile(
                profile_name=profile_name
            ) or ScliProfile(profile_name="temporary")

        local_project_config = LocalProjectConfigIO.load_project_config()
        project_name = docker_image_repository or local_project_config.project_name
        profile_data = ProfileAdapter.update_profile_data(
            profile_data=profile_data,
            deployment_mode=deployment_mode,
            ververica_url=ververica_url,
            ververica_namespace=ververica_namespace,
            ververica_deployment_target_name=ververica_deployment_target_name,
            ververica_webtoken_secret=ververica_webtoken_secret,
            docker_registry_url=docker_registry_url,
            k8s_namespace=k8s_namespace,
        )
        deployment_adapter = DeploymentAdapterFactory.get_adapter(
            profile_data.deployment_mode,
            profile_data=profile_data,
            docker_image_tag=docker_image_tag,
            project_name=project_name,
        )

        # Generate deployment YAML
        deployment_yml = deployment_adapter.generate_project_template(
            local_project_config.dependencies
        )

        if overrides_from_yaml:
            deployment_yml = YamlMerger.merge_two_yaml(
                deployment_yml, overrides_from_yaml
            )

        click.echo(f"Deploying streaming project: {project_name} ...")
        msg = deployment_adapter.deploy(deployment_yml)
        click.echo(msg)


class DeploymentAdapterFactory:
    @staticmethod
    def get_adapter(
        deployment_mode: Optional[DeploymentMode], **kwargs: Any
    ) -> DeploymentAdapter:
        if deployment_mode == DeploymentMode.K8S_OPERATOR:
            return K8SDeploymentAdapter(**kwargs)
        if deployment_mode == DeploymentMode.VVP:
            return VervericaDeploymentAdapter(**kwargs)
        raise click.ClickException("Unsupported deployment mode")
