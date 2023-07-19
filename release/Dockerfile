# syntax=docker/dockerfile:1
FROM context

ARG PYTHON_VERSION
ARG STREAMING_CLI_VERSION

RUN apk add --no-cache build-base python3>=${PYTHON_VERSION} python3-dev>=${PYTHON_VERSION} py3-pip curl
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
RUN python3 -m pip install --no-cache wheel
RUN source "$HOME/.cargo/env" && python3 -m pip install --no-cache streamingcli==${STREAMING_CLI_VERSION} --ignore-installed six

WORKDIR /root
ENTRYPOINT ["sh", "-c", "scli"]