FROM cisc2200/cpp-dev-container:latest

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install git python3 python3-blessings python3-tz \
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

ENV TERM=xterm-256color
ENV CXX=g++

COPY entrypoint.sh /entrypoint.sh
COPY autograding.py /autograding.py

ENTRYPOINT ["/entrypoint.sh"]
