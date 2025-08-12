$GALogName = "galog"
$GALogSrcDir = ".\galog"
$GALogVenvDir = ".\venv"

$DistDir = ".\__dist_release"
$OutDir = "$DistDir\$GALogName"

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
	throw "Command 'pyinstaller --version' failed with exit code $LASTEXITCODE"
}

Write-Host "Run pyinstaller"
pyinstaller `
	--clean `
	--noupx `
	--onedir `
	--noconsole `
	--noconfirm `
	--name $GALogName `
	--add-data "res;res" `
	--add-data "config;config" `
	--distpath $DistDir `
	--exclude-module .\galog\tests `
	"$GALogSrcDir\__main__.py"

if ($LASTEXITCODE -ne 0) {
	throw "Command 'pyinstaller' failed with exit code $LASTEXITCODE"
}

Write-Host "Remove unused files"
Remove-Item -ErrorAction Continue -Recurse -Path $OutDir\PyQt5\Qt5\translations\*
Remove-Item -ErrorAction Continue -Path $OutDir\api-ms-win*.dll
Remove-Item -ErrorAction Continue -Path $OutDir\ucrtbase.dll
Remove-Item -ErrorAction Continue -Path $OutDir\unicodedata.pyd
Remove-Item -ErrorAction Continue -Path $OutDir\_queue.pyd
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\bin\d3dcompiler_47.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\bin\libEGL.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\bin\libGLESv2.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\bin\opengl32sw.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\bin\Qt5DBus.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\bin\Qt5Network.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\bin\Qt5Qml.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\bin\Qt5QmlModels.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\bin\Qt5Quick.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\bin\Qt5WebSockets.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\bin\VCRUNTIME140_1.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\plugins\generic\qtuiotouchplugin.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\plugins\platforms\qminimal.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\plugins\platforms\qoffscreen.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\plugins\platforms\qwebgl.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\plugins\platformthemes\qxdgdesktopportal.dll
Remove-Item -ErrorAction Continue -Path $OutDir\libcrypto-1_1.dll
Remove-Item -ErrorAction Continue -Path $OutDir\libffi-7.dll
Remove-Item -ErrorAction Continue -Path $OutDir\libssl-1_1.dll
Remove-Item -ErrorAction Continue -Path $OutDir\pyexpat.pyd
Remove-Item -ErrorAction Continue -Path $OutDir\VCRUNTIME140.dll
Remove-Item -ErrorAction Continue -Path $OutDir\VCRUNTIME140_1.dll
Remove-Item -ErrorAction Continue -Path $OutDir\_bz2.pyd
Remove-Item -ErrorAction Continue -Path $OutDir\_decimal.pyd
Remove-Item -ErrorAction Continue -Path $OutDir\_elementtree.pyd
Remove-Item -ErrorAction Continue -Path $OutDir\_hashlib.pyd
Remove-Item -ErrorAction Continue -Path $OutDir\_ssl.pyd
Remove-Item -ErrorAction Continue -Path $OutDir\_uuid.pyd
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\bin\MSVCP140.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\bin\MSVCP140_1.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\plugins\iconengines\qsvgicon.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\plugins\imageformats\qgif.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\plugins\imageformats\qicns.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\plugins\imageformats\qico.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\plugins\imageformats\qjpeg.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\plugins\imageformats\qtga.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\plugins\imageformats\qtiff.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\plugins\imageformats\qwbmp.dll
Remove-Item -ErrorAction Continue -Path $OutDir\PyQt5\Qt5\plugins\imageformats\qwebp.dll
Remove-Item -ErrorAction Continue -Path $OutDir\yaml\_yaml.cp39-win_amd64.pyd

Write-Host "Strip files"
strip -s $OutDir\python3.dll
strip -s $OutDir\python39.dll
strip -s $OutDir\select.pyd
strip -s $OutDir\_ctypes.pyd
strip -s $OutDir\_lzma.pyd
strip -s $OutDir\_socket.pyd
strip -s $OutDir\pydantic_core\_pydantic_core.cp39-win_amd64.pyd
strip -s $OutDir\PyQt5\QtCore.pyd
strip -s $OutDir\PyQt5\QtGui.pyd
strip -s $OutDir\PyQt5\QtWidgets.pyd
strip -s $OutDir\PyQt5\sip.cp39-win_amd64.pyd
strip -s $OutDir\PyQt5\Qt5\bin\Qt5Core.dll
strip -s $OutDir\PyQt5\Qt5\bin\Qt5Gui.dll
strip -s $OutDir\PyQt5\Qt5\bin\Qt5Svg.dll
strip -s $OutDir\PyQt5\Qt5\bin\Qt5Widgets.dll
strip -s $OutDir\PyQt5\Qt5\plugins\imageformats\qsvg.dll
strip -s $OutDir\PyQt5\Qt5\plugins\platforms\qwindows.dll
strip -s $OutDir\PyQt5\Qt5\plugins\styles\qwindowsvistastyle.dll

Write-Host "Done"
