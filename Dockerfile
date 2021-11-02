FROM python:3.8-alpine

RUN set -ex && \
    apk add --no-cache git

COPY ./dist/*.whl .

RUN set -ex && \
    python3 -m pip install *.whl

ENTRYPOINT ["scli"]

WORKDIR /app
