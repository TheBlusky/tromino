@echo off
echo + Preparing env
docker stop mongo 2>NUL
docker run --rm -d --name mongo mongo > NUL
echo + Starting tests
docker run --rm -v %cd%:/opt/tromino:ro -w /opt/tromino/src --link mongo theblusky/tromino:dev sh run_tests.sh
echo + Cleaning env
docker stop mongo 2>NUL
