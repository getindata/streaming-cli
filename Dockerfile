FROM python:3.8-buster

RUN set -ex && \
    apt-get install -y --no-install-recommends git

RUN set -ex && \
    python3 -m pip install --upgrade pip \
    && python3 -m pip install --upgrade setuptools

COPY ./dist/*.whl .

RUN set -ex && \
    python3 -m pip install *.whl

ENTRYPOINT ["scli"]

WORKDIR /app
