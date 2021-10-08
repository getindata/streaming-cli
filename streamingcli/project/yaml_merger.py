import yaml


class YamlMerger:
    @staticmethod
    def merge_two_yaml(input1: str, yaml_file_path: str) -> str:
        yaml_1 = yaml.safe_load(input1)
        with open(yaml_file_path, "r") as file:
            yaml_2 = yaml.load(file)
        yaml_1.update(yaml_2)

        return yaml.safe_dump(yaml_1)