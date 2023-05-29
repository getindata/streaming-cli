import sys
from typing import Optional

import click

from .docker.login_command import LoginCommand
from .error import StreamingCliError
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
@click.option("--env", help="Environment name to use")
@click.option(
    "--file-descriptor-path",
    "file_descriptor_path",
    help="Optional custom deployment descriptor file path",
)
@click.option(
    "--vvp-api-token",
    "vvp_api_token",
    help="Ververica WebToken secret to make API calls",
)
def project_deploy(
    docker_image_tag: str,
    env: Optional[str] = None,
    file_descriptor_path: Optional[str] = None,
    vvp_api_token: Optional[str] = None,
) -> None:
    ProjectDeployer.deploy_project(
        docker_image_tag=docker_image_tag,
        env=env,
        ververica_webtoken_secret=vvp_api_token,
        file_descriptor_path=file_descriptor_path,
    )


@project.command()
@click.option("--docker-image-tag", help="Project image tag", default="latest")
def project_build(docker_image_tag: str) -> None:
    ProjectBuilder.build_project(docker_image_tag)


@project.command()
def project_convert() -> None:
    ProjectBuilder.convert_jupyter_notebook()


@project.command()
@click.option("--env", help="Environment name to use")
@click.option("--docker-image-tag", help="Project image tag")
def project_publish(
    env: Optional[str] = None, docker_image_tag: Optional[str] = None
) -> None:
    ProjectPublisher.publish(env, docker_image_tag)


@_cli.group()
def docker() -> None:
    pass


@docker.command()
@click.option("--username", required=True, help="The registry username")
@click.option("--password", required=True, help="The plaintext password")
@click.option("--env", help="Environment name to use")
def docker_login(username: str, password: str, env: Optional[str] = None) -> None:
    LoginCommand.docker_login(username, password, env)


project.add_command(project_init, "init")
project.add_command(project_deploy, "deploy")
project.add_command(project_convert, "convert")
project.add_command(project_build, "build")
project.add_command(project_publish, "publish")
docker.add_command(docker_login, "login")

if __name__ == "__main__":
    cli()
