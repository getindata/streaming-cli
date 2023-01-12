from abc import ABC, abstractmethod
from jinja2 import Environment
from typing import Optional, List

from streamingcli.platform.ververica.deployment_adapter import VervericaDeploymentAdapter

from streamingcli.platform.k8s.deployment_adapter import K8SDeploymentAdapter
from streamingcli.project.template_loader import TemplateLoader

from streamingcli.profile.profile_adapter import ScliProfile, DeploymentMode


class DeploymentAdapter(ABC):

    def __init__(self, profile_data: ScliProfile, docker_image_tag: str, project_name: str):
        self.profile_data = profile_data
        self.docker_image_tag = docker_image_tag
        self.project_name = project_name

    @abstractmethod
    def deploy(self, deployment_yml: Optional[str]) -> Optional[str]:
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
        return (
            Environment()
            .from_string(template)
            .render(params)
        )


class DeploymentAdapterFactory:
    @staticmethod
    def get_adapter(deployment_mode: DeploymentMode, **kwargs):
        if deployment_mode == DeploymentMode.K8S_OPERATOR:
            return K8SDeploymentAdapter(**kwargs)
        if deployment_mode == DeploymentMode.VVP:
            return VervericaDeploymentAdapter(**kwargs)
