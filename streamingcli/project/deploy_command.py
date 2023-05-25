import os
from typing import Any, Optional

import click

from streamingcli.config import DEFAULT_PROFILE, PROFILE_ENV_VARIABLE_NAME
from streamingcli.platform.deployment_adapter import DeploymentAdapter
from streamingcli.platform.k8s.deployment_adapter import K8SDeploymentAdapter
from streamingcli.platform.ververica.deployment_adapter import (
    VervericaDeploymentAdapter,
)
from streamingcli.profile.profile_adapter import DeploymentMode, ProfileAdapter
from streamingcli.project.local_project_config import LocalProjectConfigIO


class ProjectDeployer:
    @staticmethod
    def get_profile_name(profile_name: Optional[str]) -> str:
        return profile_name or os.getenv(PROFILE_ENV_VARIABLE_NAME) or DEFAULT_PROFILE

    @staticmethod
    def deploy_project(
        docker_image_tag: str,
        env: Optional[str] = None,
        ververica_webtoken_secret: Optional[str] = None,
        file_descriptor_path: Optional[str] = None,
    ) -> None:

        profile_name = ProjectDeployer.get_profile_name(profile_name=env)
        profile_data = ProfileAdapter.get_profile(profile_name=profile_name)

        local_project_config = LocalProjectConfigIO.load_project_config()
        profile_data = ProfileAdapter.update_token(
            profile_data=profile_data,
            ververica_webtoken_secret=ververica_webtoken_secret,
        )
        deployment_adapter = DeploymentAdapterFactory.get_adapter(
            profile_data.deployment_mode,
            profile_data=profile_data,
            docker_image_tag=docker_image_tag,
            project_name=local_project_config.project_name,
        )

        # Generate deployment YAML
        deployment_yml = deployment_adapter.generate_project_template(
            local_project_config.dependencies,
            file_descriptor_path,
        )

        click.echo(
            f"Deploying streaming project: {local_project_config.project_name} ..."
        )
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
