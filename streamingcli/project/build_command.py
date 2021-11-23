import os
from streamingcli.project.local_project_config import LocalProjectConfigIO
import docker
import click
from streamingcli.Config import DEFAULT_NOTEBOOK_NAME, DEFAULT_FLINK_APP_NAME
from streamingcli.project.project_type import ProjectType
from streamingcli.utils.notebook_converter import NotebookConverter


class ProjectBuilder:

    @staticmethod
    def build_project(tag_name: str):
        # Load local project config
        local_project_config = LocalProjectConfigIO.load_project_config()
        client = docker.from_env()

        if local_project_config.project_type == ProjectType.JUPYTER:
            notebook_dir = './src'
            notebooks = [os.path.join(notebook_dir, _) for _ in os.listdir(notebook_dir) if _.endswith(".ipynb")]
            if len(notebooks) > 1:
                raise click.ClickException(f"Too many notebooks in directory {notebook_dir}")
            notebook_path = notebooks[0] if len(notebooks) == 1 else f"{notebook_dir}/{DEFAULT_NOTEBOOK_NAME}"
            ProjectBuilder.convert_notebook(notebook_path)

        image_tag = f"{local_project_config.project_name}:{tag_name}"
        click.echo(f"Building Docker image {image_tag} ...")

        (image, _) = client.images.build(path=".", tag=image_tag)
        click.echo(f"Docker image {image.short_id} created with tags: {image.tags}")

        return image.tags[0]

    @staticmethod
    def convert_notebook(notebook_path: str = None):
        file_path = notebook_path if notebook_path != None else f"./src/{DEFAULT_NOTEBOOK_NAME}"
        flink_app_script = NotebookConverter.convert_notebook(file_path)
        with open(f"./src/{DEFAULT_FLINK_APP_NAME}", "w+") as script_file:
            script_file.write(flink_app_script)
