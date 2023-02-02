import os
from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Type

import click
from marshmallow_dataclass import class_schema
from yaml import SafeLoader, load, safe_dump

from streamingcli.config import (
    DEFAULT_PROFILE_DIR,
    DEFAULT_PROFILE_PATH,
    PROFILE_ENV_VARIABLE_NAME,
)


class DeploymentMode(Enum):
    VVP = "VVP"
    K8S_OPERATOR = "K8S_OPERATOR"

    @staticmethod
    def from_label(label: Optional[str]) -> Optional["DeploymentMode"]:
        return DeploymentMode(label.upper()) if label else None


def custom_asdict_factory(data: Any) -> Dict[str, Any]:
    def convert_value(obj: Any) -> Any:
        if isinstance(obj, Enum):
            return obj.value
        return obj

    return {k: convert_value(v) for k, v in data}


@dataclass(repr=True)
class ScliProfile:
    profile_name: str
    deployment_mode: Optional[DeploymentMode] = field(default=DeploymentMode.VVP)
    ververica_url: Optional[str] = field(default=None)
    ververica_namespace: Optional[str] = field(default=None)
    ververica_deployment_target: Optional[str] = field(default=None)
    ververica_api_token: Optional[str] = field(default=None)
    docker_registry_url: Optional[str] = field(default=None)
    k8s_namespace: Optional[str] = field(default=None)


@dataclass
class ScliProfiles:
    profiles: Dict[str, ScliProfile] = field(default_factory=dict)


class ProfileAdapter:
    @staticmethod
    def save_profile(scli_profile: ScliProfile) -> None:
        os.makedirs(DEFAULT_PROFILE_DIR, exist_ok=True)
        profiles = ProfileAdapter.load_profiles()
        profiles_dict = profiles.profiles
        profiles_dict[scli_profile.profile_name] = scli_profile
        content = safe_dump(
            asdict(
                replace(profiles, profiles=profiles_dict),
                dict_factory=custom_asdict_factory,
            )
        )
        with open(DEFAULT_PROFILE_PATH, "w+") as file:
            file.write(content)

    @staticmethod
    def get_profile(profile_name: str) -> Optional[ScliProfile]:
        profiles_dict = ProfileAdapter.load_profiles().profiles
        return profiles_dict.get(profile_name)

    @staticmethod
    def get_or_create_temporary(ordered_profile_name: str) -> ScliProfile:
        profile_name = ProfileAdapter.get_profile_name(
            profile_name=ordered_profile_name
        )

        if profile_name is not None:
            profile = ProfileAdapter.get_profile(profile_name=profile_name)
            return (
                profile
                if profile is not None
                else ScliProfile(profile_name="temporary")
            )
        else:
            raise click.ClickException(
                f"Profile data not accessible for profile name: {ordered_profile_name}. Create profile first"
            )

    @staticmethod
    def load_profiles(default_profile_path: str = DEFAULT_PROFILE_PATH) -> ScliProfiles:
        profiles_path = Path(default_profile_path)

        if profiles_path.is_file() is False:
            return ScliProfiles(profiles={})

        with open(profiles_path, "r") as file:
            content = file.read()
            return ProfileAdapter.strict_load_yaml(content, ScliProfiles)

    @staticmethod
    def update_profile_data(
        profile_data: ScliProfile,
        deployment_mode: Optional[DeploymentMode] = None,
        ververica_url: Optional[str] = None,
        ververica_namespace: Optional[str] = None,
        ververica_deployment_target_name: Optional[str] = None,
        ververica_webtoken_secret: Optional[str] = None,
        docker_registry_url: Optional[str] = None,
        k8s_namespace: Optional[str] = None,
    ) -> ScliProfile:
        params = {}  # type: Dict[str, Any]
        if deployment_mode is not None:
            params["deployment_mode"] = deployment_mode
        if ververica_url is not None:
            params["ververica_url"] = ververica_url
        if ververica_namespace is not None:
            params["ververica_namespace"] = ververica_namespace
        if ververica_deployment_target_name is not None:
            params["ververica_deployment_target"] = ververica_deployment_target_name
        if ververica_webtoken_secret is not None:
            params["ververica_api_token"] = ververica_webtoken_secret
        if docker_registry_url is not None:
            params["docker_registry_url"] = docker_registry_url
        if k8s_namespace is not None:
            params["k8s_namespace"] = k8s_namespace

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
    def strict_load_yaml(yaml: str, loaded_type: Type[Any]) -> ScliProfiles:
        schema = class_schema(loaded_type)
        return schema().load(load(yaml, Loader=SafeLoader))
