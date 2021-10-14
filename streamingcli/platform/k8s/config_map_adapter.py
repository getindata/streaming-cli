from typing import Dict, Optional

from streamingcli.platform.k8s.config_loader import KubernetesConfigLoader
from kubernetes.client.exceptions import ApiException


class KubernetesConfigmapAdapter:

    @staticmethod
    def load_k8s_configmap(configmap_name: str, namespace: str) -> Optional[Dict]:
        k8s_api_client = KubernetesConfigLoader.get_client()
        configmap = k8s_api_client.read_namespaced_config_map(name=configmap_name, namespace=namespace)
        if configmap is None:
            return None
        else:
            return configmap.data

    @staticmethod
    def save_k8s_configmap(configmap_name: str, namespace: str, configmap_data: Dict):
        k8s_api_client = KubernetesConfigLoader.get_client()

        configmap_manifest = {
            "kind": "ConfigMap",
            "apiVersion": "v1",
            "metadata": {
                "name": configmap_name,
                "labels": {
                    "streaming": "true",
                },
            },
            "data": configmap_data,
        }

        try:
            k8s_api_client.read_namespaced_config_map(name=configmap_name, namespace=namespace)
            k8s_api_client.patch_namespaced_config_map(name=configmap_name, namespace=namespace, body=configmap_manifest)
        except ApiException as e:
            if e.status == 404:
                k8s_api_client.create_namespaced_config_map(namespace=namespace, body=configmap_manifest)
            else:
                raise e

    @staticmethod
    def delete_k8s_configmap(configmap_name: str, namespace: str):
        k8s_api_client = KubernetesConfigLoader.get_client()
        k8s_api_client.delete_namespaced_config_map(name=configmap_name, namespace=namespace)
