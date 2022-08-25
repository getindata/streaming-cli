from typing import Optional

import click

from streamingcli.platform.ververica.deployment_target_adapter import (
    VervericaDeploymentTargetAdapter,
)
from streamingcli.profile.profile_adapter import ProfileAdapter, ScliProfile


class DeploymentTargetCommand:
    @staticmethod
    def create_deployment_target(
        kubernetes_namespace: str,
        profile_name: str,
        deployment_target_name: Optional[str] = None,
        ververica_url: Optional[str] = None,
        ververica_namespace: Optional[str] = None,
        vvp_api_token: Optional[str] = None,
        registry_url: Optional[str] = None,
    ) -> None:
        profile = ProfileAdapter.get_or_create_temporary(profile_name)

        profile = ProfileAdapter.update_profile_data(
            profile_data=profile,
            ververica_url=ververica_url,
            ververica_namespace=ververica_namespace,
            ververica_deployment_target_name=deployment_target_name,
            ververica_webtoken_secret=vvp_api_token,
            docker_registry_url=registry_url,
        )
        DeploymentTargetCommand.validate_scli_profile(profile)
        if (
            profile.ververica_url is not None
            and profile.ververica_namespace is not None
            and profile.ververica_deployment_target is not None
            and profile.ververica_api_token is not None
        ):
            VervericaDeploymentTargetAdapter.create_deployment_target(
                ververica_url=profile.ververica_url,
                ververica_namespace=profile.ververica_namespace,
                ververica_kubernetes_namespace=kubernetes_namespace,
                ververica_webtoken_secret=profile.ververica_api_token,
                ververica_deployment_target_name=profile.ververica_deployment_target,
            )
        else:
            raise click.ClickException(
                "Missing one of deployment attribute: ververica_namespace, "
                "kubernetes_namespace, ververica_api_token, ververica_deployment_target"
            )

    @staticmethod
    def validate_scli_profile(profile_data: ScliProfile) -> None:
        if profile_data.ververica_url is None:
            raise click.ClickException("Missing Ververica URL attribute")
        if profile_data.ververica_namespace is None:
            raise click.ClickException("Missing Ververica Namespace attribute")
        if profile_data.ververica_deployment_target is None:
            raise click.ClickException(
                "Missing Ververica Deployment Target Name attribute"
            )
        if profile_data.ververica_api_token is None:
            raise click.ClickException("Missing Ververica APIToken secret attribute")
