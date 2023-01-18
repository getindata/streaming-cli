from abc import ABC, abstractmethod
from typing import List, Optional

from jinja2 import Environment

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

    @staticmethod
    @abstractmethod
    def get_template_name() -> str:
        pass

    def generate_project_template(self, dependencies: List[str]) -> str:
        template = TemplateLoader.load_project_template(self.get_template_name())
        params = self.profile_data.__dict__.copy()
        params["project_name"] = self.project_name
        params["docker_image_tag"] = self.docker_image_tag
        params["dependencies"] = dependencies
        return Environment().from_string(template).render(params)
