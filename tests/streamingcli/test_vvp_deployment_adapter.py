import copy
import unittest
from pathlib import Path

from click import ClickException

from streamingcli.platform.ververica.deployment_adapter import VervericaDeploymentAdapter
from streamingcli.profile.profile_adapter import DeploymentMode, ScliProfile


class TestVVPProfileAdapter(unittest.TestCase):
    VVP_TEST_PROFILE = ScliProfile(
        profile_name="test_profile",
        deployment_mode=DeploymentMode.VVP,
        ververica_url="https://localhost/",
        ververica_namespace="default",
        ververica_deployment_target="deploymenttarget",
        ververica_api_token ="token",
        docker_registry_url="docker_registry_url"
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
        invalid_profile.ververica_namespace = None
        with self.assertRaises(ClickException):
            VervericaDeploymentAdapter(invalid_profile, self.DOCKER_TAG, self.PROJECT_NAME)

    def test_generating_default_project_template(self):
        vvp_deployment_adapter = VervericaDeploymentAdapter(
            self.VVP_TEST_PROFILE, self.DOCKER_TAG, self.PROJECT_NAME
        )
        print(vvp_deployment_adapter.generate_project_template([]))
        expected_file_path = "tests/streamingcli/resources/platform/vvp/expected_vvp_default_flink_deployment.yml"
        self.assertEqual(
            Path(expected_file_path).read_text(),
            vvp_deployment_adapter.generate_project_template([]),
        )

    def test_generating_project_with_custom_template(self):
        custom_profile = copy.deepcopy(self.VVP_TEST_PROFILE)
        custom_profile.ververica_deployment_template_path = "tests/streamingcli/resources/platform/vvp/custom_vvp_flink_deployment_template.yml"
        vvp_deployment_adapter = VervericaDeploymentAdapter(
            custom_profile, self.DOCKER_TAG, self.PROJECT_NAME
        )
        print(vvp_deployment_adapter.generate_project_template([]))
        expected_file_path = "tests/streamingcli/resources/platform/vvp/expected_vvp_custom_flink_deployment.yml"
        self.assertEqual(
            Path(expected_file_path).read_text(),
            vvp_deployment_adapter.generate_project_template([]),
        )
