from typing import Optional

from kubernetes import client, config

k8s_api_client: Optional[client.CoreV1Api] = None


class KubernetesConfigLoader:
    @staticmethod
    def get_client() -> client.CoreV1Api:
        global k8s_api_client
        if k8s_api_client is None:
            try:
                config.load_incluster_config()
            except config.ConfigException:
                try:
                    config.load_kube_config()
                except config.ConfigException:
                    raise Exception("Could not configure kubernetes python client")

            k8s_api_client = client.CoreV1Api()
        return k8s_api_client
