import importlib.resources as pkg_resources
from streamingcli.project import templates


class TemplateLoader:
    @staticmethod
    def load_project_template(template_name: str) -> str:
        template = pkg_resources.read_text(templates, template_name)
        return template
