from typing import Optional

from kubernetes import client, config


k8s_api_client: Optional[client.CoreV1Api] = None


class KubernetesConfigLoader:
    @staticmethod
    def get_client() -> client.CoreV1Api:
        global k8s_api_client
        if k8s_api_client is None:
            config.load_kube_config()
            k8s_api_client = client.CoreV1Api()
        return k8s_api_client

