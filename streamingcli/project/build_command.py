from streamingcli.project.local_project_config import LocalProjectConfigIO
import docker
import click


class ProjectBuilder:
    @staticmethod
    def build_project(tag_name:str = None):
        # Load local project config
        local_project_config = LocalProjectConfigIO.load_project_config()

        image_tag = f"{local_project_config.project_name}:{tag_name if tag_name is not None else 'latest'}"
        click.echo(f"Building Docker image {image_tag} ...")

        client = docker.from_env()
        (image, logs) = client.images.build(path=".", tag=image_tag)
        click.echo(f"Docker image {image.short_id} created with tags: {image.tags}")

        return image.tags[0]
