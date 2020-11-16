#!/bin/sh -l

mv tests/Makefile ./
mv tests/test_driver.cpp ./
python3 /autograding.py
exit $?
