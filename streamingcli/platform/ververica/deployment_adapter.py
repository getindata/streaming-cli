from typing import Optional

import click
import requests
from requests.models import Response

from streamingcli.platform.deployment_adapter import DeploymentAdapter


class VervericaDeploymentAdapter(DeploymentAdapter):
    def deploy(self, deployment_yml: str) -> Optional[str]:
        response = self.post_deployment_file(deployment_yml)

        if response.status_code != 201:
            raise click.ClickException("Failed to POST deployment.yaml file")
        else:
            deployment_name = response.json()["metadata"]["name"]
            return (
                "Created deployment: "
                + f"{self.profile_data.ververica_url}/app/#/namespaces/"
                + f"{self.profile_data.ververica_namespace}/deployments/{deployment_name}"
            )

    def validate_profile_data(self) -> None:
        if self.profile_data.ververica_url is None:
            raise click.ClickException("Missing Ververica URL attribute or profile")
        if self.profile_data.ververica_namespace is None:
            raise click.ClickException(
                "Missing Ververica Namespace attribute or profile"
            )
        if self.profile_data.ververica_deployment_target is None:
            raise click.ClickException(
                "Missing Ververica Deployment Target Name attribute or profile"
            )
        if self.profile_data.ververica_api_token is None:
            raise click.ClickException(
                "Missing Ververica APIToken secret attribute or profile"
            )
        if self.profile_data.docker_registry_url is None:
            raise click.ClickException(
                "Missing Docker repository URL attribute or profile"
            )
        if self.docker_image_tag is None or len(self.docker_image_tag) == 0:
            raise click.ClickException("Missing Docker image tag attribute")

    @staticmethod
    def get_template_name() -> str:
        return "vvp_flink_deployment.yml"

    def post_deployment_file(self, deployment_file: str) -> Response:
        deployments_url = (
            f"{self.profile_data.ververica_url}/api/v1/namespaces/"
            + f"{self.profile_data.ververica_namespace}/deployments"
        )

        response = requests.post(
            url=deployments_url,
            data=deployment_file,
            headers={
                "Content-Type": "application/yaml",
                "Authorization": f"Bearer {self.profile_data.ververica_api_token}",
            },
        )
        return response
