#!/bin/bash
# check for --test option
TEST=false
VERBOSE=""
if [ "$1" = "--test" ]; then
    echo -e "[test mode] – will publish to test.pypi.org\n"
    TEST=true
    shift
fi

# check for --verbose option
if [ "$1" = "--verbose" ]; then
    VERBOSE="--verbose"
    shift
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

# passthrough call ./build.sh and pass all args:
./dist/build.sh "$@"

# get newest tar.gz from /dist
LATEST=$(ls -t $ROOT/dist/*.gz | head -n1)

if [ "$TEST" = true ]; then
    python3 -m twine upload --repository-url https://test.pypi.org/legacy/ --username $USERNAME --password $PASSWORD $VERBOSE $LATEST
else
    python3 -m twine upload --username $USERNAME --password $PASSWORD $VERBOSE $LATEST
fi
