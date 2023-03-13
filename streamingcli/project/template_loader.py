import importlib.resources as pkg_resources
from pathlib import Path
from typing import Optional

from streamingcli.project import templates


class TemplateLoader:
    @staticmethod
    def load_project_template(template_name: str) -> str:
        template = TemplateLoader.try_to_load_text_from_packages(
            template_name
        ) or TemplateLoader.try_to_load_text_from_path(template_name)
        if template is None:
            raise ValueError(f"Could not read file for name: {template_name}")
        return template

    @staticmethod
    def copy_binary(file_name: str, target_path: str) -> None:
        file_content = pkg_resources.read_binary(templates, file_name)
        with open(target_path, "wb") as target_file:
            target_file.write(file_content)

    @staticmethod
    def try_to_load_text_from_packages(name: str) -> Optional[str]:
        try:
            return pkg_resources.read_text(templates, name)
        except ValueError:
            return None

    @staticmethod
    def try_to_load_text_from_path(name: str) -> Optional[str]:
        try:
            return Path(name).absolute().read_text()
        except OSError:
            return None
