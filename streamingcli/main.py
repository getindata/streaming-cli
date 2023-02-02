import sys
from typing import Optional

import click
from markupsafe import re

from .docker.login_command import LoginCommand
from .error import StreamingCliError
from .platform.apitoken_create_command import VervericaApiTokenCreateCommand
from .platform.apitoken_remove_command import VervericaApiTokenRemoveCommand
from .platform.deployment_target_command import DeploymentTargetCommand
from .profile.profile_adapter import DeploymentMode
from .profile.profile_command import ProfileCommand
from .project.build_command import ProjectBuilder
from .project.cicd_command import CICDInitializer
from .project.deploy_command import ProjectDeployer
from .project.jupyter.jupyter_project_factory import JupyterProjectFactory
from .project.project_type import ProjectType
from .project.publish_command import ProjectPublisher
from .project.python.python_project_factory import PythonProjectFactory


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option()
def _cli(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()
    pass


def cli() -> None:
    try:
        _cli()
    except StreamingCliError as err:
        click.secho(err.message, file=sys.stderr, fg="red")
        sys.exit(1)


@_cli.group()
def project() -> None:
    pass


@project.command()
@click.option(
    "--project_name",
    prompt="Project name",
    help="Project name which will become Flink job name in Ververica platform",
)
@click.option(
    "--project_type",
    prompt="Project type",
    required=False,
    help="Project type",
    type=click.Choice(["python", "jupyter"]),
    default="python",
)
@click.option(
    "--template_url",
    prompt="Template URL",
    prompt_required=False,
    help="Project template url",
    required=False,
)
def project_init(
    project_name: str,
    project_type: Optional[str] = None,
    template_url: Optional[str] = None,
) -> None:
    click.echo(f"Initializing streaming project: {project_name}")
    if ProjectType(project_type) == ProjectType.PYTHON:
        PythonProjectFactory.create(project_name, template_url)
    elif ProjectType(project_type) == ProjectType.JUPYTER:
        JupyterProjectFactory.create(
            project_name=project_name, template_url=template_url
        )
    else:
        raise click.exceptions.ClickException(f"Unknown project type: {project_type}")
    click.echo(f"Project: {project_name} initialized")


@project.command()
@click.option("--docker-image-tag", help="Docker image tag", default="latest")
@click.option(
    "--docker-image-registry",
    "docker_image_registry",
    help='URL for Docker registry, i.e: "https://hub.docker.com/"',
)
@click.option(
    "--docker-image-repository",
    "docker_image_repository",
    help="Docker image repository",
)
@click.option("--profile", help="Profile name to use")
@click.option(
    "--deployment-mode",
    "deployment_mode",
    type=click.Choice([x.name for x in DeploymentMode], case_sensitive=False),
)
@click.option(
    "--vvp-url",
    "ververica_url",
    help='URL for Ververica cluster, i.e: "https://vvp.streaming-platform.example.com"',
)
@click.option("--vvp-namespace", "ververica_namespace", help="Ververica namespace")
@click.option(
    "--vvp-deployment-target",
    "ververica_deployment_target_name",
    help="Ververica deployment target name",
)
@click.option(
    "--vvp-api-token",
    "vvp_api_token",
    help="Ververica WebToken secret to make API calls",
)
@click.option("--k8s-namespace", "k8s_namespace", help="Target namespace")
@click.option(
    "--overrides-from-yaml",
    help="Path to additional deployment YAML file to merge with Ververica one",
)
def project_deploy(
    docker_image_tag: str,
    docker_image_registry: Optional[str] = None,
    docker_image_repository: Optional[str] = None,
    profile: Optional[str] = None,
    deployment_mode: Optional[str] = None,
    ververica_url: Optional[str] = None,
    ververica_namespace: Optional[str] = None,
    ververica_deployment_target_name: Optional[str] = None,
    vvp_api_token: Optional[str] = None,
    k8s_namespace: Optional[str] = None,
    overrides_from_yaml: Optional[str] = None,
) -> None:
    ProjectDeployer.deploy_project(
        docker_image_tag=docker_image_tag,
        docker_registry_url=docker_image_registry,
        docker_image_repository=docker_image_repository,
        profile=profile,
        deployment_mode=DeploymentMode.from_label(deployment_mode),
        ververica_url=ververica_url,
        ververica_namespace=ververica_namespace,
        ververica_deployment_target_name=ververica_deployment_target_name,
        ververica_webtoken_secret=vvp_api_token,
        k8s_namespace=k8s_namespace,
        overrides_from_yaml=overrides_from_yaml,
    )


@project.command()
@click.option("--docker-image-tag", help="Project image tag", default="latest")
def project_build(docker_image_tag: str) -> None:
    ProjectBuilder.build_project(docker_image_tag)


@project.command()
def project_convert() -> None:
    ProjectBuilder.convert_jupyter_notebook()


@project.command()
@click.option(
    "--registry-url",
    prompt="Docker registry URL",
    help='URL for Docker registry, i.e: "https://hub.docker.com/"',
)
@click.option("--docker-image-tag", help="Project image tag")
def project_publish(registry_url: str, docker_image_tag: Optional[str] = None) -> None:
    ProjectPublisher.publish(registry_url, docker_image_tag)


@_cli.group()
def platform() -> None:
    pass


@platform.group("api-token")
def api_token() -> None:
    pass


def validate_k8s_secret(ctx: click.Context, param: click.Parameter, value: str) -> str:
    if value is not None and re.match(r"^[\w\-\_]+\/[\w\-\_]+$", value) is None:
        raise click.BadParameter(message="K8s secret in incorrect format")
    else:
        return value


@api_token.command()
@click.option(
    "--vvp-url",
    "ververica_url",
    prompt="Ververica URL",
    help='URL for Ververica cluster, i.e: "https://vvp.streaming-platform.example.com"',
)
@click.option(
    "--vvp-namespace",
    "ververica_namespace",
    prompt="Ververica namespace",
    help="Ververica namespace",
)
@click.option(
    "--name",
    "apitoken_name",
    prompt="Ververica ApiToken name",
    help="Ververica ApiToken name",
)
@click.option(
    "--role",
    "apitoken_role",
    prompt="Ververica ApiToken role",
    help="Ververica ApiToken role",
)
@click.option(
    "--save-to-kubernetes-secret",
    "k8s_secret",
    callback=validate_k8s_secret,
    help="Save K8s secret in format 'namespace/secret_name' i.e. 'vvp/token",
)
def platform_apitoken_create(
    ververica_url: str,
    ververica_namespace: str,
    apitoken_name: str,
    apitoken_role: str,
    k8s_secret: Optional[str] = None,
) -> None:
    VervericaApiTokenCreateCommand.create_apitoken(
        ververica_url=ververica_url,
        ververica_namespace=ververica_namespace,
        token_name=apitoken_name,
        token_role=apitoken_role,
        k8s_secret=k8s_secret,
    )


@api_token.command()
@click.option(
    "--vvp-url",
    "ververica_url",
    prompt="Ververica URL",
    help='URL for Ververica cluster, i.e: "https://vvp.streaming-platform.example.com"',
)
@click.option(
    "--vvp-namespace",
    "ververica_namespace",
    prompt="Ververica namespace",
    help="Ververica namespace",
)
@click.option(
    "--name",
    "apitoken_name",
    prompt="Ververica ApiToken name",
    help="Ververica ApiToken name",
)
def platform_apitoken_remove(
    ververica_url: str, ververica_namespace: str, apitoken_name: str
) -> None:
    VervericaApiTokenRemoveCommand.remove_apitoken(
        ververica_url=ververica_url,
        ververica_namespace=ververica_namespace,
        token_name=apitoken_name,
    )


@platform.group()
def deployment_target() -> None:
    pass


@deployment_target.command()
@click.option(
    "--kubernetes-namespace",
    prompt="Kubernetes namespace name",
    help="Kubernetes namespace name",
    required=True,
)
@click.option("--profile", help="Profile name to use", required=True)
@click.option("--name", help="Ververica deployment target name")
@click.option(
    "--vvp-url",
    required=False,
    help='URL for Ververica cluster, i.e: "https://vvp.streaming-platform.example.com"',
)
@click.option("--vvp-namespace", required=False, help="Ververica namespace")
@click.option("--vvp-api-token", required=False, help="Ververica API Token")
@click.option(
    "--registry-url",
    prompt="Docker registry URL",
    help='URL for Docker registry, i.e: "https://hub.docker.com/"',
)
def deployment_target_create(
    kubernetes_namespace: str,
    profile: str,
    name: Optional[str] = None,
    vvp_url: Optional[str] = None,
    vvp_namespace: Optional[str] = None,
    vvp_api_token: Optional[str] = None,
    registry_url: Optional[str] = None,
) -> None:
    DeploymentTargetCommand.create_deployment_target(
        kubernetes_namespace=kubernetes_namespace,
        deployment_target_name=name,
        profile_name=profile,
        ververica_url=vvp_url,
        ververica_namespace=vvp_namespace,
        vvp_api_token=vvp_api_token,
        registry_url=registry_url,
    )


@project.group()
def cicd() -> None:
    pass


@cicd.command()
@click.option(
    "--provider",
    prompt="Provider's name",
    help="Provider's name",
    type=click.Choice(["gitlab"], case_sensitive=False),
)
def cicd_setup(provider: str) -> None:
    CICDInitializer.setup_cicd(provider)


@_cli.group()
def profile() -> None:
    pass


@profile.command()
@click.argument("profile_name")
@click.option(
    "--deployment-mode",
    "deployment_mode",
    type=click.Choice([x.name for x in DeploymentMode], case_sensitive=False),
    default="VVP",
)
@click.option(
    "--vvp-url",
    required=False,
    help='URL for Ververica cluster, i.e: "https://vvp.streaming-platform.example.com"',
)
@click.option("--vvp-namespace", required=False, help="Ververica namespace")
@click.option(
    "--vvp-deployment-target", required=False, help="Ververica deployment target name"
)
@click.option("--vvp-api-token", required=False, help="Ververica API Token")
@click.option(
    "--docker-registry-url",
    required=False,
    help='URL for Docker registry, i.e: "https://hub.docker.com/"',
)
@click.option("--k8s-namespace", "k8s_namespace", help="Target namespace")
def add_profile(
    profile_name: str,
    deployment_mode: str,
    vvp_url: Optional[str],
    vvp_namespace: Optional[str],
    vvp_deployment_target: Optional[str],
    vvp_api_token: Optional[str],
    docker_registry_url: Optional[str],
    k8s_namespace: Optional[str],
) -> None:
    ProfileCommand.create_profile(
        profile_name=profile_name,
        deployment_mode=deployment_mode,
        ververica_url=vvp_url,
        ververica_namespace=vvp_namespace,
        ververica_deployment_target=vvp_deployment_target,
        ververica_api_token=vvp_api_token,
        docker_registry_url=docker_registry_url,
        k8s_namespace=k8s_namespace,
    )


@_cli.group()
def docker() -> None:
    pass


@docker.command()
@click.option("--username", required=True, help="The registry username")
@click.option("--password", required=True, help="The plaintext password")
@click.option(
    "--docker-registry-url",
    required=True,
    help="URL to the registry. E.g. https://index.docker.io/v1/",
)
def docker_login(username: str, password: str, docker_registry_url: str) -> None:
    LoginCommand.docker_login(username, password, docker_registry_url)


project.add_command(project_init, "init")
project.add_command(project_deploy, "deploy")
project.add_command(project_convert, "convert")
project.add_command(project_build, "build")
project.add_command(project_publish, "publish")
api_token.add_command(platform_apitoken_create, "create")
api_token.add_command(platform_apitoken_remove, "remove")
deployment_target.add_command(deployment_target_create, "create")
cicd.add_command(cicd_setup, "setup")
profile.add_command(add_profile, "add")
docker.add_command(docker_login, "login")

if __name__ == "__main__":
    cli()
