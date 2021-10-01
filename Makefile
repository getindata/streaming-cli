install:
	pip install .

install-pip-setuptools:
	python -m pip install -U "pip>=20.0" "setuptools>=38.0" wheel

package: install
	python setup.py sdist bdist_wheel

flink/init:
	scli project init --project_name tmp_project

flink/build:
	cd tmp_project; docker build --file=.vvp/Dockerfile .

flink/run:
	cd tmp_project; docker run tmp_project

flink/deploy:
	cd tmp_project; scli project deploy

platform/setup:
	scli platform setup --ververica_url "http://localhost:8080" --ververica_namespace default --ververica_kubernetes_namespace vvp
