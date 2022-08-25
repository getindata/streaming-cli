import hiyapyco


class YamlMerger:
    @staticmethod
    def merge_two_yaml(input1: str, yaml_file_path: str) -> str:
        merged_result = hiyapyco.load(
            [input1, yaml_file_path],
            method=hiyapyco.METHOD_MERGE,
            interpolate=True,
            failonmissingfiles=True,
            mergelists=True,
            castinterpolated=True,
        )

        return hiyapyco.dump(merged_result)
