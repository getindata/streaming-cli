import os
import sys
from typing import List

from setuptools import find_packages, setup
from setuptools.command.install import install

__version__ = "1.9.1"

with open("README.md", "r") as fh:
    long_description = fh.read()


def get_requirements(filename: str) -> List[str]:
    with open(filename, "r", encoding="utf-8") as fp:
        reqs = [
            x.strip()
            for x in fp.read().splitlines()
            if not x.strip().startswith("#") and not x.strip().startswith("-i")
        ]
    return reqs


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""

    description = "verify that the git tag matches our version"

    def run(self) -> None:
        tag = os.getenv("CI_COMMIT_TAG")

        if tag != f"v{__version__}":
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, __version__
            )
            sys.exit(info)


EXTRAS_REQUIRE = {
    "tests": [
        "pytest>=6.2.2, <7.0.0",
        "pytest-cov>=2.8.0, <3.0.0",
        "pre-commit==2.15.0",
        "tox==3.21.1",
    ]
}


setup(
    name="streamingcli",
    version=__version__,
    author="GetInData",
    author_email="office@getindata.com",
    description="Streaming platform CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/getindata/streaming-cli",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    install_requires=get_requirements("requirements.txt"),
    extras_require=EXTRAS_REQUIRE,
    py_modules=["streamingcli"],
    entry_points={
        "console_scripts": [
            "scli = streamingcli.main:cli",
        ],
    },
    package_data={
        "streamingcli.project": ["templates/*"],
    },
    cmdclass={
        "verify": VerifyVersionCommand,
    },
)
