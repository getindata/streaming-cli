import subprocess
from typing import Optional, Tuple

import click

from streamingcli.platform.deployment_adapter import DeploymentAdapter


class K8SDeploymentAdapter(DeploymentAdapter):
    def deploy(self, deployment_yml: str) -> Optional[str]:

        (stdout, stderr) = self._kubectl_apply(deployment_yml)

        if stderr:
            raise click.ClickException(
                f"Failed to kubectl apply deployment.yaml file: {str(stderr)}"
            )
        return str(stdout) if stdout else None

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

    @staticmethod
    def _kubectl_apply(deployment_yml: str) -> Tuple[bytes, bytes]:
        cmd = subprocess.Popen(
            ["kubectl apply -f -"], stdin=subprocess.PIPE, shell=True
        )
        return cmd.communicate(bytes(deployment_yml, "utf-8"), timeout=120)
