from typing import Dict

from streamingcli.platform.ververica.webtoken_factory import VervericaWebTokenFactory
from streamingcli.project.template_loader import TemplateLoader
from jinja2 import Environment
import requests
import yaml
import click


class VervericaDeploymentTargetFactory:
    @staticmethod
    def create_deployment_target(ververica_url: str,
                                 ververica_namespace: str,
                                 ververica_kubernetes_namespace: str,
                                 ververica_webtoken: Dict,
                                 ververica_deployment_target_name: str):
        deployment_target_template = TemplateLoader.load_project_template("deployment_target.yml")
        request_payload = Environment().from_string(deployment_target_template).render(
            ververica_deployment_target_name=ververica_deployment_target_name,
            ververica_namespace=ververica_namespace,
            ververica_kubernetes_namespace=ververica_kubernetes_namespace
        )

        dp_url = f"{ververica_url}/api/v1/namespaces/{ververica_namespace}/deployment-targets"
        response = requests.post(dp_url, request_payload, headers={
            "accept": "application/yaml",
            "Content-Type": "application/yaml",
            "Authorization": f"Bearer {ververica_webtoken[VervericaWebTokenFactory.WEBTOKEN_SECRET_ATTRIBUTE]}",
        })
        if response.status_code == 400:
            response = requests.get(dp_url, request_payload, headers={
                "accept": "application/yaml",
                "Content-Type": "application/yaml",
                "Authorization": f"Bearer {ververica_webtoken[VervericaWebTokenFactory.WEBTOKEN_SECRET_ATTRIBUTE]}",
            })
            all_deployment_targets = yaml.safe_load(response.content)
            for item in all_deployment_targets["items"]:
                if item["metadata"]["name"] == ververica_deployment_target_name:
                    deployment_target_id = item["metadata"]["id"]
                    click.echo(f"Reused existing Ververica deployment target: {ververica_deployment_target_name} with ID: {deployment_target_id}")
                    return deployment_target_id

        if response.status_code != 201:
            raise click.ClickException(f"Ververica DeploymentTarget creation error: {response.content}")
        deployment_target = yaml.safe_load(response.content)
        deployment_target_id = deployment_target["metadata"]["id"]
        click.echo(f"Ververica deployment target: {ververica_deployment_target_name} created with ID: {deployment_target_id}")
        return deployment_target_id

