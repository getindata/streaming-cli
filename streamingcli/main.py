import click


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


cli.add_command(init)


if __name__ == '__main__':
    cli()
