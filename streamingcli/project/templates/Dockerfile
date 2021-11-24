FROM registry.gitlab.com/getindata/streaming-labs/docker-images/vvp-flink-python:latest

USER flink

COPY ./Pipfile /flink/opt

RUN set -ex && \
    cd /flink/opt && \
    pipenv lock -r > requirements.txt && \
    pip install -r requirements.txt

COPY ./src /app/src
COPY .streaming_config.yml ./jars/* /app/lib/