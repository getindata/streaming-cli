import yaml
from streamingcli.Config import PROJECT_CONFIG_FILE_NAME
from typing import Dict


class ProjectConfig:
    def __init__(self, project_name: str):
        self.project_name = project_name

    def __repr__(self):
        return f"(project_name={self.project_name})"

    def to_yaml_object(self) -> Dict[str, str]:
        return {
            "project_name": self.project_name
        }


class ProjectConfigGenerator:
    @staticmethod
    def generate_initial_project_config(project_name: str):
        config = ProjectConfig(project_name=project_name)
        ProjectConfigIO.save_project_config(config)


class ProjectConfigIO:
    @staticmethod
    def save_project_config(config: ProjectConfig):
        config_yaml = yaml.dump(config.to_yaml_object())
        with open(f"./{config.project_name}/{PROJECT_CONFIG_FILE_NAME}", "w") as text_file:
            text_file.write(config_yaml)
