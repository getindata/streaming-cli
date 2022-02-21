from typing import Optional

import click
import requests
from requests.models import Response


class VervericaDeploymentAdapter:

    @staticmethod
    def deploy(deployment_yml: str,
               ververica_url: str,
               ververica_namespace: str,
               auth_token: str) -> Optional[str]:
        deployments_url = f"{ververica_url}/api/v1/namespaces/{ververica_namespace}/deployments"
        response = VervericaDeploymentAdapter.post_deployment_file(deployments_url, auth_token, deployment_yml)

        if response.status_code != 201:
            raise click.ClickException("Failed to POST deployment.yaml file")
        else:
            deployment_name = response.json()["metadata"]["name"]
            return deployment_name

    @staticmethod
    def post_deployment_file(deployments_url: str, auth_token: str, deployment_file: str) -> Response:
        response = requests.post(
                url=deployments_url,
                data=deployment_file,
                headers={
                    "Content-Type": "application/yaml",
                    "Authorization": f"Bearer {auth_token}"
                }
            )
        return response
