import click
from streamingcli.platform.ververica.webtoken_factory import VervericaWebTokenFactory


class PlatformSetupCommand:

    @staticmethod
    def setup_ververica(ververica_url: str, ververica_namespace: str, kubernetes_namespace: str):
        click.echo(f"Generate Ververica WebToken ...")
        webtoken = VervericaWebTokenFactory.create_token(ververica_url=ververica_url, ververica_namespace=ververica_namespace)
        if webtoken is None:
            raise click.ClickException("Ververica WebToken generation error")
        click.echo(f"Ververica WebToken: {webtoken['name']} generated")

        streaming_platform_secret_name = "streaming-platform-secret"
        # TODO store webtoken in K8S secret
        click.echo(f"Ververica WebToken stored in Kubernetes secret name: {streaming_platform_secret_name}")

        streaming_platform_configmap_name = "streaming-platform-config"
        streaming_platform_config = {
            "ververica_url": ververica_url,
            "ververica_namespace": ververica_namespace,
            "secret_name": streaming_platform_secret_name,
            "kubernetes_namespace": kubernetes_namespace
        }
        # TODO store URL and secret_name in K8S configmap
        click.echo(f"Streaming platform configuration stored in Kubernetes configmap name: {streaming_platform_configmap_name}")

        click.echo(f"Streaming Platform setup finished")

