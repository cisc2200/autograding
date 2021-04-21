FROM cisc2200/cpp-dev-container:latest

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install python3 python3-blessings python3-tz \
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

ENV CC=gcc
ENV CXX=g++
ENV TERM=xterm-256color

COPY entrypoint.sh /entrypoint.sh
COPY autograding.py /autograding.py

ENTRYPOINT ["/entrypoint.sh"]
