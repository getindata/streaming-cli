from typing import Optional

import click
import requests
from requests.models import Response

from streamingcli.platform.deployment_adapter import DeploymentAdapter


class VervericaDeploymentAdapter(DeploymentAdapter):
    def deploy(self, deployment_yml: str) -> Optional[str]:
        deployment_url = (
            f"{self.profile_data.config['vvp']['url']}/api/v1/namespaces/"
            + f"{self.profile_data.config['vvp']['namespace']}/deployments/{self.project_name}"
        )

        response = self.put_deployment_file(deployment_yml, deployment_url)

        if response.ok:
            return (
                f"Status {response.status_code}. Deployment: {deployment_url} \n"
                + f"{response.text}"
            )

        raise click.ClickException(
            f"Failed to PUT deployment.yaml file. Status code: {response.status_code}. "
            f"{response.text}"
        )

    def validate_profile_data(self) -> None:
        if self.profile_data.config["vvp"]["url"] is None:
            raise click.ClickException("Missing Ververica URL attribute or profile")
        if self.profile_data.config["vvp"]["namespace"] is None:
            raise click.ClickException(
                "Missing Ververica Namespace attribute or profile"
            )
        if self.profile_data.config["vvp"]["deployment_target"] is None:
            raise click.ClickException(
                "Missing Ververica Deployment Target Name attribute or profile"
            )
        if self.profile_data.config["vvp"]["api_token"] is None:
            raise click.ClickException(
                "Missing Ververica APIToken secret attribute or profile"
            )
        if self.profile_data.docker_registry_url is None:
            raise click.ClickException(
                "Missing Docker repository URL attribute or profile"
            )
        if self.docker_image_tag is None or len(self.docker_image_tag) == 0:
            raise click.ClickException("Missing Docker image tag attribute")

    def put_deployment_file(
        self, deployment_file: str, deployment_url: str
    ) -> Response:
        response = requests.put(
            url=deployment_url,
            data=deployment_file,
            headers={
                "Content-Type": "application/yaml",
                "Authorization": f"Bearer {self.profile_data.config['vvp']['api_token']}",
            },
        )
        return response
