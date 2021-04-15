FROM mcr.microsoft.com/vscode/devcontainers/cpp:focal

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install python3 python3-blessings python3-tz

ENV CC=gcc
ENV CXX=g++
ENV TERM=xterm-256color

COPY entrypoint.sh /entrypoint.sh
COPY autograding.py /autograding.py

ENTRYPOINT ["/entrypoint.sh"]
