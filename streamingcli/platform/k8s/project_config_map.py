from dataclasses import dataclass
from dataclasses_json import dataclass_json
from streamingcli.project.local_project_config import LocalProjectConfig


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
