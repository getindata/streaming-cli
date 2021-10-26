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
You can set up your own profile, which will help you to connect to Ververica. 
Instead of providing common parameters to each command, you can just pass the profile name with `--profile` 
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
  --vvp-deployment-target "vvp-team1" \
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
```
scli project deploy \
  --vvp-url "https://vvp.example.com" \
  --vvp-namespace "default" \
  --vvp-api-token "x§11d091jd1jd9jasd0j" \
  --vvp-deployment-target "vvp-team1" \
  --docker_image_registry "${CI_REGISTRY_IMAGE}" \
  --docker-image-tag "${CI_COMMIT_TAG}" \
  --docker-image-repository tmp_project \
  --profile "sandbox"
```
> Parameters `--vvp-url`, `--vvp-namespace`, `--vvp-api-token`, `--vvp-deployment-target` are optional if they can be read from profile.

### Project operations

## SCLI Development
### Prerequisities ##
* `pipenv`

### Build
* `make setup` - Install dependencies required to build a wheel package
* `make package` - Create a wheel package

### Install
* `make install` - Install a wheel package
* `make install/force` - Reinstall a wheel package