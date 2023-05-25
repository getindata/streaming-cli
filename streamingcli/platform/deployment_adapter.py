from abc import ABC, abstractmethod
from typing import List, Optional

from jinja2 import Environment

from streamingcli.config import PROJECT_DEPLOYMENT_TEMPLATE
from streamingcli.platform.jinja_prettifier import yaml_pretty
from streamingcli.profile.profile_adapter import ScliProfile
from streamingcli.project.template_loader import TemplateLoader


class DeploymentAdapter(ABC):
    def __init__(
        self, profile_data: ScliProfile, docker_image_tag: str, project_name: str
    ):
        self.profile_data = profile_data
        self.docker_image_tag = docker_image_tag
        self.project_name = project_name

        self.validate_profile_data()

    @abstractmethod
    def deploy(self, deployment_yml: str) -> Optional[str]:
        pass

    @abstractmethod
    def validate_profile_data(self) -> None:
        pass

    def generate_project_template(
        self, dependencies: List[str], file_descriptor_path: Optional[str] = None
    ) -> str:
        descriptor_path = file_descriptor_path or PROJECT_DEPLOYMENT_TEMPLATE
        template = TemplateLoader.load_project_template(descriptor_path)

        params = self.profile_data.__dict__.copy()
        params["project_name"] = self.project_name
        params["docker_image_tag"] = self.docker_image_tag
        params["dependencies"] = dependencies
        env = Environment()
        env.filters["pretty"] = yaml_pretty
        return env.from_string(template).render(params)
