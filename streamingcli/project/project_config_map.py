from dataclasses import dataclass
from dataclasses_json import dataclass_json

from streamingcli.platform.k8s.config_map_adapter import KubernetesConfigmapAdapter
from streamingcli.project.local_project_config import LocalProjectConfig
from streamingcli.Config import PROJECT_K8S_CONFIGMAP_KEY


@dataclass_json
@dataclass
class ProjectConfigMap:
    project_name: str


class ProjectConfigMapFactory:
    @staticmethod
    def create_from_project_config(project_config: LocalProjectConfig) -> ProjectConfigMap:
        return ProjectConfigMap(project_name=project_config.project_name)

    @staticmethod
    def create_from_json(configmap_json: str) -> ProjectConfigMap:
        return ProjectConfigMap.from_json(configmap_json)


class ProjectConfigMapAdapter:

    @staticmethod
    def load_project_config_map(project_config: LocalProjectConfig):
        configmap_name = project_config.project_configmap_name
        kubernetes_namespace = "default"

        configmap_list = KubernetesConfigmapAdapter.load_k8s_configmap(configmap_name=configmap_name,
                                                                       namespace=kubernetes_namespace)
        if configmap_list is None:
            return ProjectConfigMapFactory.create_from_project_config(project_config)
        else:
            configmap_json = configmap_list.data[PROJECT_K8S_CONFIGMAP_KEY]
            return ProjectConfigMapFactory.create_from_json(configmap_json)

    @staticmethod
    def save_project_config_map(project_config: LocalProjectConfig, project_configmap: ProjectConfigMap):
        configmap_name = project_config.project_configmap_name
        kubernetes_namespace = "default"

        configmap_data = {
            PROJECT_K8S_CONFIGMAP_KEY: project_configmap.to_json(),
        }

        KubernetesConfigmapAdapter.save_k8s_configmap(configmap_name=configmap_name,
                                                      namespace=kubernetes_namespace,
                                                      configmap_data=configmap_data)
