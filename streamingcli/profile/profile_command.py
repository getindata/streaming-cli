import click
from streamingcli.profile.profile_adapter import ProfileAdapter, ScliProfile


class ProfileCommand:

    @staticmethod
    def create_profile(profile_name: str,
                        ververica_url: str=None,
                        ververica_namespace: str=None,
                        ververica_deployment_target: str=None,
                        ververica_api_token: str=None,
                        docker_registry_url: str=None):
        scli_profile = ScliProfile(
            profile_name=profile_name,
            ververica_url=ververica_url,
            ververica_namespace=ververica_namespace,
            ververica_deployment_target=ververica_deployment_target,
            docker_registry_url=docker_registry_url,
            ververica_api_token=ververica_api_token
        )
        ProfileAdapter.save_profile(scli_profile=scli_profile)
        click.echo(f"Scli profile {profile_name} saved")
