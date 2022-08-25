import json
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, Optional

import click
import docker
from docker.client import DockerClient
from docker.errors import DockerException
from docker.models.images import Image

from streamingcli.project.local_project_config import LocalProjectConfigIO


@dataclass
class UserCredentials:
    username: str = field()
    password: str


class ProjectPublisher:
    @staticmethod
    def publish(
        docker_repository_url: str,
        docker_image_tag: Optional[str] = None,
        docker_credentials: Optional[UserCredentials] = None,
    ) -> None:
        local_project_config = LocalProjectConfigIO.load_project_config()

        client = docker.from_env()
        image_tag = docker_image_tag if docker_image_tag is not None else "latest"
        local_image_tag = f"{local_project_config.project_name}:{image_tag}"
        repository_name = f"{docker_repository_url}/{local_project_config.project_name}"

        if docker_credentials is not None:
            ProjectPublisher.authenticate(
                client, docker_credentials, docker_repository_url
            )

        image = ProjectPublisher.get_image(client, local_image_tag)
        if image is None:
            raise click.ClickException(
                f"No project image {local_image_tag} in local registry! "
                "Firstly build image with command 'scli project build'"
            )

        image.tag(repository_name, image_tag, force=True)
        push_gen = client.images.push(
            repository_name, image_tag, stream=True, decode=True
        )
        ProjectPublisher.show_progressbar(push_gen, local_image_tag)

    @staticmethod
    def get_image(client: DockerClient, image_tag: str) -> Optional[Image]:
        try:
            image = client.images.get(image_tag)
            return image
        except DockerException:
            return None

    @staticmethod
    def authenticate(
        client: DockerClient, credentials: UserCredentials, docker_registry_url: str
    ) -> None:
        client.login(
            credentials.username, credentials.password, registry=docker_registry_url
        )
        click.echo(f"Successfully logged in to {docker_registry_url}")

    @staticmethod
    def show_progressbar(data: Generator[Any, Any, Any], image_tag: str) -> None:
        with click.progressbar(
            label=f"Publishing docker image {image_tag}", length=100
        ) as bar:
            total = 0
            pushed = 0
            items: Dict[str, int] = {}
            for item in (json.loads(json.dumps(item)) for item in data):
                status = item.get("status")
                id = item.get("id")
                progress_detail = item.get("progressDetail")
                if item.get("errorDetail") is not None:
                    raise click.ClickException(
                        f"Failed to push to docker registry: {item.get('error')}"
                    )
                if item.get("aux") is not None:
                    bar.update(100)
                    pass
                elif status == "Pushing" and progress_detail is not None:
                    item_total = progress_detail.get("total")
                    item_current = progress_detail.get("current")
                    if (
                        item_total is None
                        or item_current is None
                        or item_current > item_total
                    ):
                        continue
                    elif id in items:
                        diff = item_current - items[id]
                        pushed += diff
                        items[id] = item_current
                    else:
                        items[id] = item_current
                        total += item_total
                        pushed += item_current
                    update_val = pushed / total * 100
                    bar.update(update_val - bar.pos)
