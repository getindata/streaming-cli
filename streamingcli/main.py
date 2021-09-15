import click


@click.group()
def cli():
    pass


@click.command()
def version():
    click.echo("Streaming CLI: V0.1.2")


@click.command()
@click.option('--project_name', prompt='Project name',
              help='Project name which will become Flink job name in Ververica platform')
def init(project_name: str):
    click.echo(f"Initializing streaming project: {project_name}")


cli.add_command(version)
cli.add_command(init)


if __name__ == '__main__':
    cli()
