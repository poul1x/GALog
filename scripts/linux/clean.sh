#!/bin/bash

set -eu

DistDirMin="./__dist_min"
DistDirRelease="./__dist_release"
GALogVenvDir="./venv"

echo "Clean GALog venv"
rm -rf $GALogVenvDir

echo "Clean min dir"
rm -rf $DistDirMin

echo "Clean release dir"
rm -rf $DistDirRelease

echo "Done"