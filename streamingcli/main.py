import click

from streamingcli.Config import PLATFORM_DEFAULT_DEPLOYMENT_TARGET_NAME
from streamingcli.platform.setup_command import PlatformSetupCommand
from streamingcli.project.build_command import ProjectBuilder
from streamingcli.project.cicd_command import CICDInitializer
from streamingcli.project.deploy_command import ProjectDeployer
from streamingcli.project.init_command import NewProjectInitializer
from streamingcli.project.publish_command import ProjectPublisher
from streamingcli.project.configure_command import ConfigureProjectProfile


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option()
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()
    pass


@cli.group()
def project():
    pass


@project.command()
@click.option('--project_name', prompt='Project name',
              help='Project name which will become Flink job name in Ververica platform')
def project_init(project_name: str):
    click.echo(f"Initializing streaming project: {project_name}")
    NewProjectInitializer.createProject(project_name)
    click.echo(f"Project: {project_name} initialized")


@project.command()
@click.option('--profile_name', prompt='Project profile name to create',
              help='Project profile name to create')
@click.option('--ververica_kubernetes_namespace', prompt='Kubernetes namespace where Ververica is deployed',
              help='Kubernetes namespace where Ververica is deployed')
@click.option('--docker_registry_url', prompt='Docker registry URL',
              help='URL for Docker registry, i.e: "https://hub.docker.com/"')
def project_config(profile_name: str, ververica_kubernetes_namespace: str, docker_registry_url: str):
    ConfigureProjectProfile.create_profile(profile_name=profile_name,
                                           ververica_kubernetes_namespace=ververica_kubernetes_namespace,
                                           docker_registry_url=docker_registry_url)


@project.command()
@click.option('--overrides_from_yaml',
              help='Path to additional deployment YAML file to merge with Ververica one')
def project_deploy(overrides_from_yaml: str = None):
    ProjectDeployer.deploy_project(overrides_from_yaml)


@project.command()
def project_build():
    ProjectBuilder.build_project()

@project.command()
@click.option('--registry_url', prompt='Docker registry URL',
                help='URL for Docker registry, i.e: "https://hub.docker.com/"')
def project_publish(registry_url: str):
    ProjectPublisher.publish(registry_url)

@cli.group()
def platform():
    pass


@platform.command()
@click.option('--ververica_url', prompt='Ververica URL',
              help='URL for Ververica cluster, i.e: "https://vvp.streaming-platform.example.com"')
@click.option('--ververica_namespace', prompt='Ververica namespace',
              help='Ververica namespace')
@click.option('--ververica_deployment_target', prompt='Ververica deployment target name',
              help='Ververica deployment target name')
@click.option('--ververica_kubernetes_namespace', prompt='Kubernetes namespace where Ververica is deployed',
              help='Kubernetes namespace where Ververica is deployed')
@click.option('--force', help='Force recreate tokens and secrets', is_flag=True)
def platform_setup(ververica_url: str,
                   ververica_namespace: str,
                   ververica_kubernetes_namespace: str,
                   force: bool,
                   ververica_deployment_target: str = PLATFORM_DEFAULT_DEPLOYMENT_TARGET_NAME):
    PlatformSetupCommand.setup_ververica(ververica_url=ververica_url,
                                         ververica_namespace=ververica_namespace,
                                         ververica_kubernetes_namespace=ververica_kubernetes_namespace,
                                         ververica_deployment_target_name=ververica_deployment_target,
                                         force=force)


@project.group()
def cicd():
    pass

@cicd.command()
@click.option('--provider', prompt="Provider's name",
            help="Provider's name", type=click.Choice(['gitlab'], case_sensitive=False))
def cicd_setup(provider: str):
    CICDInitializer.setup_cicd(provider)


project.add_command(project_init, "init")
project.add_command(project_deploy, "deploy")
project.add_command(project_build, "build")
project.add_command(project_publish, "publish")
project.add_command(project_config, "config")
platform.add_command(platform_setup, "setup")
cicd.add_command(cicd_setup, "setup")

if __name__ == '__main__':
    cli()
