from typing import Dict, Optional
import requests
import json

# curl --location --request POST 'https://vvp.streaming-platform.getindata.dev/apitokens/v1/namespaces/default/apitokens' \
# --header 'accept: application/json' \
# --header 'Content-Type: application/json' \
# --data-raw '{
#   "name": "namespaces/default/apitokens/ci-token",
#   "role": "editor"
# }'

# {
#     "apiToken": {
#         "name": "namespaces/default/apitokens/ci-token",
#         "secret": "xxx",
#         "role": "editor",
#         "createTime": "2021-09-02T09:21:20.875745Z"
#     }
# }


class VervericaWebTokenFactory:

    @staticmethod
    def create_token(ververica_url: str, ververica_namespace: str) -> Optional[Dict]:
        apitokens_url = f"{ververica_url}/apitokens/v1/namespaces/{ververica_namespace}/apitokens"
        webtoken_name = f"namespaces/{ververica_namespace}/apitokens/ci-token"
        request_body = {
            "name": webtoken_name,
            "role": "editor"
        }
        response = requests.post(apitokens_url, json.dumps(request_body), headers={
            "accept": "application / json",
            "Content-Type": "application/json"
        })
        print(response)
        if response.status_code == 200:
            webtoken_secret = json.loads(response.json()["apiToken"]["secret"])
            return {
                "name": webtoken_name,
                "secret": webtoken_secret
            }
        else:
            return None
