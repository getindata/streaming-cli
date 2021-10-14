import click
from jinja2 import Environment

from streamingcli.platform.platform_config_map import PlatformConfigAdapter
from streamingcli.platform.ververica.deployment_adapter import DeploymentAdapter
from streamingcli.project.template_loader import TemplateLoader
from streamingcli.project.local_project_config import LocalProjectConfigIO
from streamingcli.project.yaml_merger import YamlMerger
from streamingcli.platform.ververica.webtoken_factory import VervericaWebTokenLoader
from typing import Optional


class ProjectDeployer:
    @staticmethod
    def deploy_project(overrides_from_yaml: Optional[str] = None):
        # Load local project config
        local_project_config = LocalProjectConfigIO.load_project_config()

        # Load platform ConfigMap
        kubernetes_namespace = "default"  # TODO load from config
        platform_config = PlatformConfigAdapter.load_platform_config(kubernetes_namespace=kubernetes_namespace)

        # TODO Load kubernetes ConfigMap

        # Load kubernetes secret
        webtoken = VervericaWebTokenLoader.load_webtoken(kubernetes_namespace=kubernetes_namespace)

        # Generate deployment YAML
        docker_registry_url = "registry.ververica.com/v2.5"  # TODO parametrize that
        docker_image_tag = f"{local_project_config.project_name}:{local_project_config.project_version}"
        deployment_yml = ProjectDeployer.generate_project_template(
            project_name=local_project_config.project_name,
            docker_registry_url=docker_registry_url,
            docker_image_tag=docker_image_tag)
        if overrides_from_yaml:
            deployment_yml = YamlMerger.merge_two_yaml(deployment_yml, overrides_from_yaml)

        click.echo(f"Deploying streaming project: {local_project_config.project_name} ...")
        # TODO Read url and namespace from config
        deployment_name = DeploymentAdapter.deploy(deployment_yml, ververica_url="http://localhost:8080", ververica_namespace="default")
        click.echo(f"Created deployment: http://localhost:8080/app/#/namespaces/default/deployments/{deployment_name}")

    @staticmethod
    def generate_project_template(project_name: str, docker_registry_url: str, docker_image_tag: str) -> str:
        template = TemplateLoader.load_project_template("flink_deployment.yml")
        return Environment().from_string(template).render(
            project_name=project_name,
            docker_registry_url=docker_registry_url,
            docker_image_tag=docker_image_tag
        )
