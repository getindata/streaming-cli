import tempfile

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

    @staticmethod
    def merge_two_yaml_str(input1: str, input2: str) -> str:
        file1 = tempfile.NamedTemporaryFile()
        file2 = tempfile.NamedTemporaryFile()
        with open(file1.name, 'w') as fh:
            fh.write(input1)
        with open(file2.name, 'w') as fh:
            fh.write(input2)
        merged = YamlMerger.merge_two_yaml(file1.name, file2.name)
        file1.close()
        file2.close()

        return merged
