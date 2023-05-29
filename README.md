[![Python Version](https://img.shields.io/badge/python-3.8-blue.svg)](https://github.com/getindata/streaming-cli)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![SemVer](https://img.shields.io/badge/semver-2.0.0-green)](https://semver.org/)
[![PyPI version](https://badge.fury.io/py/streamingcli.svg)](https://pypi.org/project/streamingcli/)
[![Downloads](https://pepy.tech/badge/streamingcli)](https://pepy.tech/badge/streamingcli)

# Streaming platform CLI

## Usage

### Platform operations

#### Environments

You can set up your own environment, which will allow you to connect to Ververica/K8S operator. You need to fill
properties within `config/<env_name>` directory. `config/flink_deployment.yml` is default deployment descriptor file
for each environment (you can overwrite it using `--file-descriptor-path` flag). You can use jinja for templating
(look at the tests for an example). `base` environment is the default environment. Others environment override
parameters from `base`. You need to have in `base` or your own environment `profile.yml`
file with given schema:
```yaml
deployment_mode: <VVP|K8S_OPERATOR>
docker_registry_url: <docker_registry_url>
```
You need also extra file(s) with Ververica/Kubernetes configuration
and optionally other configuration used for templating.

Example `vvp.yml`:
```yaml
vvp:
  url: <ververica_url>
  namespace: <ververica_namespace>
  deployment_target: <some_deployment_target>
  ```

Example `k8s.yml`:
```yaml
k8s:
  namespace: test_ns
```

For most of the command, you can pass the environment name with `--env`
or export environmental variable as `SCLI_ENV`.

#### Deploying job

```shell
scli project deploy \
  --vvp-api-token "x§11d091jd1jd9jasd0j" \
  --docker-image-tag "${CI_COMMIT_TAG}" \
  --profile "dev"
```

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
  --profile "dev"
```

> Parameters`--docker-image-tag` is optional and has default value `latest`.

### Providing certificates
Scli uses `requests` library to deploy jobs to Ververica Platform via REST Api. Currently `requests` does not support
automatic downloading of intermediate certificates so entire chain of certificates should be present before making
a http call

example:
```sh
sh -c 'CA_CERT_PATH=`python3 -c "import requests; print(requests.certs.where())"`;for CERT in certs/*; do cat ${CERT}; done >> ${CA_CERT_PATH}';

```

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
