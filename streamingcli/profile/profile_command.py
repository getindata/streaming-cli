from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, Optional, Type

import click
from marshmallow import Schema
from marshmallow_dataclass import class_schema
from streamingcli.Config import DEFAULT_PROFILE_DIR
from yaml import SafeLoader, load, safe_dump


@dataclass(repr=True)
class ScliProfile:
    profile_name: str
    ververica_url: Optional[str] = field(default=None)
    ververica_namespace: Optional[str] = field(default=None)
    ververica_deployment_target: Optional[str] = field(default=None)
    ververica_api_token: Optional[str] = field(default=None)
    docker_registry_url: Optional[str] = field(default=None)

@dataclass
class ScliProfiles:    
    profiles: Dict[str, ScliProfile] = field(default_factory=dict)


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
        ProfileCommand.save_profile(scli_profile=scli_profile)
        click.echo(f"Scli profile {profile_name} saved")

    @staticmethod
    def save_profile(scli_profile: ScliProfile):
        profiles = ProfileCommand.load_profiles()
        profiles_dict = profiles.profiles
        profiles_dict[scli_profile.profile_name] = scli_profile
        content = safe_dump(asdict(replace(profiles, profiles = profiles_dict)))
        with open(DEFAULT_PROFILE_DIR, "w") as file:
            file.write(content)

    @staticmethod
    def get_profile(profile_name: str) -> Optional[ScliProfile]: 
        profiles_dict = ProfileCommand.load_profiles().profiles
        return profiles_dict.get(profile_name)

    @staticmethod
    def load_profiles() -> ScliProfiles:
        profiles_path = Path(DEFAULT_PROFILE_DIR)

        if (profiles_path.is_file() is False):
            return ScliProfiles(profiles={})
        
        with open(profiles_path, "r") as file:
            content = file.read()
            return ProfileCommand.strict_load_yaml(content, ScliProfiles)

    @staticmethod
    def strict_load_yaml(yaml: str, loaded_type: Type[Any]):
        schema = class_schema(loaded_type)
        return schema().load(load(yaml, Loader=SafeLoader))
