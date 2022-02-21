import importlib.resources as pkg_resources

from streamingcli.project import templates


class TemplateLoader:
    @staticmethod
    def load_project_template(template_name: str) -> str:
        template = pkg_resources.read_text(templates, template_name)
        return template

    @staticmethod
    def copy_binary(file_name: str, target_path: str) -> None:
        file_content = pkg_resources.read_binary(templates, file_name)
        with open(target_path, "wb") as target_file:
            target_file.write(file_content)
