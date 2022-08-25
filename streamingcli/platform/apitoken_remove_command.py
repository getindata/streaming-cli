import click

from streamingcli.platform.ververica.apitoken_adapter import VervericaApiTokenAdapter


class VervericaApiTokenRemoveCommand:
    @staticmethod
    def remove_apitoken(
        ververica_url: str, ververica_namespace: str, token_name: str
    ) -> None:
        VervericaApiTokenAdapter.remove_token(
            ververica_url=ververica_url,
            ververica_namespace=ververica_namespace,
            apitoken_name=token_name,
        )
        click.echo("Ververica API token removed")
