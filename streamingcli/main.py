import click
from streamingcli.project.init_command import NewProjectInitializer
from streamingcli.platform.setup_command import PlatformSetupCommand


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option()
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()
    pass


@cli.command()
@click.option('--project_name', prompt='Project name',
              help='Project name which will become Flink job name in Ververica platform')
def init(project_name: str):
    click.echo(f"Initializing streaming project: {project_name}")
    NewProjectInitializer.createProject(project_name)
    click.echo(f"Project: {project_name} initialized")


@cli.command()
@click.option('--ververica_url', prompt='Ververica URL',
              help='URR for Ververica cluster, i.e: "https://vvp.streaming-platform.example.com"')
@click.option('--ververica_namespace', prompt='Ververica namespace',
              help='Ververica namespace')
@click.option('--ververica_kubernetes_namespace', prompt='Kubernetes namespace where Ververica is deployed',
              help='Kubernetes namespace where Ververica is deployed')
def platform_setup(ververica_url: str, ververica_namespace: str, ververica_kubernetes_namespace: str):
    PlatformSetupCommand.setup_ververica(ververica_url=ververica_url,
                                         ververica_namespace=ververica_namespace,
                                         ververica_kubernetes_namespace=ververica_kubernetes_namespace)


cli.add_command(init, "init")
cli.add_command(platform_setup, "platform_setup")

if __name__ == '__main__':
    cli()
