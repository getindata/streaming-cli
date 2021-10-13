import click
from jinja2 import Environment

from streamingcli.platform.platform_config_map import PlatformConfigAdapter
from streamingcli.project.template_loader import TemplateLoader
from streamingcli.project.local_project_config import LocalProjectConfigIO
from streamingcli.project.yaml_merger import YamlMerger
from typing import Optional


class ProjectDeployer:
    @staticmethod
    def deploy_project(overrides_from_yaml: Optional[str] = None):
        # Load local project config
        local_project_config = LocalProjectConfigIO.load_project_config()

        # Load platform ConfigMap
        PlatformConfigAdapter.load_platform_config(local_project_config.)

        # TODO Load kubernetes ConfigMap
        # TODO Load kubernetes secret

        # Generate deployment YAML
        docker_image_tag = f"{local_project_config.project_name}:{local_project_config.project_version}"
        deployment_yml = ProjectDeployer.generate_project_template(project_name=local_project_config.project_name, docker_image_tag=docker_image_tag)
        if overrides_from_yaml:
            deployment_yml = YamlMerger.merge_two_yaml(deployment_yml, overrides_from_yaml)
        print(deployment_yml)

        click.echo(f"Deploying streaming project: {local_project_config.project_name} ...")
        # TODO Post deployment YAML to Ververica cluster

    @staticmethod
    def generate_project_template(project_name: str, docker_image_tag: str) -> str:
        template = TemplateLoader.load_project_template("flink_deployment.yml")
        return Environment().from_string(template).render(project_name=project_name, docker_image_tag=docker_image_tag)
