from typing import Dict

import requests
import json
import click


class VervericaApiTokenAdapter:
    @staticmethod
    def create_token(ververica_url: str, ververica_namespace: str, apitoken_name: str, apitoken_role: str) -> Dict:
        apitokens_url = f"{ververica_url}/apitokens/v1/namespaces/{ververica_namespace}/apitokens"
        webtoken_name = f"namespaces/{ververica_namespace}/apitokens/{apitoken_name}"
        request_body = {
            "name": webtoken_name,
            "role": apitoken_role
        }
        response = requests.post(apitokens_url, json.dumps(request_body), headers={
            "accept": "application/json",
            "Content-Type": "application/json"
        })
        if response.status_code == 200:
            webtoken_secret = response.json()["apiToken"]["secret"]

            token_object = {
                "namespace": ververica_namespace,
                "name": apitoken_name,
                "role": apitoken_role,
                "secret": webtoken_secret
            }

            return token_object
        elif response.status_code == 409:
            raise click.ClickException("Ververica WebToken already exists! Remove it first")
        else:
            raise click.ClickException(f"Ververica WebToken generation error: {response.status_code}")

    @staticmethod
    def delete_token(ververica_url: str, ververica_namespace: str, apitoken_name: str, ):
        apitokens_url = f"{ververica_url}/apitokens/v1/namespaces/{ververica_namespace}/apitokens/{apitoken_name}"
        response = requests.delete(apitokens_url)
        if response.status_code != 200 and response.status_code != 404:
            raise click.ClickException("Cant remove Ververica WebToken")
