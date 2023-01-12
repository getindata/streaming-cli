from kubernetes import utils
import yaml

from streamingcli.platform.k8s.config_loader import KubernetesConfigLoader


class K8SDeploymentAdapter:

    @staticmethod
    def deploy(
        deployment_yml: str,
        namespace: str
    ) -> None:
        k8s_client = KubernetesConfigLoader.get_client()
        utils.create_from_dict(k8s_client, yaml.load(deployment_yml), namespace=namespace)

