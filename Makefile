docker/build:
	docker-compose build

docker/run:
	docker-compose run --rm scli project init --project_name tmp_project

setup:
	pipenv install

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

flink/init:
	pipenv run scli project init --project_name tmp_project

flink/build:
	cd tmp_project; pipenv run scli project build

flink/run:
	cd tmp_project; docker run tmp_project

flink/deploy:
	cd tmp_project; pipenv run scli project deploy

flink/deploy/overrides:
	cd tmp_project; pipenv run scli project deploy --overrides_from_yaml=./deployment_prod.yml

platform/setup:
	pipenv run scli platform setup --ververica_url "http://localhost:8080" --ververica_namespace default --ververica_kubernetes_namespace vvp --ververica_deployment_target default --force
