from typing import Optional

import click

from streamingcli.profile.profile_adapter import (
    DeploymentMode,
    ProfileAdapter,
    ScliProfile,
)


class ProfileCommand:
    @staticmethod
    def create_profile(
        profile_name: str,
        deployment_mode: str,
        ververica_url: Optional[str] = None,
        ververica_namespace: Optional[str] = None,
        ververica_deployment_target: Optional[str] = None,
        ververica_api_token: Optional[str] = None,
        docker_registry_url: Optional[str] = None,
        k8s_namespace: Optional[str] = None,
    ) -> None:
        scli_profile = ScliProfile(
            profile_name=profile_name,
            deployment_mode=DeploymentMode.from_label(deployment_mode),
            ververica_url=ververica_url,
            ververica_namespace=ververica_namespace,
            ververica_deployment_target=ververica_deployment_target,
            docker_registry_url=docker_registry_url,
            ververica_api_token=ververica_api_token,
            k8s_namespace=k8s_namespace,
        )
        ProfileAdapter.save_profile(scli_profile=scli_profile)
        click.echo(f"Scli profile {profile_name} saved")
