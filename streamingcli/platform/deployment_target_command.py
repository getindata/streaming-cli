import click
from streamingcli.platform.ververica.deployment_target_factory import \
    VervericaDeploymentTargetFactory
from streamingcli.profile.profile_adapter import ProfileAdapter, ScliProfile


class DeploymentTargetCommand:

    def create_deployment_target(deployment_target_name: str=None,
                            profile: str=None,
                            ververica_url: str=None,
                            ververica_namespace: str=None,
                            vvp_api_token: str=None):
        profile = ProfileAdapter.get_or_create_temporary(profile)

        profile = ProfileAdapter.update_profile_data(
            profile_data=profile,
            ververica_url=ververica_url,
            ververica_namespace=ververica_namespace,
            ververica_deployment_target_name=deployment_target_name,
            ververica_webtoken_secret=vvp_api_token
        )
        DeploymentTargetCommand.validate_scli_profile(profile)
        deployment_target_id = VervericaDeploymentTargetFactory.create_deployment_target(
            ververica_url=profile.ververica_url,
            ververica_namespace=profile.ververica_namespace,
            ververica_kubernetes_namespace=profile.ververica_namespace,
            ververica_webtoken_secret=profile.ververica_api_token,
            ververica_deployment_target_name=profile.ververica_deployment_target
        )

        click.echo(f"Created deployment target {profile.ververica_deployment_target} with id {deployment_target_id}")
        
    @staticmethod
    def validate_scli_profile(profile_data: ScliProfile):
        if profile_data.ververica_url is None:
            raise click.ClickException("Missing Ververica URL attribute")
        if profile_data.ververica_namespace is None:
            raise click.ClickException("Missing Ververica Namespace attribute")
        if profile_data.ververica_deployment_target is None:
            raise click.ClickException("Missing Ververica Deployment Target Name attribute")
        if profile_data.ververica_api_token is None:
            raise click.ClickException("Missing Ververica APIToken secret attribute")
