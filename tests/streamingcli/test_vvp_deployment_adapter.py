import copy
import os
import unittest
from pathlib import Path

import pytest
from click import ClickException

from streamingcli.platform.ververica.deployment_adapter import (
    VervericaDeploymentAdapter,
)
from streamingcli.profile.profile_adapter import (
    DeploymentMode,
    ProfileAdapter,
    ScliProfile,
)


class TestVVPProfileAdapter(unittest.TestCase):
    @pytest.fixture(scope="session", autouse=True)
    def chdir(self):
        os.chdir(Path(Path(__file__).parent, "resources/platform/profile_vvp"))

    VVP_TEST_PROFILE = ScliProfile(
        profile_name="format",
        deployment_mode=DeploymentMode.VVP,
        config={
            "vvp": {
                "url": "https://localhost/",
                "namespace": "default",
                "deployment_target": "deploymenttarget",
                "api_token": "token",
            },
        },
        docker_registry_url="docker_registry_url",
    )
    PROJECT_NAME = "test"
    DOCKER_TAG = "latest"

    def test_init_with_valid_profile(self):
        vvp_deployment_adapter = VervericaDeploymentAdapter(
            self.VVP_TEST_PROFILE, self.DOCKER_TAG, self.PROJECT_NAME
        )
        self.assertEqual(vvp_deployment_adapter.profile_data, self.VVP_TEST_PROFILE)
        self.assertEqual(vvp_deployment_adapter.project_name, self.PROJECT_NAME)
        self.assertEqual(vvp_deployment_adapter.docker_image_tag, self.DOCKER_TAG)

    def test_init_with_invalid_profile(self):
        invalid_profile = copy.deepcopy(self.VVP_TEST_PROFILE)
        invalid_profile.config["vvp"]["namespace"] = None
        with self.assertRaises(ClickException):
            VervericaDeploymentAdapter(
                invalid_profile, self.DOCKER_TAG, self.PROJECT_NAME
            )

    def test_generating_default_project_template(self):
        vvp_deployment_adapter = VervericaDeploymentAdapter(
            ProfileAdapter.get_profile("format"), self.DOCKER_TAG, self.PROJECT_NAME
        )
        result = vvp_deployment_adapter.generate_project_template([])
        print(result)
        expected_file_path = "../vvp/expected_vvp_default_flink_deployment.yml"
        self.assertEqual(
            Path(expected_file_path).read_text(),
            "\n".join([s for s in result.split("\n") if s.strip()]),
        )

    def test_generating_default_project_template_with_deps(self):
        vvp_deployment_adapter = VervericaDeploymentAdapter(
            ProfileAdapter.get_profile("format"), self.DOCKER_TAG, self.PROJECT_NAME
        )
        result = vvp_deployment_adapter.generate_project_template(["another.jar"])
        print(result)
        expected_file_path = "../vvp/expected_vvp_flink_deployment_with_deps.yml"
        self.assertEqual(
            Path(expected_file_path).read_text(),
            "\n".join([s for s in result.split("\n") if s.strip()]),
        )

    def test_generating_project_with_custom_template(self):
        custom_deployment_file = "../vvp/custom_vvp_flink_deployment_template.yml"
        custom_profile = copy.deepcopy(self.VVP_TEST_PROFILE)
        custom_profile.ververica_deployment_template_path = custom_deployment_file
        vvp_deployment_adapter = VervericaDeploymentAdapter(
            custom_profile, self.DOCKER_TAG, self.PROJECT_NAME
        )
        result = vvp_deployment_adapter.generate_project_template(
            [], custom_deployment_file
        )
        print(result)
        expected_file_path = "../vvp/expected_vvp_custom_flink_deployment.yml"
        self.assertEqual(
            Path(expected_file_path).read_text(),
            result,
        )
