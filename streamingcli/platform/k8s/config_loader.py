from kubernetes import config, dynamic
from kubernetes.client import api_client


client = None


class KubernetesConfigLoader:
    @staticmethod
    def get_client():
        global client
        if client is None:
            client = dynamic.DynamicClient(
                api_client.ApiClient(configuration=config.load_kube_config())
            )
        return client

