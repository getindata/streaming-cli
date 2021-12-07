from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Type

import click
from marshmallow_dataclass import class_schema
from streamingcli.Config import PROJECT_LOCAL_CONFIG_FILE_NAME
from streamingcli.project.project_type import ProjectType
from yaml import SafeLoader, load, safe_dump


@dataclass(repr=True)
class LocalProjectConfig:
    project_name: str
    project_version: str
    project_type: ProjectType = field(metadata={"by_value": True})
    dependencies: list = field(default_factory=lambda: [])

    def add_dependency(self, dependency_path):
        self.dependencies.append(dependency_path)
        self.dependencies = list(dict.fromkeys(self.dependencies))


def custom_asdict_factory(data):
    def convert_value(obj):
        if isinstance(obj, Enum):
            return obj.value
        return obj

    return dict((k, convert_value(v)) for k, v in data)


class LocalProjectConfigFactory:
    @staticmethod
    def from_yaml_object(config_yaml) -> LocalProjectConfig:
        project_name = config_yaml["project_name"]
        project_version = config_yaml["project_version"]
        project_type = config_yaml["project_type"]

        return LocalProjectConfig(project_name=project_name,
                                  project_version=project_version,
                                  project_type=project_type)


class LocalProjectConfigIO:

    @staticmethod
    def project_config_default_path():
        return f"./{PROJECT_LOCAL_CONFIG_FILE_NAME}"

    @staticmethod
    def save_project_config(config: LocalProjectConfig):
        config_yaml = safe_dump(asdict(config, dict_factory=custom_asdict_factory))
        with open(f"./{config.project_name}/{PROJECT_LOCAL_CONFIG_FILE_NAME}", "w") as config_file:
            config_file.write(config_yaml)

    @staticmethod
    def update_project_config(config: LocalProjectConfig):
        config_yaml = safe_dump(asdict(config, dict_factory=custom_asdict_factory))
        with open(f"./{PROJECT_LOCAL_CONFIG_FILE_NAME}", "w") as config_file:
            config_file.seek(0)
            config_file.write(config_yaml)
            config_file.truncate()

    @staticmethod
    def load_project_config() -> LocalProjectConfig:
        config_file_path = LocalProjectConfigIO.project_config_default_path()
        try:
            with open(config_file_path, "r+") as config_file:
                content = config_file.read()
                return LocalProjectConfigIO.strict_load_yaml(content, LocalProjectConfig)
        except Exception:
            raise click.ClickException("Current directory is not streaming project. Initialize project first")

    @staticmethod
    def strict_load_yaml(yaml: str, loaded_type: Type[Any]):
        schema = class_schema(loaded_type)
        return schema().load(load(yaml, Loader=SafeLoader))
