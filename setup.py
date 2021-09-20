import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="streamingcli",
    version="0.1.3",
    author="GetInData",
    author_email="office@getindata.com",
    description="Streaming platform CLI",
    long_description=long_description,
    url="https://gitlab.com/getindata/streaming-labs/streaming-cli",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'click',
        'gitpython',
        'pyyaml',
        'kubernetes',
        'dataclasses_json'
    ],
    py_modules=['scli'],
    entry_points={
        'console_scripts': [
            'scli = streamingcli.main:cli',
        ],
    },
)