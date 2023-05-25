import copy
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

import click
import yaml
from marshmallow_dataclass import class_schema
from yaml import SafeLoader, load

from streamingcli.config import (
    DEFAULT_PROFILE,
    DEFAULT_PROFILE_PATH,
    PROFILE_CONFIG_FILE,
    PROFILE_ENV_VARIABLE_NAME,
)
from streamingcli.project.yaml_merger import YamlMerger


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
class ProfileConf:
    deployment_mode: Optional[DeploymentMode] = field(default=DeploymentMode.VVP)
    docker_registry_url: Optional[str] = field(default=None)


@dataclass(repr=True)
class ScliProfile:
    profile_name: str
    deployment_mode: Optional[DeploymentMode] = field(default=DeploymentMode.VVP)
    docker_registry_url: Optional[str] = field(default=None)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScliProfiles:
    profiles: Dict[str, ScliProfile] = field(default_factory=dict)


class ProfileAdapter:
    @staticmethod
    def get_profile(profile_name: str) -> ScliProfile:
        profiles_dict = ProfileAdapter.load_profiles().profiles
        profile = profiles_dict.get(profile_name)
        if profile is None:
            raise click.ClickException(f"Invalid environment name: {profile_name}")
        return profile

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

        profiles = [x.name for x in profiles_path.iterdir() if x.is_dir()]

        profile_list = {}
        for profile_name in profiles:
            profile = ProfileAdapter.load_profile(default_profile_path, profile_name)
            profile_list[profile_name] = profile
        return ScliProfiles(profiles=profile_list)

    @staticmethod
    def update_token(
        profile_data: ScliProfile, ververica_webtoken_secret: Optional[str] = None
    ) -> ScliProfile:
        profile = copy.deepcopy(profile_data)
        if ververica_webtoken_secret:
            if profile.config["vvp"] is None:
                profile.config["vvp"] = {}
            profile.config["vvp"]["api_token"] = ververica_webtoken_secret  # type: ignore

        return profile

    @staticmethod
    def get_profile_name(profile_name: Optional[str]) -> Optional[str]:
        if profile_name is not None:
            return profile_name
        else:
            return os.getenv(PROFILE_ENV_VARIABLE_NAME)

    @staticmethod
    def load_from_file(file_path: str) -> str:
        with open(file_path, "r") as file:
            return file.read()

    @staticmethod
    def merge_files(base_path: Path, profile_path: Path, file: str) -> str:
        base_file = f"{base_path}/{file}"
        profile_file = f"{profile_path}/{file}"
        if os.path.isfile(base_file) and os.path.isfile(profile_file):
            return YamlMerger.merge_two_yaml(base_file, profile_file)
        if os.path.isfile(profile_file):
            return ProfileAdapter.load_from_file(profile_file)
        return ProfileAdapter.load_from_file(base_file)

    @staticmethod
    def load_profile(profiles_path: str, profile_name: str) -> ScliProfile:
        profile_path = Path(profiles_path, profile_name)
        base_path = Path(profiles_path, DEFAULT_PROFILE)

        profile_str = ProfileAdapter.merge_files(
            base_path, profile_path, PROFILE_CONFIG_FILE
        )
        profile_schema = class_schema(ProfileConf)
        profile_conf = profile_schema().load(load(profile_str, Loader=SafeLoader))

        all_files = list(
            set(
                [
                    x.name
                    for x in profile_path.iterdir()
                    if x.name != PROFILE_CONFIG_FILE
                ]
                + [x.name for x in base_path.iterdir() if x.name != PROFILE_CONFIG_FILE]
            )
        )
        configuration = {}
        for file in all_files:
            merged = ProfileAdapter.merge_files(base_path, profile_path, file)
            conf = yaml.load(merged, Loader=yaml.Loader)
            configuration.update(conf)

        return ScliProfile(
            profile_name=profile_name,
            deployment_mode=profile_conf.deployment_mode,
            docker_registry_url=profile_conf.docker_registry_url,
            config=configuration,
        )
