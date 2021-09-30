import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setuptools.setup(
    name="streamingcli",
    version="0.1.5",
    author="GetInData",
    author_email="office@getindata.com",
    description="Streaming platform CLI",
    long_description=long_description,
    url="https://gitlab.com/getindata/streaming-labs/streaming-cli",
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    install_requires=[requirements],
    py_modules=['streamingcli'],
    entry_points={
        'console_scripts': [
            'scli = streamingcli.main:cli',
        ],
    },
    package_data={
          'streamingcli.project': ['templates/*'],
    },
)