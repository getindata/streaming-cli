import copy
import os
from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Type

import click
from marshmallow_dataclass import class_schema
from yaml import SafeLoader, load, safe_dump

from streamingcli.config import (
    DEFAULT_PROFILE_PATH,
    PROFILE_ENV_VARIABLE_NAME, PROJECT_DEPLOYMENT_TEMPLATE, VVP_CONFIG_FILE, DOCKER_CONFIG_FILE, RESOURCES_CONFIG_FILE,
    K8S_CONFIG_FILE, FLINK_CONFIG_FILE, PROFILE_CONFIG_FILE,
)
from streamingcli.profile.config_merger import ConfigMerger


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
class VervericaConf:
    url: Optional[str] = field(default=None)
    namespace: Optional[str] = field(default=None)
    deployment_target: Optional[str] = field(default=None)
    api_token: Optional[str] = field(default=None)


@dataclass(repr=True)
class K8SConf:
    namespace: Optional[str] = field(default=None)
    spec: Optional[str] = field(default=None)


@dataclass(repr=True)
class ProfileConf:
    name: str
    deployment_mode: Optional[DeploymentMode] = field(default=DeploymentMode.VVP)
    docker_registry_url: Optional[str] = field(default=None)


@dataclass(repr=True)
class ScliProfile:
    profile_name: str
    deployment_mode: Optional[DeploymentMode] = field(default=DeploymentMode.VVP)
    docker_registry_url: Optional[str] = field(default=None)
    ververica_conf: Optional[VervericaConf] = field(default=None)
    k8s_conf: Optional[K8SConf] = field(default=None)
    flink_conf: Optional[str] = field(default=None)
    resources_conf: Optional[str] = field(default=None)


@dataclass
class ScliProfiles:
    profiles: Dict[str, ScliProfile] = field(default_factory=dict)


class ProfileAdapter:

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

        profiles = [x.name for x in profiles_path.iterdir() if x.is_dir()]
        base = None
        if 'base' in profiles:
            base = ProfileAdapter.load_profile('base')

        profile_list = {'base': base}
        for profile_name in profiles:
            if profile_name != 'base':
                profile = ProfileAdapter.load_profile(profile_name)
                profile_list[profile_name] = ConfigMerger.merge_profiles(base, profile)
        return ScliProfiles(profiles=profile_list)

    @staticmethod
    def enrich_profile_data(
        profile_data: ScliProfile,
        deployment_mode: Optional[DeploymentMode] = None,
        ververica_url: Optional[str] = None,
        ververica_namespace: Optional[str] = None,
        ververica_deployment_target_name: Optional[str] = None,
        ververica_webtoken_secret: Optional[str] = None,
        docker_registry_url: Optional[str] = None,
        k8s_namespace: Optional[str] = None,
    ) -> ScliProfile:
        profile = copy.deepcopy(profile_data)
        if deployment_mode is not None:
            profile.deployment_mode = deployment_mode
        if ververica_url is not None:
            profile.ververica_conf.url = ververica_url
        if ververica_namespace is not None:
            profile.ververica_conf.namespace = ververica_namespace
        if ververica_deployment_target_name is not None:
            profile.ververica_conf.deployment_target = ververica_deployment_target_name
        if ververica_webtoken_secret is not None:
            profile.ververica_conf.api_token = ververica_webtoken_secret
        if docker_registry_url is not None:
            profile.docker_registry_url = docker_registry_url
        if k8s_namespace is not None:
            profile.k8s_conf.namespace = k8s_namespace

        return profile

    @staticmethod
    def get_profile_name(profile_name: Optional[str]) -> Optional[str]:
        if profile_name is not None:
            return profile_name
        else:
            return os.getenv(PROFILE_ENV_VARIABLE_NAME)

    @staticmethod
    def load_if_exists(profile_name: str, file: str, loaded_type: Type[Any]) -> Optional[Any]:
        file_path = f"{DEFAULT_PROFILE_PATH}/{profile_name}/{file}"
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                content = file.read()
                schema = class_schema(loaded_type)
                return schema().load(load(content, Loader=SafeLoader))
        return None

    @staticmethod
    def load_profile(profile_name: str) -> ScliProfile:
        profile_conf = ProfileAdapter.load_if_exists(profile_name, PROFILE_CONFIG_FILE, ProfileConf)
        vvp_conf = ProfileAdapter.load_if_exists(profile_name, VVP_CONFIG_FILE, VervericaConf)
        resources_conf = ProfileAdapter.load_if_exists(profile_name, RESOURCES_CONFIG_FILE, str)
        k8s_conf = ProfileAdapter.load_if_exists(profile_name, K8S_CONFIG_FILE, K8SConf)
        flink_conf = ProfileAdapter.load_if_exists(profile_name, FLINK_CONFIG_FILE, str)

        return ScliProfile(profile_name=profile_name, deployment_mode=profile_conf.deployment_mode,
                           docker_registry_url=profile_conf.docker_registry_url,
                           ververica_conf=vvp_conf, flink_conf=flink_conf, k8s_conf=k8s_conf,
                           resources_conf=resources_conf)


