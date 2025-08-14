#!/bin/bash

GALogName="galog"
GALogSrcDir="./galog"
GALogVenvDir="./venv"

DistDir="./__dist_release"
OutDir="$DistDir/$GALogName"

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

echo "Run pyinstaller"
pyinstaller \
--clean \
--noupx \
--onedir \
--noconsole \
--noconfirm \
--name $GALogName \
--add-data "res:res" \
--add-data "config:config" \
--distpath $DistDir \
--exclude-module ./galog/tests \
"$GALogSrcDir/__main__.py"

if [ $? -ne 0 ]; then
    echo "Command 'pyinstaller' failed"
    exit 1
fi

echo "Remove unused files"
TmpDir="$OutDir.tmp"
mv $OutDir $TmpDir
mkdir $OutDir

mv "$TmpDir/PyQt5" $OutDir
rm -rf "$OutDir/PyQt5/Qt5"

mv "$TmpDir/base_library.zip" $OutDir
mv "$TmpDir/lib-dynload" $OutDir
mv "$TmpDir/pydantic_core" $OutDir
mv "$TmpDir/res" $OutDir
mv "$TmpDir/config" $OutDir

mv "$TmpDir/galog" $OutDir
mv "$TmpDir/libffi.so.7" $OutDir
mv "$TmpDir/libpython3.9.so.1.0" $OutDir

echo "Strip files"
strip -s "$OutDir/libffi.so.7"
strip -s "$OutDir/libpython3.9.so.1.0"
strip -s "$OutDir/pydantic_core/_pydantic_core.cpython-39-x86_64-linux-gnu.so"
strip -s "$OutDir/PyQt5/QtGui.abi3.so"
strip -s "$OutDir/PyQt5/QtWidgets.abi3.so"
strip -s "$OutDir/PyQt5/QtCore.abi3.so"
strip -s "$OutDir/PyQt5/sip.cpython-39-x86_64-linux-gnu.so"
strip -s "$OutDir/galog"

echo "Done"
