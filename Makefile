docker/build:
	docker-compose build

docker/run:
	docker-compose run --rm scli project init --project_name tmp_project

setup:
	pipenv install --dev

test:
	pipenv run pytest

cli/requirements:
	pipenv lock -r > requirements.txt

cli/package: cli/requirements
	pipenv run python setup.py sdist bdist_wheel

cli/uninstall:
	pipenv run python -m pip uninstall streamingcli

cli/install:
	pipenv run python -m pip install dist/*.whl

cli/install/force:
	pipenv run python -m pip install --force-reinstall dist/*.whl

cli/build: cli/package cli/install/force

cli/version:
	pipenv run python setup.py --version

cli/install/from-pypi:
	pipenv run python -m pip install streamingcli --extra-index-url https://__token__:$GITLAB_TOKEN@gitlab.com/api/v4/projects/29597698/packages/pypi/simple --upgrade

project/init:
	pipenv run scli project init --project_name tmp_project --project_type python

project/build:
	cd tmp_project; pipenv run scli project build

project/run:
	cd tmp_project; docker run tmp_project

project/deploy:
	pipenv run scli project deploy --profile local --docker-image-tag local --docker-image-repository tmp_project

project/deploy/overrides:
	cd tmp_project; pipenv run scli project deploy --profile local --docker-image-tag tmp_project:v1.1.22 --overrides_from_yaml=./deployment_prod.yml

platform/setup:
	pipenv run scli platform setup --ververica_url "http://localhost:8080" --ververica_namespace default --ververica_kubernetes_namespace vvp --ververica_deployment_target default --force

platform/apitoken/create:
	export PIPENV_VERBOSITY=-1; pipenv run scli platform api-token create --vvp-url "http://localhost:8080" --vvp-namespace default --name "test-token" --role "editor" --save-to-kubernetes-secret "vvp/secret"

platform/apitoken/remove:
	export PIPENV_VERBOSITY=-1; pipenv run scli platform api-token remove --vvp-url "http://localhost:8080" --vvp-namespace default --name "test-token" 

platform/target/add:
	export PIPENV_VERBOSITY=-1; pipenv run scli scli platform deployment-target create --profile local --kubernetes-namespace vvp

profile/add:
	pipenv run scli profile add local --vvp-url "http://localhost:8080" --vvp-namespace default --vvp-deployment-target default --docker-registry-url localhost:5000
