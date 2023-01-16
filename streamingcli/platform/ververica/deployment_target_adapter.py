from typing import Optional

import click
import requests
import yaml
from jinja2 import Environment

from streamingcli.project.template_loader import TemplateLoader


class VervericaDeploymentTargetAdapter:
    @staticmethod
    def get_existing_deployment_target_id_by_name(
        ververica_url: str,
        ververica_namespace: str,
        ververica_webtoken_secret: str,
        ververica_deployment_target_name: str,
    ) -> Optional[str]:
        dp_url = f"{ververica_url}/api/v1/namespaces/{ververica_namespace}/deployment-targets"
        response = requests.get(
            dp_url,
            headers={
                "accept": "application/yaml",
                "Content-Type": "application/yaml",
                "Authorization": f"Bearer {ververica_webtoken_secret}",
            },
        )
        all_deployment_targets = yaml.safe_load(response.content)
        for item in all_deployment_targets["items"]:
            if item["metadata"]["name"] == ververica_deployment_target_name:
                deployment_target_id = item["metadata"]["id"]
                click.echo(
                    f"Reused existing Ververica deployment target: {ververica_deployment_target_name}"
                    + f" with ID: {deployment_target_id}"
                )
                return deployment_target_id
        return None

    @staticmethod
    def format_template(
        ververica_kubernetes_namespace: str,
        ververica_namespace: str,
        ververica_deployment_target_name: str,
    ) -> str:
        deployment_target_template = TemplateLoader.load_project_template(
            "deployment_target.yml"
        )
        return (
            Environment()
            .from_string(deployment_target_template)
            .render(
                ververica_deployment_target_name=ververica_deployment_target_name,
                ververica_namespace=ververica_namespace,
                ververica_kubernetes_namespace=ververica_kubernetes_namespace,
            )
        )

    @staticmethod
    def create_deployment_target(
        ververica_url: str,
        ververica_namespace: str,
        ververica_kubernetes_namespace: str,
        ververica_webtoken_secret: str,
        ververica_deployment_target_name: str,
    ) -> str:
        deployment_target_id = (
            VervericaDeploymentTargetAdapter.get_existing_deployment_target_id_by_name(
                ververica_url=ververica_url,
                ververica_namespace=ververica_namespace,
                ververica_webtoken_secret=ververica_webtoken_secret,
                ververica_deployment_target_name=ververica_deployment_target_name,
            )
        )
        if deployment_target_id is not None:
            click.echo(
                f"Reused existing Ververica deployment target: {ververica_deployment_target_name}"
                + f" with ID: {deployment_target_id}"
            )
            return deployment_target_id

        deployment_target_yaml: str = VervericaDeploymentTargetAdapter.format_template(
            ververica_deployment_target_name=ververica_deployment_target_name,
            ververica_namespace=ververica_namespace,
            ververica_kubernetes_namespace=ververica_kubernetes_namespace,
        )

        dp_url = f"{ververica_url}/api/v1/namespaces/{ververica_namespace}/deployment-targets"
        response = requests.post(
            dp_url,
            deployment_target_yaml,
            headers={
                "accept": "application/yaml",
                "Content-Type": "application/yaml",
                "Authorization": f"Bearer {ververica_webtoken_secret}",
            },
        )

        if response.status_code != 201:
            raise click.ClickException(
                f"Ververica DeploymentTarget creation error: {response.text}"
            )
        deployment_target = yaml.safe_load(response.content)
        deployment_target_id = deployment_target["metadata"]["id"]

        click.echo(
            f"Ververica deployment target: {ververica_deployment_target_name} created with ID: {deployment_target_id}"
        )
        return deployment_target_id
