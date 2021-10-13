import pytest
import hiyapyco

from streamingcli.project.yaml_merger import YamlMerger


class TestYamlMerger:
    """Test merging two YAML files"""
    def test_merge_two_yaml_files(self):
        merged = YamlMerger.merge_two_yaml("tests/yaml/input_1.yml", "tests/yaml/input_2.yml")
        expected = hiyapyco.dump(hiyapyco.load("tests/yaml/expected.yml"))

        assert merged == expected
