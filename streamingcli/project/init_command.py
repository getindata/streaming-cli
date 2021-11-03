from streamingcli.Config import TEMPLATE_PROJECT_REPOSITORIES, PYTHON_TEMPLATE_PROJECT, PROJECT_LOCAL_TEMPLATE_DIR_NAME
from streamingcli.project.local_project_config import LocalProjectConfigFactory, LocalProjectConfigIO
import click
import git
import pathlib
from jinja2 import Environment

from streamingcli.project.project_type import ProjectType
from streamingcli.project.template_loader import TemplateLoader
import os


class NewProjectInitializer:
    @staticmethod
    def check_if_directory_exists(project_name: str) -> bool:
        return pathlib.Path(f"./{project_name}").exists()

    @staticmethod
    def createProject(project_name: str, project_type: ProjectType):
        if NewProjectInitializer.check_if_directory_exists(project_name=project_name):
            raise click.ClickException("Project directory already exists!")

        with click.progressbar(length=100,
                               label='Generating project structure') as bar:
            class CloneProgress(git.RemoteProgress):
                def update(self, op_code, cur_count, max_count=None, message=''):
                    bar.update(current_item=cur_count, n_steps=int(cur_count))

            git.Repo.clone_from(ProjectType.to_template_repository(project_type), f"./{project_name}",
                                progress=CloneProgress())

        LocalProjectConfigFactory.generate_initial_project_config(project_name)
        LocalProjectConfigIO.create_template_directory(project_name=project_name)
        NewProjectInitializer.generate_dockerfile_template(project_name=project_name)
        TemplateLoader.copy_binary("flink-python-loader.jar",
                                   f"./{project_name}/{PROJECT_LOCAL_TEMPLATE_DIR_NAME}/flink-python-loader.jar")

    @staticmethod
    def generate_dockerfile_template(project_name: str):
        template = TemplateLoader.load_project_template("Dockerfile")
        project_dockerfile = Environment().from_string(template).render(project_name=project_name)
        with open(f"./{project_name}/Dockerfile", "w") as docker_file:
            docker_file.write(project_dockerfile)
