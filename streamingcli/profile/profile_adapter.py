import os
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, Optional, Type

from marshmallow import Schema
from marshmallow_dataclass import class_schema
from streamingcli.Config import DEFAULT_PROFILE_DIR, PROFILE_ENV_VARIABLE_NAME
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

class ProfileAdapter:

    @staticmethod
    def save_profile(scli_profile: ScliProfile):
        profiles = ProfileAdapter.load_profiles()
        profiles_dict = profiles.profiles
        profiles_dict[scli_profile.profile_name] = scli_profile
        content = safe_dump(asdict(replace(profiles, profiles = profiles_dict)))
        with open(DEFAULT_PROFILE_DIR, "w") as file:
            file.write(content)

    @staticmethod
    def get_profile(profile_name: str) -> Optional[ScliProfile]: 
        profiles_dict = ProfileAdapter.load_profiles().profiles
        return profiles_dict.get(profile_name)

    @staticmethod
    def get_or_create_temporary(profile: str) -> ScliProfile:
        profile_name = ProfileAdapter.get_profile_name(profile_name=profile)

        if profile_name is not None:
            profile = ProfileAdapter.get_profile(profile_name=profile)
            return profile if profile is not None else ScliProfile(profile_name="temporary")
        else:
            return ScliProfile(profile_name="temporary")

    @staticmethod
    def load_profiles() -> ScliProfiles:
        profiles_path = Path(DEFAULT_PROFILE_DIR)

        if (profiles_path.is_file() is False):
            return ScliProfiles(profiles={})
        
        with open(profiles_path, "r") as file:
            content = file.read()
            return ProfileAdapter.strict_load_yaml(content, ScliProfiles)

    @staticmethod
    def update_profile_data(profile_data, 
                            ververica_url:str=None, 
                            ververica_namespace:str=None, 
                            ververica_deployment_target_name:str=None,
                            ververica_webtoken_secret:str=None, 
                            docker_registry_url:str=None) -> ScliProfile: 
        params = {
            'ververica_url': ververica_url,
            'ververica_namespace': ververica_namespace,
            'ververica_deployment_target': ververica_deployment_target_name,
            'ververica_api_token': ververica_webtoken_secret,
            'docker_registry_url': docker_registry_url
        }

        non_empty_params = {
            key: value for (key, value) in params.items() if value is not None
        }

        profile_data = replace(profile_data, **non_empty_params)
        return profile_data

    @staticmethod
    def get_profile_name(profile_name: Optional[str]) -> Optional[str]:
        if profile_name is not None:
            return profile_name
        else:
            return os.getenv(PROFILE_ENV_VARIABLE_NAME)

    @staticmethod
    def strict_load_yaml(yaml: str, loaded_type: Type[Any]):
        schema = class_schema(loaded_type)
        return schema().load(load(yaml, Loader=SafeLoader))
