import yaml
from streamingcli.Config import PROJECT_LOCAL_CONFIG_FILE_NAME, PROJECT_LOCAL_TEMPLATE_DIR_NAME
from typing import Dict, Optional
import click
import os


class LocalProjectConfig:
    def __init__(self, project_name: str, project_version: str, project_configmap_name: Optional[str] = None):
        self.project_name = project_name
        self.project_version = project_version
        self.project_configmap_name = project_configmap_name

    def __repr__(self):
        return f"(project_name={self.project_name},project_version={self.project_version},project_configmap_name={self.project_configmap_name})"

    def to_yaml_object(self) -> Dict[str, str]:
        return {
            "project_name": self.project_name,
            "project_version": self.project_version,
            "project_configmap_name": self.project_configmap_name
        }

    def to_yaml_string(self) -> str:
        return yaml.dump(self.to_yaml_object())


class LocalProjectConfigFactory:
    DEFAULT_PROJECT_VERSION = "v1.0"

    @staticmethod
    def generate_initial_project_config(project_name: str):
        configmap_name = LocalProjectConfigFactory.format_project_configmap_name(project_name)
        config = LocalProjectConfig(project_name=project_name, project_version=LocalProjectConfigFactory.DEFAULT_PROJECT_VERSION, project_configmap_name=configmap_name)
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

        return LocalProjectConfig(project_name=project_name, project_version=project_version, project_configmap_name=project_configmap_name)


class LocalProjectConfigIO:
    @staticmethod
    def create_template_directory(project_name: str):
        os.makedirs(f"{project_name}/{PROJECT_LOCAL_TEMPLATE_DIR_NAME}")

    @staticmethod
    def project_config_default_path():
        return f"./{PROJECT_LOCAL_CONFIG_FILE_NAME}"

    @staticmethod
    def save_project_config(config: LocalProjectConfig):
        config_yaml = yaml.dump(config.to_yaml_object())
        with open(f"./{config.project_name}/{PROJECT_LOCAL_CONFIG_FILE_NAME}", "w") as config_file:
            config_file.write(config_yaml)

    @staticmethod
    def load_project_config() -> LocalProjectConfig:
        config_file_path = LocalProjectConfigIO.project_config_default_path()
        try:
            with open(config_file_path, "r+") as config_file:
                file_content = "".join(config_file.readlines())
                config_yaml = yaml.load(stream=file_content, Loader=yaml.FullLoader)
                return LocalProjectConfigFactory.from_yaml_object(config_yaml)
        except Exception as e:
            print(e)
            raise click.ClickException("Current directory is not streaming project. Initialize project first")


