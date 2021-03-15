#!/bin/sh -l

FILE=tests/prerun.sh
if [ -f "$FILE" ]; then
  cd tests
  sh tests/prerun.sh
  cd ..
else 
  mv tests/Makefile ./
  mv tests/test_driver.cpp ./
fi
python3 /autograding.py
res=$?
echo ::set-output name=points::"$(cat points)"
exit $res
