from typing import Any

import yaml


def yaml_pretty(d: Any, indent: int = 8) -> str:
    dump = yaml.dump(d)
    res = ""
    for line in dump.split("\n"):
        res += " " * indent + line + "\n"
    return res
