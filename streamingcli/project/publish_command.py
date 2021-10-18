import json
from math import floor
from typing import Generator, Optional

import click
import docker
from docker.client import DockerClient
from docker.errors import DockerException, ImageNotFound
from docker.models.images import Image
from streamingcli.project.local_project_config import LocalProjectConfigIO


class ProjectPublisher:

    @staticmethod
    def publish(docker_repository_url: str):
        local_project_config = LocalProjectConfigIO.load_project_config()

        client = docker.from_env()
        local_image_tag = f"{local_project_config.project_name}:{local_project_config.project_version}"
        repository_name = f"{docker_repository_url}/{local_project_config.project_name}"
        image_tag = local_project_config.project_version
        image = ProjectPublisher.get_image(client, local_image_tag)
        if image is None:
            raise click.ClickException(
                "No project image in local registry! "
                "Firstly build image with command 'scli project build'"
            )

        image.tag(repository_name, image_tag, force = True)
        push_gen = client.images.push(repository_name, image_tag,
                                stream = True, decode= True)
        ProjectPublisher.show_progressbar(push_gen, local_image_tag)

    @staticmethod
    def get_image(client: DockerClient, image_tag: str) -> Optional[Image]:
        try:
            image = client.images.get(image_tag)
            return image
        except DockerException as e:
            return None
    
    @staticmethod
    def show_progressbar(data: Generator, image_tag: str):
        with click.progressbar(label=f"Publishing docker image {image_tag}",
                                length=100) as bar:
            total = 0
            pushed = 0
            items = {}
            for item in map(lambda item: json.loads(json.dumps(item)), data):
                status = item.get('status')
                id = item.get('id')
                progress_detail = item.get('progressDetail')
                if(item.get('aux') != None):
                    bar.update(100)
                    pass
                elif(status == 'Pushing' and progress_detail != None):
                    item_total = progress_detail.get('total')
                    item_current = progress_detail.get('current')
                    if(item_current > item_total):
                        continue  
                    elif id in items:
                        diff = (item_current - items[id])
                        pushed += diff
                        items[id] = item_current 
                    else:
                        items[id] = item_current
                        total += item_total
                        pushed += item_current
                    update_val = pushed / total * 100
                    bar.update(update_val - bar.pos)
