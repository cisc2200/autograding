FROM alpine:3.12

RUN apk update && \
    apk upgrade && \
    apk add --no-cache py3-pip build-base

RUN pip3 install colorama

ENV CC=gcc
ENV CXX=g++

COPY entrypoint.sh /entrypoint.sh
COPY autograding.py /autograding.py

ENTRYPOINT ["/entrypoint.sh"]
