from typing import Optional

import click
from kubernetes import utils
import yaml

from streamingcli.platform.deployment_adapter import DeploymentAdapter
from streamingcli.platform.k8s.config_loader import KubernetesConfigLoader


class K8SDeploymentAdapter(DeploymentAdapter):

    def deploy(self, deployment_yml: Optional[str]) -> Optional[str]:
        k8s_client = KubernetesConfigLoader.get_client()
        utils.create_from_dict(k8s_client, yaml.load(deployment_yml), namespace=self.profile_data.k8s_namespace)

        return f"Created FlinkDeployment: {self.project_name}"

    def validate_profile_data(self) -> None:
        if self.profile_data.k8s_namespace is None:
            raise click.ClickException(
                "Missing K8S Namespace attribute or profile"
            )
        if self.profile_data.docker_registry_url is None:
            raise click.ClickException(
                "Missing Docker repository URL attribute or profile"
            )
        if self.docker_image_tag is None or len(self.docker_image_tag) == 0:
            raise click.ClickException("Missing Docker image tag attribute")

    @staticmethod
    def get_template_name() -> str:
        return "k8s_flink_deployment.yml"

