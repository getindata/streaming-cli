import pathlib
import click
import copier
from streamingcli.Config import (
    TEMPLATE_PROJECT_REPOSITORIES,
    PYTHON_TEMPLATE_PROJECT,
    PROJECT_LOCAL_TEMPLATE_DIR_NAME
)
from streamingcli.project.local_project_config import LocalProjectConfigFactory, LocalProjectConfigIO
from streamingcli.project.project_type import ProjectType
from streamingcli.project.template_loader import TemplateLoader
from jinja2 import Environment


class PythonProjectFactory:
    @staticmethod
    def check_if_directory_exists(project_path: str) -> bool:
        return pathlib.Path(project_path).exists()

    @staticmethod
    def create(project_name: str):
        project_path = f"./{project_name}"

        if PythonProjectFactory.check_if_directory_exists(project_path=project_path):
            raise click.ClickException("Project directory already exists!")

        copier.copy(src_path=TEMPLATE_PROJECT_REPOSITORIES[PYTHON_TEMPLATE_PROJECT], dst_path=project_path)
        LocalProjectConfigFactory.generate_initial_project_config(project_name, ProjectType.PYTHON)
        LocalProjectConfigIO.create_template_directory(project_name=project_name)
        PythonProjectFactory.generate_dockerfile_template(project_name=project_name)
        TemplateLoader.copy_binary("flink-python-loader.jar",
                                   f"{project_path}/{PROJECT_LOCAL_TEMPLATE_DIR_NAME}/flink-python-loader.jar")

    @staticmethod
    def generate_dockerfile_template(project_name: str):
        template = TemplateLoader.load_project_template("Dockerfile")
        project_dockerfile = Environment().from_string(template).render(project_name=project_name)
        with open(f"./{project_name}/Dockerfile", "w") as docker_file:
            docker_file.write(project_dockerfile)
