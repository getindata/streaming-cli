import json
from typing import Optional

import click

from streamingcli.platform.k8s.secret_adapter import KubernetesSecretAdapter
from streamingcli.platform.ververica.apitoken_adapter import VervericaApiTokenAdapter


class VervericaApiTokenCreateCommand:
    @staticmethod
    def create_apitoken(
        ververica_url: str,
        ververica_namespace: str,
        token_name: str,
        token_role: str,
        k8s_secret: Optional[str] = None,
    ) -> None:
        token_data = VervericaApiTokenAdapter.create_token(
            ververica_url=ververica_url,
            ververica_namespace=ververica_namespace,
            apitoken_name=token_name,
            apitoken_role=token_role,
        )
        click.echo(json.dumps(token_data, indent=4, sort_keys=True))

        if k8s_secret is not None:
            secret_params = k8s_secret.split("/")
            secret_namespace = secret_params[0]
            secret_name = secret_params[1]

            KubernetesSecretAdapter.save_k8s_secret(
                secret_name=secret_name,
                namespace=secret_namespace,
                secret_data=token_data,
            )
            click.echo(f"Saved k8s secret {k8s_secret}")
