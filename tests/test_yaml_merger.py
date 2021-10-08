import pytest
import yaml

from streamingcli.project.yaml_merger import YamlMerger


class TestYamlMerger:
    """Test merging two YAML files"""

    def test_merge_two_yaml_files(self):
        yaml1 = '''name: John
age: 30
automobiles:
- brand: Honda
  type: Odyssey
  year: 2018
- brand: Toyota
  type: Sienna
  year: 2015'''
        merged = YamlMerger.merge_two_yaml(yaml1, "yaml/test.yml")

        with open("yaml/expected.yml", "r") as file:
            expected = yaml.safe_dump(yaml.load(file))

        assert merged == expected
