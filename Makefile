docker/build:
	docker-compose build

docker/run:
	docker run -it getindata/streaming-labs/streaming-cli project init --project_name tmp_project

install:
	pipenv install

requirements:
	pipenv lock -r > requirements.txt

package: requirements
	pipenv run python setup.py sdist bdist_wheel

install_scli:
	pipenv run python -m pip install streamingcli --extra-index-url https://__token__:$GITLAB_TOKEN@gitlab.com/api/v4/projects/29597698/packages/pypi/simple --upgrade

uninstall_scli:
	pipenv run python -m pip uninstall streamingcli

flink/init:
	scli project init --project_name tmp_project

flink/build:
	cd tmp_project; docker build .

flink/run:
	cd tmp_project; docker run tmp_project

flink/deploy:
	cd tmp_project; scli project deploy

platform/setup:
	scli platform setup --ververica_url "http://localhost:8080" --ververica_namespace default --ververica_kubernetes_namespace vvp
