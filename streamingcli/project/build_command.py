import os

from streamingcli.jupyter.jar_handler import JarHandler
from streamingcli.project.local_project_config import LocalProjectConfigIO
import docker
import click
from streamingcli.Config import DEFAULT_NOTEBOOK_NAME, DEFAULT_FLINK_APP_NAME, ADDITIONAL_DEPENDENCIES_DIR
from streamingcli.project.project_type import ProjectType
from streamingcli.utils.notebook_converter import NotebookConverter, ConvertedNotebook


class ProjectBuilder:

    @staticmethod
    def build_project(tag_name: str):
        # Load local project config
        local_project_config = LocalProjectConfigIO.load_project_config()
        client = docker.from_env()

        if local_project_config.project_type == ProjectType.JUPYTER:
            ProjectBuilder.convert_jupyter_notebook(local_project_config)
        image_tag = f"{local_project_config.project_name}:{tag_name}"
        click.echo(f"Building Docker image {image_tag} ...")

        (image, _) = client.images.build(path=".", tag=image_tag)
        click.echo(f"Docker image {image.short_id} created with tags: {image.tags}")

        return image.tags[0]

    @staticmethod
    def convert_jupyter_notebook(local_project_config):
        notebook_dir = './src'
        notebooks = [os.path.join(notebook_dir, _) for _ in os.listdir(notebook_dir) if _.endswith(".ipynb")]
        if len(notebooks) > 1:
            raise click.ClickException(f"Too many notebooks in directory {notebook_dir}")
        notebook_path = notebooks[0] if len(notebooks) == 1 else f"{notebook_dir}/{DEFAULT_NOTEBOOK_NAME}"
        converted_notebook = ProjectBuilder.convert_notebook(notebook_path)
        ProjectBuilder.write_notebook(converted_notebook.content)
        if converted_notebook.jars:
            ProjectBuilder.get_jars(converted_notebook, local_project_config)

    @staticmethod
    def get_jars(converted_notebook, local_project_config):
        jar_handler = JarHandler(project_root_dir=os.getcwd())
        for jar in converted_notebook.jars:
            local_path = jar_handler.remote_copy(jar)
            image_path = f"{ADDITIONAL_DEPENDENCIES_DIR}/{os.path.basename(local_path)}"
            local_project_config.add_dependency(image_path)
        LocalProjectConfigIO.update_project_config(local_project_config)

    @staticmethod
    def convert_notebook(notebook_path: str = None) -> ConvertedNotebook:
        file_path = notebook_path if notebook_path is not None else f"./src/{DEFAULT_NOTEBOOK_NAME}"
        return NotebookConverter.convert_notebook(file_path)

    @staticmethod
    def write_notebook(notebook_content: str):
        with open(f"./src/{DEFAULT_FLINK_APP_NAME}", "w+") as script_file:
            script_file.write(notebook_content)
