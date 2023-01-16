import os
from typing import Optional

import click
import requests
import yaml
from kubernetes.config import KUBE_CONFIG_DEFAULT_LOCATION
from requests import Response

from streamingcli.platform.deployment_adapter import DeploymentAdapter


class K8SDeploymentAdapter(DeploymentAdapter):
    def deploy(self, deployment_yml: str) -> Optional[str]:
        self.load_k8s_config()

        response = self.post_deployment_file(deployment_yml)

        if response.status_code != 201:
            raise click.ClickException("Failed to POST deployment.yaml file")
        else:
            deployment_name = response.json()["metadata"]["name"]
            namespace = response.json()["metadata"]["namespace"]
            return f"Created deployment: {deployment_name} (namespace: {namespace})"

    def validate_profile_data(self) -> None:
        if self.profile_data.k8s_namespace is None:
            raise click.ClickException("Missing K8S Namespace attribute or profile")
        if self.profile_data.docker_registry_url is None:
            raise click.ClickException(
                "Missing Docker repository URL attribute or profile"
            )
        if self.docker_image_tag is None or len(self.docker_image_tag) == 0:
            raise click.ClickException("Missing Docker image tag attribute")

    @staticmethod
    def get_template_name() -> str:
        return "k8s_flink_deployment.yml"

    def post_deployment_file(self, deployment_file: str) -> Response:
        deployments_url = (
            f"{self.cluster}/apis/flink.apache.org/v1beta1/namespaces/"
            + f"{self.profile_data.k8s_namespace}/flinkdeployments"
        )

        response = requests.post(
            url=deployments_url,
            data=deployment_file,
            verify=self.ca_crt,
            cert=(self.client_crt, self.client_key),
            headers={
                "Content-Type": "application/yaml",
            },
        )
        return response

    def load_k8s_config(self) -> None:
        path = os.path.expanduser(KUBE_CONFIG_DEFAULT_LOCATION)
        with open(path, "r") as stream:
            parsed_yaml = yaml.safe_load(stream)
            current_context = parsed_yaml["current-context"]
            for cluster in parsed_yaml["clusters"]:
                if cluster["name"] == current_context:
                    self.ca_crt = cluster["cluster"]["certificate-authority"]
                    self.cluster = cluster["cluster"]["server"]
            for user in parsed_yaml["users"]:
                if user["name"] == current_context:
                    self.client_crt = user["user"]["client-certificate"]
                    self.client_key = user["user"]["client-key"]
