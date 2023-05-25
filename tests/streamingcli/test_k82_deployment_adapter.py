import copy
import os
import unittest
from pathlib import Path

import pytest
from click import ClickException

from streamingcli.platform.k8s.deployment_adapter import K8SDeploymentAdapter
from streamingcli.profile.profile_adapter import (
    DeploymentMode,
    ProfileAdapter,
    ScliProfile,
)


class TestK8SProfileAdapter(unittest.TestCase):
    K8S_TEST_PROFILE = ScliProfile(
        profile_name="test_profile",
        deployment_mode=DeploymentMode.K8S_OPERATOR,
        docker_registry_url="docker_registry_url",
        config={"k8s": {"namespace": "test_ns"}},
    )
    PROJECT_NAME = "test"
    DOCKER_TAG = "latest"

    @pytest.fixture(scope="session", autouse=True)
    def chdir(self):
        os.chdir(Path(Path(__file__).parent, "resources/platform/profile_k8s"))

    def test_init_with_valid_profile(self):
        k8s_deployment_adapter = K8SDeploymentAdapter(
            self.K8S_TEST_PROFILE, self.DOCKER_TAG, self.PROJECT_NAME
        )
        self.assertEqual(k8s_deployment_adapter.profile_data, self.K8S_TEST_PROFILE)
        self.assertEqual(k8s_deployment_adapter.project_name, self.PROJECT_NAME)
        self.assertEqual(k8s_deployment_adapter.docker_image_tag, self.DOCKER_TAG)

    def test_init_with_invalid_profile(self):
        invalid_profile = copy.deepcopy(self.K8S_TEST_PROFILE)
        invalid_profile.config["k8s"]["namespace"] = None
        with self.assertRaises(ClickException):
            K8SDeploymentAdapter(invalid_profile, self.DOCKER_TAG, self.PROJECT_NAME)

    def test_generating_project_template(self):
        k8s_deployment_adapter = K8SDeploymentAdapter(
            ProfileAdapter.get_profile("base"), self.DOCKER_TAG, self.PROJECT_NAME
        )
        result = k8s_deployment_adapter.generate_project_template([])
        print(result)
        file_path = "../k8s_flink_deployment.yml"
        self.assertEqual(
            Path(file_path).read_text(),
            "\n".join([s for s in result.split("\n") if s.strip()]),
        )
