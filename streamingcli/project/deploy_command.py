import click
from jinja2 import Environment
from streamingcli.project.template_loader import TemplateLoader
from streamingcli.project.local_project_config import LocalProjectConfigIO


class ProjectDeployer:
    @staticmethod
    def deploy_project():
        # Load local project config
        local_project_config = LocalProjectConfigIO.load_project_config()

        # TODO Load kubernetes ConfigMap
        # TODO Load kubernetes secret
        # TODO Upload project artifact/code into Min.io... or make dockerfile with python code
        # TODO Generate deployment YAML
        deployment_yml = ProjectDeployer.generate_project_template(project_name=local_project_config.project_name)
        print(deployment_yml)

        # TODO Post deployment YAML to Ververica cluster
        click.echo(f"Deploying streaming project: {local_project_config.project_name} ...")
        print("ok")

    @staticmethod
    def generate_project_template(project_name: str) -> str:
        template = TemplateLoader.load_project_template("flink_deployment.yml")
        return Environment().from_string(template).render(project_name=project_name)
