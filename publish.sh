#!/bin/bash
# check for --test option 
TEST=false
if [ "$1" = "--test" ]; then
    echo -e "[test mode] – will publish to test.pypi.org\n"
    TEST=true
fi

# grab credentials from .pypirc file in .

# get the github root ROOT
ROOT=$(git rev-parse --show-toplevel)

# get the username and password
USERNAME="__token__"
if [ "$TEST" = true ]; then
    PASSWORD=$(grep -A 2 "\[testpypi\]" $ROOT/.pypirc | grep "password" | cut -d "=" -f 2)
else
    PASSWORD=$(grep -A 2 "\[pypi\]" $ROOT/.pypirc | grep "password" | cut -d "=" -f 2)
fi

# trim pw
PASSWORD=$(echo $PASSWORD | xargs)
# get the repo name
REPO="tinta"

# remove tinta.egg-info and dist
rm -rf $ROOT/tinta.egg-info
rm -rf $ROOT/dist
rm -rf $ROOT/build

# build the package with twine and hatchling
pip install --upgrade pip &> /dev/null
pip install twine hatchling setuptools wheel &> /dev/null

hatchling build
if [ "$TEST" = true ]; then
    python3 -m twine upload --repository-url https://test.pypi.org/legacy/ --username $USERNAME --password $PASSWORD dist/*
else
    python3 -m twine upload --username $USERNAME --password $PASSWORD dist/*
fi