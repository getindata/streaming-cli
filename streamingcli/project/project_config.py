import yaml
from streamingcli.Config import PROJECT_CONFIG_FILE_NAME
from typing import Dict, Optional
import click


class ProjectConfig:
    def __init__(self, project_name: str, project_configmap_name: Optional[str] = None):
        self.project_name = project_name
        self.project_configmap_name = project_configmap_name

    def __repr__(self):
        return f"(project_name={self.project_name},project_configmap_name={self.project_configmap_name})"

    def to_yaml_object(self) -> Dict[str, str]:
        return {
            "project_name": self.project_name,
            "project_configmap_name": self.project_configmap_name
        }

    def to_yaml_string(self) -> str:
        return yaml.dump(self.to_yaml_object())


class ProjectConfigFactory:
    @staticmethod
    def generate_initial_project_config(project_name: str):
        configmap_name = ProjectConfigFactory.format_project_configmap_name(project_name)
        config = ProjectConfig(project_name=project_name, project_configmap_name=configmap_name)
        ProjectConfigIO.save_project_config(config)

    @staticmethod
    def format_project_configmap_name(project_name: str):
        formatted_project_name = project_name.replace("_", "-")
        return f"{formatted_project_name}-configmap"

    @staticmethod
    def from_yaml_object(config_yaml) -> ProjectConfig:
        project_name = config_yaml["project_name"]
        project_configmap_name = config_yaml["project_configmap_name"]

        return ProjectConfig(project_name=project_name, project_configmap_name=project_configmap_name)


class ProjectConfigIO:
    @staticmethod
    def project_config_default_path():
        return f"./{PROJECT_CONFIG_FILE_NAME}"

    @staticmethod
    def save_project_config(config: ProjectConfig):
        config_yaml = yaml.dump(config.to_yaml_object())
        with open(f"./{config.project_name}/{PROJECT_CONFIG_FILE_NAME}", "w") as config_file:
            config_file.write(config_yaml)

    @staticmethod
    def load_project_config() -> ProjectConfig:
        config_file_path = ProjectConfigIO.project_config_default_path()
        try:
            with open(config_file_path, "r+") as config_file:
                file_content = config_file.readlines()
                config_yaml = yaml.load(file_content)
                return ProjectConfigFactory.from_yaml_object(config_yaml)
        except:
            raise click.ClickException("Current directory is not streaming project. Initialize project first")


