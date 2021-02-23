FROM mcr.microsoft.com/vscode/devcontainers/cpp:focal

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install python3 python3-colorama

ENV CC=gcc
ENV CXX=g++

COPY entrypoint.sh /entrypoint.sh
COPY autograding.py /autograding.py

ENTRYPOINT ["/entrypoint.sh"]
