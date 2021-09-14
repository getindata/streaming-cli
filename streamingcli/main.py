import typer

app = typer.Typer()


@app.command()
def version():
    typer.echo("Streaming CLI: V0.1.0")


if __name__ == "__main__":
    app()
