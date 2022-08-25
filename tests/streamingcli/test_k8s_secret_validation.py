import click
import pytest

from streamingcli.main import validate_k8s_secret


class TestK8SSecretValidator:
    """Validate K8S secret for empty string"""

    def test_k8s_secret_validation_for_empty_string(self):
        test_value = None
        assert (
            validate_k8s_secret("some_context", "some_param", test_value) == test_value
        )

    """Validate K8S secret for nonempty but incorrect string"""

    def test_k8s_secret_validation_for_non_empty_incorrect_string(self):
        with pytest.raises(click.BadParameter):
            test_value = "some"
            validate_k8s_secret("some_context", "some_param", test_value)

    """Validate K8S secret for nonempty and correct string"""

    def test_k8s_secret_validation_for_non_empty_correct_string(self):
        with pytest.raises(click.BadParameter):
            test_value = "extra: secret"
            validate_k8s_secret("some_context", "some_param", test_value)
