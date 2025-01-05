#!/bin/bash

set -eu

DistDir="./__dist_min"
DistMinPyDir="$DistDir/distminpy"
DistMinPyEntry="$DistMinPyDir/distminpy/main.py"
DistMinPyVenvDir="$DistMinPyDir/venv"
ConfigPath="./.distminpy/config.linux.yaml"
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

echo "Ensure dependecies installed..."
source "$GALogVenvDir/bin/activate"
pip install --upgrade pip
pip install -r requirements-prod.txt

echo "Verify Pyinstaller"
pyinstaller --version
if [ $? -ne 0 ]; then
    echo "Command 'pyinstaller --version' failed"
    exit 1
fi

echo "Create GALog bundle with pyinstaller"
pyinstaller \
--clean \
--noupx \
--onedir \
--console \
--noconfirm \
--name galog \
--python-option u \
--add-data "res:res" \
--distpath $DistDir \
--exclude-module ./galog/tests \
"$GALogSrcDir/__main__.py"

echo "Deactivate GALog venv"
deactivate

echo "Download and setup distminpy"
if [ ! -d "$DistMinPyDir" ]; then
    git clone https://github.com/poul1x/distminpy.git $WorkDir
    if [ $? -ne 0 ]; then
        echo "Command 'git clone' failed"
        exit 1
    fi
fi

if [ ! -d "$DistMinPyVenvDir" ]; then
    echo "Virtualenv directory does not exist. Creating..."
    python3.9 -m venv $DistMinPyVenvDir
fi

echo "Ensure dependencies installed"
source "$DistMinPyVenvDir/bin/activate"
pip install -r "$DistMinPyDir/requirements-prod.txt"
if [ $? -ne 0 ]; then
    echo "Command 'pip install' failed"
    exit 1
fi

echo "Verify distminpy + GALog"
python $DistMinPyEntry $ConfigPath -t
if [ $? -ne 0 ]; then
    echo "Command 'distminpy -t' failed"
    exit 1
fi

echo "Run distminpy on GALog dist"
python $DistMinPyEntry $ConfigPath
if [ $? -ne 0 ]; then
    echo "Command 'distminpy <config>' failed"
    exit 1
fi