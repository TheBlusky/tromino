COVERAGE_FILE=/tmp/cov python -m coverage run --source . -m unittest tests &&
COVERAGE_FILE=/tmp/cov python -m coverage report -m