import os
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional, Type

import click
from marshmallow_dataclass import class_schema
from streamingcli.Config import (PROJECT_LOCAL_CONFIG_FILE_NAME,
                                 PROJECT_LOCAL_TEMPLATE_DIR_NAME)
from streamingcli.project.project_type import ProjectType
from yaml import SafeLoader, load, safe_dump


@dataclass(repr=True)
class LocalProjectConfig:
    project_name: str
    project_version: str
    project_type: ProjectType = field(metadata={"by_value": True})
    project_configmap_name: Optional[str] = field(default=None)
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
    DEFAULT_PROJECT_VERSION = "v1.0"

    @staticmethod
    def generate_initial_project_config(project_name: str, project_type: ProjectType):
        configmap_name = LocalProjectConfigFactory.format_project_configmap_name(project_name)
        config = LocalProjectConfig(project_name=project_name,
                                    project_version=LocalProjectConfigFactory.DEFAULT_PROJECT_VERSION,
                                    project_type=project_type,
                                    project_configmap_name=configmap_name)
        LocalProjectConfigIO.save_project_config(config)

    @staticmethod
    def format_project_configmap_name(project_name: str):
        formatted_project_name = project_name.replace("_", "-")
        return f"{formatted_project_name}-configmap"

    @staticmethod
    def from_yaml_object(config_yaml) -> LocalProjectConfig:
        project_name = config_yaml["project_name"]
        project_version = config_yaml["project_version"]
        project_configmap_name = config_yaml["project_configmap_name"]

        return LocalProjectConfig(project_name=project_name, project_version=project_version,
                                  project_configmap_name=project_configmap_name)


class LocalProjectConfigIO:
    @staticmethod
    def create_template_directory(project_name: str):
        os.makedirs(f"{project_name}/{PROJECT_LOCAL_TEMPLATE_DIR_NAME}")

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
