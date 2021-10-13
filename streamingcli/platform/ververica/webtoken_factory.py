from typing import Dict, Optional
import requests
import json
import click
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class VervericaWebToken:
    name: str
    secret: str


class VervericaWebTokenFactory:
    @staticmethod
    def create_token(ververica_url: str, ververica_namespace: str) -> Optional[VervericaWebToken]:
        apitokens_url = f"{ververica_url}/apitokens/v1/namespaces/{ververica_namespace}/apitokens"
        webtoken_name = f"namespaces/{ververica_namespace}/apitokens/ci-token"
        request_body = {
            "name": webtoken_name,
            "role": "editor"
        }
        response = requests.post(apitokens_url, json.dumps(request_body), headers={
            "accept": "application/json",
            "Content-Type": "application/json"
        })
        if response.status_code == 200:
            webtoken_secret = response.json()["apiToken"]["secret"]
            return VervericaWebToken(name=webtoken_name, secret=webtoken_secret)
        elif response.status_code == 409:
            raise click.ClickException("Ververica WebToken already exists! Remove it first")
        else:
            raise click.ClickException(f"Ververica WebToken generation error: {response.status_code}")

    @staticmethod
    def delete_token(ververica_url: str, ververica_namespace: str):
        webtoken_name = f"namespaces/{ververica_namespace}/apitokens/ci-token"
        apitokens_url = f"{ververica_url}/apitokens/v1/{webtoken_name}"
        response = requests.delete(apitokens_url)
        if response.status_code != 200 and response.status_code != 404:
            raise click.ClickException("Cant remove Ververica WebToken")
