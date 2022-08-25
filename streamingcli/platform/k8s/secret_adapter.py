from base64 import b64decode, b64encode
from typing import Any, Dict, Optional

from kubernetes.client import V1ObjectMeta, V1Secret
from kubernetes.client.exceptions import ApiException

from streamingcli.platform.k8s.config_loader import KubernetesConfigLoader


class KubernetesSecretAdapter:
    @staticmethod
    def load_k8s_secret(secret_name: str, namespace: str) -> Optional[Dict[Any, Any]]:
        k8s_api_client = KubernetesConfigLoader.get_client()
        try:
            secret = k8s_api_client.read_namespaced_secret(
                name=secret_name, namespace=namespace
            )

            deserialized_secret_data = {}

            for k in secret.data.keys():
                deserialized_secret_data[k] = b64decode(secret.data[k]).decode("UTF-8")

            return deserialized_secret_data
        except ApiException as e:
            if e.status == 404:
                return None
            else:
                raise e

    @staticmethod
    def save_k8s_secret(
        secret_name: str, namespace: str, secret_data: Dict[Any, Any]
    ) -> None:
        k8s_api_client = KubernetesConfigLoader.get_client()

        serialized_secret_data = {}

        for k in secret_data.keys():
            serialized_secret_data[k] = b64encode(
                secret_data[k].encode("UTF-8")
            ).decode("UTF-8")

        secret_body = V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=V1ObjectMeta(
                namespace=namespace,
                name=secret_name,
                labels={
                    "streaming": "true",
                },
            ),
            type="Opaque",
            data=serialized_secret_data,
        )

        try:
            k8s_api_client.read_namespaced_secret(name=secret_name, namespace=namespace)
            k8s_api_client.patch_namespaced_secret(
                name=secret_name, namespace=namespace, body=secret_body
            )
        except ApiException as e:
            if e.status == 404:
                k8s_api_client.create_namespaced_secret(
                    namespace=namespace, body=secret_body
                )
            else:
                raise e

    @staticmethod
    def delete_k8s_configmap(configmap_name: str, namespace: str) -> None:
        k8s_api_client = KubernetesConfigLoader.get_client()
        try:
            k8s_api_client.delete_namespaced_config_map(
                name=configmap_name, namespace=namespace
            )
        except ApiException as e:
            if e.status != 404:
                raise e
