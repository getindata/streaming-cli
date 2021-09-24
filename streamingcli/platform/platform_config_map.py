from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from streamingcli.platform.k8s.config_map_adapter import KubernetesConfigmapAdapter
from streamingcli.Config import (
    PLATFORM_K8S_CONFIGMAP_NAME,
    PLATFORM_K8S_CONFIGMAP_KEY,
    PLATFORM_K8S_SECRET_NAME
)
import click


@dataclass_json
@dataclass
class PlatformConfig:
    ververica_url: str
    ververica_namespace: str = field(default="default")
    ververica_kubernetes_namespace: str = field(default="vvp")
    secret_name: str = field(default=PLATFORM_K8S_SECRET_NAME)


class PlatformConfigFactory:
    @staticmethod
    def create_from_json(configmap_json: str) -> PlatformConfig:
        return PlatformConfig.from_json(configmap_json)

    @staticmethod
    def to_json(config: PlatformConfig) -> str:
        return config.to_json()


class PlatformConfigAdapter:

    @staticmethod
    def load_platform_config(kubernetes_namespace: str) -> PlatformConfig:
        configmap_name = PLATFORM_K8S_CONFIGMAP_NAME

        configmap_list = KubernetesConfigmapAdapter.load_k8s_configmap(configmap_name=configmap_name,
                                                                       namespace=kubernetes_namespace)
        if configmap_list is None:
            raise click.ClickException("Platform config load failed")
        else:
            configmap_json = configmap_list.data[PLATFORM_K8S_CONFIGMAP_KEY]
            return PlatformConfigFactory.create_from_json(configmap_json)

    @staticmethod
    def save_platform_config(platform_config: PlatformConfig):
        configmap_data = {
            PLATFORM_K8S_CONFIGMAP_KEY: PlatformConfigFactory.to_json(platform_config),
        }

        KubernetesConfigmapAdapter.save_k8s_configmap(configmap_name=PLATFORM_K8S_CONFIGMAP_NAME,
                                                      namespace=platform_config.ververica_kubernetes_namespace,
                                                      configmap_data=configmap_data)
