import os
from pathlib import Path
from unittest import mock

import pytest

from streamingcli.config import PROFILE_ENV_VARIABLE_NAME
from streamingcli.profile.profile_adapter import (
    DeploymentMode,
    ProfileAdapter,
    ScliProfile,
)

TEST_PATH = "tests/streamingcli/resources/platform/profile_vvp"

VVP_TEST_PROFILE = ScliProfile(
    profile_name="test_profile",
    deployment_mode=DeploymentMode.VVP,
    config={
        "vvp": {
            "url": "ververica_url",
            "namespace": "ververica_namespace",
            "api_token": "some_api_token",
            "deployment_target": "some_deployment_target",
        }
    },
    docker_registry_url="docker_registry_url",
)


class TestProfileAdapter:
    """Test getting profile name from env variable"""

    @pytest.fixture(scope="session", autouse=True)
    def chdir(self):
        os.chdir(Path(Path(__file__).parent.parent, "resources/platform/profile_vvp"))

    @mock.patch.dict(os.environ, {PROFILE_ENV_VARIABLE_NAME: "test"})
    def test_get_profile_name(self):
        assert ProfileAdapter.get_profile_name(profile_name=None) == "test"
        assert ProfileAdapter.get_profile_name(profile_name="default") == "default"

    """Test creating and managing profiles"""

    def test_loading_profile_data(self):

        saved_profile = ProfileAdapter.get_profile(
            profile_name=VVP_TEST_PROFILE.profile_name
        )
        assert saved_profile.profile_name == VVP_TEST_PROFILE.profile_name
        assert (
            saved_profile.config["vvp"]["url"] == VVP_TEST_PROFILE.config["vvp"]["url"]
        )
        assert (
            saved_profile.config["vvp"]["namespace"]
            == VVP_TEST_PROFILE.config["vvp"]["namespace"]
        )
        assert saved_profile.docker_registry_url == VVP_TEST_PROFILE.docker_registry_url
        assert (
            saved_profile.config["vvp"]["api_token"]
            == VVP_TEST_PROFILE.config["vvp"]["api_token"]
        )
        assert (
            saved_profile.config["vvp"]["deployment_target"]
            == VVP_TEST_PROFILE.config["vvp"]["deployment_target"]
        )

    """Test updating profile data"""

    def test_updating_profile_data(self):
        updated_token = "updated_token"
        updated_profile = ProfileAdapter.update_token(
            VVP_TEST_PROFILE, ververica_webtoken_secret=updated_token
        )
        assert updated_profile.config["vvp"]["api_token"] == updated_token

    """Test reading base profile"""

    def test_getting_temporary_profile(self):
        saved_profile = ProfileAdapter.get_profile(profile_name="base")

        assert saved_profile.profile_name == "base"
        assert saved_profile.deployment_mode == DeploymentMode.VVP
        assert saved_profile.docker_registry_url == "docker_registry_url"
