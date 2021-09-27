import click
from streamingcli.platform.ververica.webtoken_factory import VervericaWebTokenFactory
from streamingcli.platform.k8s.secret_adapter import KubernetesSecretAdapter
from streamingcli.platform.platform_config_map import (
    PlatformConfig,
    PlatformConfigAdapter
)
from streamingcli.Config import PLATFORM_K8S_SECRET_NAME


class PlatformSetupCommand:

    @staticmethod
    def setup_ververica(ververica_url: str, ververica_namespace: str, ververica_kubernetes_namespace: str):
        click.echo(f"Generate Ververica WebToken ...")
        webtoken = VervericaWebTokenFactory.create_token(ververica_url=ververica_url, ververica_namespace=ververica_namespace)
        if webtoken is None:
            raise click.ClickException("Ververica WebToken generation error")
        click.echo(f"Ververica WebToken: {webtoken['name']} generated")

        click.echo("Ververica WebToken stored in Kubernetes secret")
        KubernetesSecretAdapter.save_k8s_secret(secret_name=PLATFORM_K8S_SECRET_NAME, namespace=ververica_kubernetes_namespace, secret_data=webtoken)

        streaming_platform_config = PlatformConfig(
            ververica_url=ververica_url,
            ververica_namespace=ververica_namespace,
            secret_name=PLATFORM_K8S_SECRET_NAME,
            ververica_kubernetes_namespace=ververica_kubernetes_namespace
        )
        PlatformConfigAdapter.save_platform_config(streaming_platform_config)
        click.echo("Streaming platform configuration stored in Kubernetes configmap")

        click.echo(f"Streaming Platform setup finished")

