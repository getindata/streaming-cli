import pathlib
import click
import copier
from streamingcli.project.local_project_config import LocalProjectConfigFactory
from streamingcli.project.project_type import ProjectType


PYTHON_TEMPLATE_PROJECT = "git@gitlab.com:getindata/streaming-labs/flink-sandbox-python.git"


class PythonProjectFactory:
    @staticmethod
    def check_if_directory_exists(project_path: str) -> bool:
        return pathlib.Path(project_path).exists()

    @staticmethod
    def create(project_name: str):
        project_path = f"./{project_name}"

        if PythonProjectFactory.check_if_directory_exists(project_path=project_path):
            raise click.ClickException("Project directory already exists!")

        copier.copy(src_path=PYTHON_TEMPLATE_PROJECT, dst_path=project_path)
        LocalProjectConfigFactory.generate_initial_project_config(project_name, ProjectType.PYTHON)
