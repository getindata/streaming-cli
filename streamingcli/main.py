import sys
from typing import Optional

import click
from markupsafe import re

from .docker.login_command import LoginCommand
from .error import StreamingCliError
from .profile.profile_adapter import DeploymentMode
from .project.build_command import ProjectBuilder
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
    "--vvp-deployment-template-path",
    "ververica_deployment_template_path",
    help="Optional custom Ververica deployment descriptor file absolute path",
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
docker.add_command(docker_login, "login")

if __name__ == "__main__":
    cli()
