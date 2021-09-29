import click

from streamingcli.project.local_project_config import LocalProjectConfigIO


class ProjectDeployer:
    @staticmethod
    def deploy_project():
        # Load local project config
        local_project_config = LocalProjectConfigIO.load_project_config()

        # TODO Load kubernetes ConfigMap
        # TODO Load kubernetes secret
        # TODO Upload project artifact/code into Min.io
        # TODO Generate deployment YAML
        # TODO Post deployment YAML to Ververica cluster
        click.echo(f"Deploying streaming project: {local_project_config.project_name} ...")
        print("ok")