#!/bin/bash

set -eu

GALogSrcDir="./galog"
GALogVenvDir="./venv"

echo "Ensure python3.9 installed"
python3.9 --version
if [ $? -ne 0 ]; then
    echo "Command 'python3.9 --version' failed"
    exit 1
fi

if [ ! -d "$GALogSrcDir" ]; then
    echo "Source code directory not found: $GALogSrcDir"
    exit 1
fi

if [ ! -d "$GALogVenvDir" ]; then
    echo "Virtualenv directory does not exist. Creating..."
    python3.9 -m venv $GALogVenvDir
fi

echo "Activate 'dev' virtual environment"
source "$GALogVenvDir/bin/activate"
pip install -r requirements-dev.txt

echo "Run autoflake"
autoflake -r "$GALogSrcDir" --remove-all-unused-imports -i
if [ $? -ne 0 ]; then
    echo "Command 'autoflake' failed"
    exit 1
fi

echo "Run isort"
isort -q "$GALogSrcDir"
if [ $? -ne 0 ]; then
    echo "Command 'isort' failed"
    exit 1
fi

echo "Run black"
black -q "$GALogSrcDir"
if [ $? -ne 0 ]; then
    echo "Command 'black' failed"
    exit 1
fi

echo "Done"