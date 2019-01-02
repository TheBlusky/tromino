#!/bin/sh
COVERAGE_FILE=/tmp/cov python -m coverage run --source . --omit tromino.py -m unittest tests &&
COVERAGE_FILE=/tmp/cov python -m coverage report -m