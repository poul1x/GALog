$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$DistDir = ".\__dist_min"
$DistMinPyDir = "$DistDir\distminpy"
$DistMinPyEntry = "$DistMinPyDir\distminpy\main.py"
$DistMinPyVenvDir = "$DistMinPyDir\venv"
$ConfigPath = ".\.distminpy\config.windows.yaml"
$GALogSrcDir = ".\galog"
$GALogVenvDir = ".\venv"

# Write-Host "$GALogVenvDir\Scripts\Activate.ps"
# exit 0

if (-not (Test-Path -Path $GALogSrcDir)) {
    Write-Host "Source code directory not found: $GALogSrcDir"
	exit 1
}

if (-not (Test-Path -Path $GALogVenvDir)) {
    Write-Host "Virtualenv directory does not exist. Creating..."
	py -3 -m venv $GALogVenvDir
}

Write-Host "Ensure dependecies installed..."
& "$GALogVenvDir\Scripts\Activate.ps1"
pip install -r requirements-prod.txt

Write-Host "Verify Pyinstaller"
pyinstaller --version
if ($LASTEXITCODE -ne 0) {
	throw "Command 'pyinstaller --version' failed with exit code $LASTEXITCODE"
}

Write-Host "Create GALog bundle with pysinstaller"
pyinstaller `
	--clean `
	--noupx `
	--onedir `
	--console `
	--noconfirm `
	--name galog `
	--python-option u `
	--add-data "res;res" `
	--distpath $DistDir `
	--exclude-module .\galog\tests `
	.\galog\__main__.py

Write-Host "Deactivate GALog venv"
deactivate

Write-Host "Download and setup distminpy"
if (-not (Test-Path -Path $DistMinPyDir)) {
	git clone https://github.com/poul1x/distminpy.git $WorkDir
	if ($LASTEXITCODE -ne 0) {
        throw "Command 'git clone' failed with exit code $LASTEXITCODE"
    }

}

if (-not (Test-Path -Path $DistMinPyVenvDir)) {
    Write-Host "Virtualenv directory does not exist. Creating..."
	py -3 -m venv $DistMinPyVenvDir
}

Write-Host "Ensure dependencies installed"
& "$DistMinPyVenvDir\Scripts\Activate.ps1"
pip install -r "$DistMinPyDir\requirements-prod.txt"
if ($LASTEXITCODE -ne 0) {
	throw "Command 'pip install' failed with exit code $LASTEXITCODE"
}

# Write-Host "Verify distminpy"
# python distminpy\main.py

Write-Host "Verify distminpy + GALog"
python $DistMinPyEntry $ConfigPath -t
if ($LASTEXITCODE -ne 0) {
	throw "Command 'distminpy -t' failed with exit code $LASTEXITCODE"
}

Write-Host "Run distminpy on GALog dist"
python $DistMinPyEntry $ConfigPath
if ($LASTEXITCODE -ne 0) {
	throw "Command 'distminpy <config>' failed with exit code $LASTEXITCODE"
}