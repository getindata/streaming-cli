from typing import Dict

from kubernetes import config, dynamic
from kubernetes.client import api_client
from streamingcli.project.local_project_config import LocalProjectConfig
from streamingcli.project.project_config_map import ProjectConfigMap, ProjectConfigMapFactory
from streamingcli.platform.k8s.config_loader import KubernetesConfigLoader
from kubernetes.client.exceptions import ApiException


# https://github.com/kubernetes-client/python/blob/master/examples/dynamic-client/configmap.py
class KubernetesConfigmapAdapter:

    @staticmethod
    def load_k8s_configmap(configmap_name: str, namespace: str):
        client = KubernetesConfigLoader.get_client()
        api = client.resources.get(api_version="v1", kind="ConfigMap")

        try:
            return api.get(
                name=configmap_name, namespace=namespace, label_selector="streaming=true"
            )
        except ApiException as err:
            if err.status == 404:
                return None
            else:
                raise err

    @staticmethod
    def save_k8s_configmap(configmap_name: str, namespace: str, configmap_data: Dict):
        client = KubernetesConfigLoader.get_client()
        api = client.resources.get(api_version="v1", kind="ConfigMap")

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

        current_configmap = KubernetesConfigmapAdapter.load_k8s_configmap(configmap_name, namespace)
        if current_configmap is None:
            configmap = api.create(body=configmap_manifest, namespace=namespace)
        else:
            configmap_patched = api.patch(
                name=configmap_name, namespace=namespace, body=configmap_manifest
            )

    @staticmethod
    def delete_k8s_configmap(configmap_name: str, namespace: str):
        client = KubernetesConfigLoader.get_client()
        api = client.resources.get(api_version="v1", kind="ConfigMap")
        api.delete(name=configmap_name, body={}, namespace=namespace)
