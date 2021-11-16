import click
import docker
from docker import auth
from docker.utils import config
import json
import base64


class LoginCommand:

    @staticmethod
    def docker_login(username: str, password: str, docker_registry_url: str):
        client = docker.from_env()
        client.login(username, password, registry=docker_registry_url, reauth=True)
        click.echo(f"Successfully logged in to {docker_registry_url}")
        # it's a bit of a hack, docker-py login method does not update auth credentials in Docker config file
        LoginCommand.update_docker_auths_config(username, password, docker_registry_url)

    @staticmethod
    def update_docker_auths_config(username: str, password: str, docker_registry_url: str):
        config_file = config.find_config_file()
        with open(config_file, "r+") as f:
            config_dict = json.loads(f.read())
            auths = config_dict.get('auths', {})
            auth_entry = LoginCommand.build_auth_entry(username, password, docker_registry_url)
            auths.update(auth_entry)
            config_dict.update({'auths': auths})
            f.seek(0)
            f.write(json.dumps(config_dict, indent=4))
            f.truncate()

    @staticmethod
    def build_auth_entry(username: str, password: str, docker_registry_url: str):
        registry_index = auth.resolve_index_name(docker_registry_url)
        user_pwd = f'{username}:{password}'.encode('ascii')
        return {
            registry_index: {
                'auth': base64.b64encode(user_pwd).decode("utf-8")
            }
        }
