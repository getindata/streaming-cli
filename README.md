[![Python Version](https://img.shields.io/badge/python-3.8-blue.svg)](https://github.com/getindata/streaming-cli)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![SemVer](https://img.shields.io/badge/semver-2.0.0-green)](https://semver.org/)
[![PyPI version](https://badge.fury.io/py/streamingcli.svg)](https://pypi.org/project/streamingcli/)
[![Downloads](https://pepy.tech/badge/streamingcli)](https://pepy.tech/badge/streamingcli)

# Streaming platform CLI

## Usage

### Platform operations

Commands below will help you set up and work with Ververica Platform.

#### Generating API token

```shell
scli platform api-token create \
  --vvp-url "https://vvp.example.com" \
  --vvp-namespace "default" \
  --name "cicd" \
  --role "editor" \
  --save-to-kubernetes-secret "vvp/secret"
```

Sample response:

```json
{
  "namespace": "default",
  "name": "cicd",
  "role": "editor",
  "secret": "x§11d091jd1jd9jasd0j"
}
```

#### Removing API token

```shell
scli platform api-token remove \
  --vvp-url "https://vvp.example.com" \
  --vvp-namespace "default" \
  --name "cicd"
```

#### Profiles

You can set up your own profile, which will help you to connect to Ververica. Instead of providing common parameters to
each command, you can just pass the profile name with `--profile`
or export environmental variable as `SCLI_PROFILE`.

##### Creating a profile

The command below will walk you through an interactive way of setting up a profile:

```shell
scli profile add sandbox
```

You can also set up a profile in a non-interactive way by providing all required parameters as arguments:

```shell
scli profile add sandbox \
  --vvp-url "https://vvp.streaming-platform.getindata.dev" \
  --vvp-namespace "default" \
  --vvp-deployment-target "vvp-team1" \
  --vvp-api-token "x§11d091jd1jd9jasd0j" \
  --docker-registry-url "registry.gitlab.com/flink-jobs"
```

#### Creating Deployment target

```shell
scli platform deployment-target create \
  --vvp-url "https://vvp.example.com" \
  --vvp-namespace "default" \
  --vvp-api-token "x§11d091jd1jd9jasd0j" \
  --name "vvp-team1" \
  --kubernetes-namespace "vvp" \
  --profile "sandbox"
```

> Parameters `--vvp-url`, `--vvp-namespace`, `--vvp-api-token`, `--vvp-deployment-target` are optional if they can be read from profile.

Sample response:

```json
{
  "name": "vvp-team1"
}
```

#### Deploying job

```shell
scli project deploy \
  --vvp-url "https://vvp.example.com" \
  --vvp-namespace "default" \
  --vvp-api-token "x§11d091jd1jd9jasd0j" \
  --vvp-deployment-target "vvp-team1" \
  --docker-image-registry "${CI_REGISTRY_IMAGE}" \
  --docker-image-tag "${CI_COMMIT_TAG}" \
  --docker-image-repository tmp_project \
  --profile "sandbox"
```

> Parameters `--vvp-url`, `--vvp-namespace`, `--vvp-api-token`, `--vvp-deployment-target` are optional if they can be read from profile.

#### Building job Docker image

```shell
scli project build \
  --docker-image-tag "latest"
```

#### Logging to Docker repository

```shell
scli docker login \
  --username "user" \
  --password "password" \
  --docker-registry-url registry.gitlab.com/getindata/
```

> Parameters`--docker-image-tag` is optional and has default value `latest`.

### Project operations

## SCLI Development

### Prerequisities ##

* `pipenv`

### Build

* `make setup` - Install dependencies required to build a wheel package
* `make cli/package` - Create a wheel package

### Install

* `make cli/install` - Install a wheel package
* `make cli/install/force` - Reinstall a wheel package
