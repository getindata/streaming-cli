from dataclasses import dataclass
from dataclasses_json import dataclass_json
from streamingcli.project.local_project_config import LocalProjectConfigIO
from streamingcli.Config import PROJECT_LOCAL_TEMPLATE_DIR_NAME
from streamingcli.platform.platform_config_map import PlatformConfigAdapter
import click
import os


@dataclass_json
@dataclass
class ProjectProfile:
    profile_name: str
    ververica_url: str
    ververica_namespace: str
    ververica_kubernetes_namespace: str
    secret_name: str
    ververica_deployment_target_name: str
    ververica_deployment_target_id: str
    docker_registry_url: str


class ConfigureProjectProfile:
    @staticmethod
    def create_profile(profile_name: str, ververica_kubernetes_namespace: str, docker_registry_url: str):
        click.echo(f"Loading platform configuration")
        # Check if we are in project directory
        LocalProjectConfigIO.load_project_config()

        platform_config = PlatformConfigAdapter.load_platform_config(kubernetes_namespace=ververica_kubernetes_namespace)

        project_profile = ProjectProfile(
            profile_name=profile_name,
            ververica_url=platform_config.ververica_url,
            ververica_namespace=platform_config.ververica_namespace,
            ververica_kubernetes_namespace=platform_config.ververica_kubernetes_namespace,
            secret_name=platform_config.secret_name,
            ververica_deployment_target_name=platform_config.ververica_deployment_target_name,
            ververica_deployment_target_id=platform_config.ververica_deployment_target_id,
            docker_registry_url=docker_registry_url
        )

        ConfigureProjectProfile.save_profile(project_profile=project_profile)
        click.echo(f"Project profile {profile_name} saved")

    @staticmethod
    def save_profile(project_profile: ProjectProfile):
        local_profiles_dir = f"{PROJECT_LOCAL_TEMPLATE_DIR_NAME}/profiles"
        os.makedirs(local_profiles_dir, exist_ok=True)

        content = project_profile.to_json()
        with open(f"./{local_profiles_dir}/{project_profile.profile_name}.json", "w") as file:
            file.write(content)

    @staticmethod
    def load_profile(profile_name: str) -> ProjectProfile:
        profile_path = f"{PROJECT_LOCAL_TEMPLATE_DIR_NAME}/profiles/{profile_name}.json"
        with open(profile_path, "r") as file:
            content = file.read()
            return ProjectProfile.from_json(content)
