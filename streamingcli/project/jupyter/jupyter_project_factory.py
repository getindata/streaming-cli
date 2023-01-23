import pathlib
from typing import Optional

import click
import copier

JUPYTER_TEMPLATE_PROJECT = (
    "https://github.com/getindata/streaming-cli-jupyter-template.git"
)


class JupyterProjectFactory:
    @staticmethod
    def check_if_directory_exists(project_path: str) -> bool:
        return pathlib.Path(project_path).exists()

    @staticmethod
    def create(project_name: str, template_url: Optional[str]) -> None:
        project_path = f"./{project_name}"

        if JupyterProjectFactory.check_if_directory_exists(project_path=project_path):
            raise click.ClickException("Project directory already exists!")

        template_data = {"project_name": project_name}

        copier.copy(
            src_path=(template_url or JUPYTER_TEMPLATE_PROJECT),
            dst_path=project_path,
            data=template_data,
        )
