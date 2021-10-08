import click
from jinja2 import Environment
from streamingcli.project.template_loader import TemplateLoader
from streamingcli.project.local_project_config import LocalProjectConfigIO

class ProjectDeployer:
    @staticmethod
    def deploy_project(overrides_from_yaml: str = None):
        # Load local project config
        local_project_config = LocalProjectConfigIO.load_project_config()

        # TODO Load kubernetes ConfigMap
        # TODO Load kubernetes secret
        # TODO Generate deployment YAML
        docker_image_tag = f"{local_project_config.project_name}:{local_project_config.project_version}"
        deployment_yml = ProjectDeployer.generate_project_template(project_name=local_project_config.project_name, docker_image_tag=docker_image_tag)
        print(deployment_yml)

        # TODO Post deployment YAML to Ververica cluster
        click.echo(f"Deploying streaming project: {local_project_config.project_name} ...")
        print("ok")

    @staticmethod
    def generate_project_template(project_name: str, docker_image_tag: str) -> str:
        template = TemplateLoader.load_project_template("flink_deployment.yml")
        return Environment().from_string(template).render(project_name=project_name, docker_image_tag=docker_image_tag)
