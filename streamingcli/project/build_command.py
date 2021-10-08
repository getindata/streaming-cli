from streamingcli.project.local_project_config import LocalProjectConfigIO
import docker
import click


class ProjectBuilder:
    @staticmethod
    def build_project():
        # Load local project config
        local_project_config = LocalProjectConfigIO.load_project_config()

        image_tag = f"{local_project_config.project_name}:{local_project_config.project_version}"

        client = docker.from_env()
        (image, logs) = client.images.build(path=".", tag=image_tag)
        click.echo(f"Docker image {image.short_id} created with tags: {image.tags}")

        # TODO zapisać TAG w konfiguracji ?
        # TODO zapisać template deploymentu do katalogu projektu
        return image.tags[0]
