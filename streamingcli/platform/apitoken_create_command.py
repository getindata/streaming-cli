from streamingcli.platform.ververica.apitoken_adapter import VervericaApiTokenAdapter
import click
import json

class VervericaApiTokenCreateCommand:
    @staticmethod
    def create_apitoken(ververica_url: str,
                        ververica_namespace: str,
                        token_name: str,
                        token_role: str):
        token_data = VervericaApiTokenAdapter.create_token(ververica_url=ververica_url,
                                                           ververica_namespace=ververica_namespace,
                                                           apitoken_name=token_name,
                                                           apitoken_role=token_role)
        click.echo(json.dumps(token_data, indent=4, sort_keys=True))
