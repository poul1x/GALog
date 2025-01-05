$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

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

Write-Host "Activate 'dev' virtual environment"
& "$GALogVenvDir/Scripts/Activate.ps1"
pip install -r requirements-dev.txt

Write-Host "Run autoflake"
autoflake -r "$GALogSrcDir" --remove-all-unused-imports -i
if ($LASTEXITCODE -ne 0) {
	throw "Command 'autoflake' failed"
}

Write-Host "Run isort"
isort -q "$GALogSrcDir"
if ($LASTEXITCODE -ne 0) {
	throw "Command 'isort' failed"
}

Write-Host "Run black"
black -q "$GALogSrcDir"
if ($LASTEXITCODE -ne 0) {
	throw "Command 'black' failed"
}

Write-Host "Done"