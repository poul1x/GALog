$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$DistDir = ".\__dist_min"
$DistMinPyDir = "$DistDir\distminpy"
$DistMinPyEntry = "$DistMinPyDir\distminpy\main.py"
$DistMinPyVenvDir = "$DistMinPyDir\venv"
$ConfigPath = ".\.distminpy\config.windows.yaml"
$GALogSrcDir = ".\galog"
$GALogVenvDir = ".\venv"

Write-Host "Ensure python3.9 installed"
py -3.9 --version
if ($LASTEXITCODE -ne 0) {
	throw "Command 'py -3.9 --version' failed"
}

if (-not (Test-Path -Path $GALogSrcDir)) {
	throw "Source code directory not found: $GALogSrcDir"
}

if (-not (Test-Path -Path $GALogVenvDir)) {
    Write-Host "Virtualenv directory does not exist. Creating..."
	py -3.9 -m venv $GALogVenvDir
}

Write-Host "Ensure dependecies installed..."
& "$GALogVenvDir\Scripts\Activate.ps1"
pip install -r requirements-prod.txt

Write-Host "Verify Pyinstaller"
pyinstaller --version
if ($LASTEXITCODE -ne 0) {
	throw "Command 'pyinstaller --version' failed"
}

Write-Host "Create GALog bundle with pyinstaller"
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
	"$GALogSrcDir\__main__.py"

Write-Host "Deactivate GALog venv"
deactivate

Write-Host "Download and setup distminpy"
if (-not (Test-Path -Path $DistMinPyDir)) {
	git clone https://github.com/poul1x/distminpy.git $WorkDir
	if ($LASTEXITCODE -ne 0) {
        throw "Command 'git clone' failed"
    }

}

if (-not (Test-Path -Path $DistMinPyVenvDir)) {
    Write-Host "Virtualenv directory does not exist. Creating..."
	py -3.9 -m venv $DistMinPyVenvDir
}

Write-Host "Ensure dependencies installed"
& "$DistMinPyVenvDir\Scripts\Activate.ps1"
pip install -r "$DistMinPyDir\requirements-prod.txt"
if ($LASTEXITCODE -ne 0) {
	throw "Command 'pip install' failed"
}

Write-Host "Verify distminpy + GALog"
python $DistMinPyEntry $ConfigPath -t
if ($LASTEXITCODE -ne 0) {
	throw "Command 'distminpy -t' failed"
}

Write-Host "Run distminpy on GALog dist"
python $DistMinPyEntry $ConfigPath
if ($LASTEXITCODE -ne 0) {
	throw "Command 'distminpy <config>' failed"
}