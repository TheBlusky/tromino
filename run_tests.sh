#!/bin/sh
echo "+ Preparing env"
docker stop mongo 2>/dev/null
docker run --rm -d --name mongo mongo > /dev/null
echo "+ Starting tests"
docker run --rm -v $(pwd):/opt/tromino:ro -w /opt/tromino/src --link mongo theblusky/tromino:dev sh run_tests.sh
echo "+ Cleaning env"
docker stop mongo 2>/dev/null
