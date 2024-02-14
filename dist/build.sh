#!/bin/bash

# get the github root ROOT
ROOT=$(git rev-parse --show-toplevel)

# remove tinta.egg-info and dist
rm -rf $ROOT/tinta.egg-info
rm -rf $ROOT/dist/*.whl &>/dev/null
rm -rf $ROOT/dist/*.gz &>/dev/null

# build the package with twine and hatchling
pip install --upgrade pip &>/dev/null
pip install twine hatchling setuptools wheel &>/dev/null

hatchling build
twine check "$ROOT/dist/*.gz"
