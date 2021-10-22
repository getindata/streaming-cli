import click

from streamingcli.Config import PLATFORM_DEFAULT_DEPLOYMENT_TARGET_NAME
from streamingcli.platform.setup_command import PlatformSetupCommand
from streamingcli.platform.apitoken_create_command import VervericaApiTokenCreateCommand
from streamingcli.platform.apitoken_remove_command import VervericaApiTokenRemoveCommand
from streamingcli.profile.profile_command import ProfileCommand
from streamingcli.project.build_command import ProjectBuilder
from streamingcli.project.cicd_command import CICDInitializer
from streamingcli.project.deploy_command import ProjectDeployer
from streamingcli.project.init_command import NewProjectInitializer
from streamingcli.project.publish_command import ProjectPublisher


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
@click.argument('docker-image-tag')
@click.option('--profile',
              help='Profile name to use')
@click.option('--vvp-url', 'ververica_url',
              help='URL for Ververica cluster, i.e: "https://vvp.streaming-platform.example.com"')
@click.option('--vvp-namespace', 'ververica_namespace',
              help='Ververica namespace')
@click.option('--vvp-deployment-target', 'ververica_deployment_target_name',
              help='Ververica deployment target name')
@click.option('--token', 'ververica_webtoken_secret',
              help='Ververica WebToken secret to make API calls')
@click.option('--docker-registry-url', 'docker_registry_url',
              help='URL for Docker registry, i.e: "https://hub.docker.com/"')
@click.option('--overrides_from_yaml',
              help='Path to additional deployment YAML file to merge with Ververica one')
def project_deploy(docker_image_tag: str,
                   profile: str = None,
                   ververica_url: str = None,
                   ververica_namespace: str = None,
                   ververica_deployment_target_name: str = None,
                   ververica_webtoken_secret: str = None,
                   docker_registry_url: str = None,
                   overrides_from_yaml: str = None):
    ProjectDeployer.deploy_project(docker_image_tag=docker_image_tag,
                                   profile=profile,
                                   ververica_url=ververica_url,
                                   ververica_namespace=ververica_namespace,
                                   ververica_deployment_target_name=ververica_deployment_target_name,
                                   ververica_webtoken_secret=ververica_webtoken_secret,
                                   docker_registry_url=docker_registry_url,
                                   overrides_from_yaml=overrides_from_yaml)


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


@platform.group("api-token")
def api_token():
    pass


@api_token.command()
@click.option('--vvp-url', 'ververica_url', prompt='Ververica URL',
              help='URL for Ververica cluster, i.e: "https://vvp.streaming-platform.example.com"')
@click.option('--vvp-namespace', 'ververica_namespace', prompt='Ververica namespace',
              help='Ververica namespace')
@click.option('--name', 'apitoken_name', prompt='Ververica ApiToken name',
              help='Ververica ApiToken name')
@click.option('--role', 'apitoken_role', prompt='Ververica ApiToken role',
              help='Ververica ApiToken role')
def platform_apitoken_create(ververica_url: str,
                             ververica_namespace: str,
                             apitoken_name: str,
                             apitoken_role: str):
    VervericaApiTokenCreateCommand.create_apitoken(ververica_url=ververica_url,
                                                   ververica_namespace=ververica_namespace,
                                                   token_name=apitoken_name,
                                                   token_role=apitoken_role)


@api_token.command()
@click.option('--vvp-url', 'ververica_url', prompt='Ververica URL',
              help='URL for Ververica cluster, i.e: "https://vvp.streaming-platform.example.com"')
@click.option('--vvp-namespace', 'ververica_namespace', prompt='Ververica namespace',
              help='Ververica namespace')
@click.option('--name', 'apitoken_name', prompt='Ververica ApiToken name',
              help='Ververica ApiToken name')
def platform_apitoken_remove(ververica_url: str,
                             ververica_namespace: str,
                             apitoken_name: str):
    VervericaApiTokenRemoveCommand.remove_apitoken(ververica_url=ververica_url,
                                                   ververica_namespace=ververica_namespace,
                                                   token_name=apitoken_name)


@project.group()
def cicd():
    pass


@cicd.command()
@click.option('--provider', prompt="Provider's name",
              help="Provider's name", type=click.Choice(['gitlab'], case_sensitive=False))
def cicd_setup(provider: str):
    CICDInitializer.setup_cicd(provider)


@cli.group()
def profile():
    pass


@profile.command()
@click.argument('profile_name')
@click.option('--ververica-url', prompt='Ververica URL', required=False,
              help='URL for Ververica cluster, i.e: "https://vvp.streaming-platform.example.com"')
@click.option('--ververica-namespace', prompt='Ververica namespace', required=False,
              help='Ververica namespace')
@click.option('--ververica-deployment-target', prompt='Ververica deployment target name',
              required=False, help='Ververica deployment target name')
@click.option('--vvp-api-token', prompt='Ververica API Token',
              required=False, help='Ververica API Token')
@click.option('--docker-registry-url', prompt='Docker registry URL',
              required=False, help='URL for Docker registry, i.e: "https://hub.docker.com/"')
def add_profile(profile_name: str,
                ververica_url: str,
                ververica_namespace: str,
                ververica_deployment_target: str,
                vvp_api_token: str,
                docker_registry_url: str):
    ProfileCommand.create_profile(profile_name=profile_name,
                                  ververica_url=ververica_url,
                                  ververica_namespace=ververica_namespace,
                                  ververica_deployment_target=ververica_deployment_target,
                                  ververica_api_token=vvp_api_token,
                                  docker_registry_url=docker_registry_url
                                  )


project.add_command(project_init, "init")
project.add_command(project_deploy, "deploy")
project.add_command(project_build, "build")
project.add_command(project_publish, "publish")
platform.add_command(platform_setup, "setup")
api_token.add_command(platform_apitoken_create, "create")
api_token.add_command(platform_apitoken_remove, "remove")
cicd.add_command(cicd_setup, "setup")
profile.add_command(add_profile, "add")

if __name__ == '__main__':
    cli()
