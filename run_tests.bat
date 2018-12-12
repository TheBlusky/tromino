@echo off
docker stop mongo
docker run --rm -d --name mongo mongo
docker run --rm -it -v %cd%:/opt/tromino:ro -w /opt/tromino/src --link mongo theblusky/tromino:dev sh run_tests.sh
docker stop mongo
