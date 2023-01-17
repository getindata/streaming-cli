import os
from unittest import mock

from streamingcli.config import DEFAULT_PROFILE_PATH, PROFILE_ENV_VARIABLE_NAME
from streamingcli.profile.profile_adapter import (
    DeploymentMode,
    ProfileAdapter,
    ScliProfile,
)

VVP_TEST_PROFILE = ScliProfile(
    profile_name="test_profile",
    deployment_mode=DeploymentMode.VVP,
    ververica_url="ververica_url",
    ververica_namespace="ververica_namespace",
    docker_registry_url="docker_registry_url",
    ververica_api_token="some_api_token",
    ververica_deployment_target="some_deployment_target",
)


class TestProfileAdapter:
    """Test getting profile name from env variable"""

    @mock.patch.dict(os.environ, {PROFILE_ENV_VARIABLE_NAME: "test"})
    def test_get_profile_name(self):
        assert ProfileAdapter.get_profile_name(profile_name=None) == "test"
        assert ProfileAdapter.get_profile_name(profile_name="default") == "default"

    """Test creating and managing profiles"""

    def test_create_new_profile(self):
        ProfileAdapter.save_profile(VVP_TEST_PROFILE)
        assert os.path.isfile(DEFAULT_PROFILE_PATH) is True

        saved_profile = ProfileAdapter.get_profile(
            profile_name=VVP_TEST_PROFILE.profile_name
        )
        assert saved_profile.profile_name == VVP_TEST_PROFILE.profile_name
        assert saved_profile.ververica_url == VVP_TEST_PROFILE.ververica_url
        assert saved_profile.ververica_namespace == VVP_TEST_PROFILE.ververica_namespace
        assert saved_profile.docker_registry_url == VVP_TEST_PROFILE.docker_registry_url
        assert saved_profile.ververica_api_token == VVP_TEST_PROFILE.ververica_api_token
        assert saved_profile.k8s_namespace is None
        assert (
            saved_profile.ververica_deployment_target
            == VVP_TEST_PROFILE.ververica_deployment_target
        )

    """Test updating profile data"""

    def test_updating_profile_data(self):
        updated_ververica_url = "updated_ververica_url"
        updated_profile = ProfileAdapter.update_profile_data(
            VVP_TEST_PROFILE, ververica_url=updated_ververica_url
        )
        assert updated_profile.ververica_url == updated_ververica_url

    """Test creating temporary profile"""

    def test_getting_temporary_profile(self):
        ProfileAdapter.save_profile(VVP_TEST_PROFILE)
        empty_profile = ProfileAdapter.load_profiles(default_profile_path="~/aaa.json")
        assert len(empty_profile.profiles) == 0

        existing_profile = ProfileAdapter.load_profiles()
        assert len(existing_profile.profiles) > 0
