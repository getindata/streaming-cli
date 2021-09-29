import click


class ProjectDeployer:
    @staticmethod
    def deploy_project():
        project_name = "dsds"  # TODO load config
        click.echo(f"Deploying streaming project: {project_name} ...")
        print("ok")