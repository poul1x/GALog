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
rm -rf $OutDir/PyQt5/Qt5/translations/*
rm $OutDir/libQt5Qml.so.5
rm $OutDir/libcom_err.so.2
rm $OutDir/libQt5QmlModels.so.5
rm $OutDir/libk5crypto.so.3
rm $OutDir/libQt5Quick.so.5
rm $OutDir/libQt5Network.so.5
rm $OutDir/libQt5WaylandClient.so.5
rm $OutDir/libkrb5.so.3
rm $OutDir/libkrb5support.so.0
rm $OutDir/libgssapi_krb5.so.2
rm $OutDir/libkeyutils.so.1
rm $OutDir/libQt5WebSockets.so.5
rm $OutDir/lib-dynload/_codecs_jp.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/_codecs_iso2022.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/_codecs_cn.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/_multibytecodec.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/resource.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/_codecs_kr.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/_codecs_tw.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/_json.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/_codecs_hk.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/_queue.cpython-39-x86_64-linux-gnu.so
rm $OutDir/PyQt5/Qt5/plugins/wayland-graphics-integration-client/libvulkan-server.so
rm $OutDir/PyQt5/Qt5/plugins/wayland-graphics-integration-client/libqt-plugin-wayland-egl.so
rm $OutDir/PyQt5/Qt5/plugins/wayland-graphics-integration-client/libdrm-egl-server.so
rm $OutDir/PyQt5/Qt5/plugins/wayland-graphics-integration-client/libxcomposite-glx.so
rm $OutDir/PyQt5/Qt5/plugins/wayland-graphics-integration-client/libdmabuf-server.so
rm $OutDir/PyQt5/Qt5/plugins/wayland-graphics-integration-client/libxcomposite-egl.so
rm $OutDir/PyQt5/Qt5/plugins/wayland-graphics-integration-client/libshm-emulation-server.so
rm $OutDir/PyQt5/Qt5/plugins/wayland-shell-integration/libxdg-shell-v5.so
rm $OutDir/PyQt5/Qt5/plugins/wayland-shell-integration/libwl-shell.so
rm $OutDir/PyQt5/Qt5/plugins/wayland-shell-integration/libxdg-shell-v6.so
rm $OutDir/PyQt5/Qt5/plugins/wayland-shell-integration/libxdg-shell.so
rm $OutDir/PyQt5/Qt5/plugins/wayland-shell-integration/libfullscreen-shell-v1.so
rm $OutDir/PyQt5/Qt5/plugins/wayland-shell-integration/libivi-shell.so
rm $OutDir/PyQt5/Qt5/plugins/generic/libqevdevtouchplugin.so
rm $OutDir/PyQt5/Qt5/plugins/generic/libqtuiotouchplugin.so
rm $OutDir/PyQt5/Qt5/plugins/generic/libqevdevtabletplugin.so
rm $OutDir/PyQt5/Qt5/plugins/generic/libqevdevkeyboardplugin.so
rm $OutDir/PyQt5/Qt5/plugins/generic/libqevdevmouseplugin.so
rm $OutDir/PyQt5/Qt5/plugins/xcbglintegrations/libqxcb-egl-integration.so
rm $OutDir/PyQt5/Qt5/plugins/egldeviceintegrations/libqeglfs-x11-integration.so
rm $OutDir/PyQt5/Qt5/plugins/egldeviceintegrations/libqeglfs-emu-integration.so
rm $OutDir/PyQt5/Qt5/plugins/egldeviceintegrations/libqeglfs-kms-egldevice-integration.so
rm $OutDir/PyQt5/Qt5/plugins/wayland-decoration-client/libbradient.so
rm $OutDir/PyQt5/Qt5/plugins/platforminputcontexts/libibusplatforminputcontextplugin.so
rm $OutDir/PyQt5/Qt5/plugins/platforms/libqeglfs.so
rm $OutDir/PyQt5/Qt5/plugins/platforms/libqwayland-generic.so
rm $OutDir/PyQt5/Qt5/plugins/platforms/libqvnc.so
rm $OutDir/PyQt5/Qt5/plugins/platforms/libqminimal.so
rm $OutDir/PyQt5/Qt5/plugins/platforms/libqwayland-xcomposite-egl.so
rm $OutDir/PyQt5/Qt5/plugins/platforms/libqwayland-xcomposite-glx.so
rm $OutDir/PyQt5/Qt5/plugins/platforms/libqwebgl.so
rm $OutDir/PyQt5/Qt5/plugins/platforms/libqoffscreen.so
rm $OutDir/PyQt5/Qt5/plugins/platforms/libqminimalegl.so
rm $OutDir/PyQt5/Qt5/plugins/platforms/libqlinuxfb.so
rm $OutDir/PyQt5/Qt5/plugins/platforms/libqwayland-egl.so
rm $OutDir/PyQt5/Qt5/plugins/platformthemes/libqxdgdesktopportal.so
rm $OutDir/libgmodule-2.0.so.0
rm $OutDir/libxcb-render-util.so.0
rm $OutDir/libXdamage.so.1
rm $OutDir/libdatrie.so.1
rm $OutDir/libpcre.so.3
rm $OutDir/libblkid.so.1
rm $OutDir/libfreetype.so.6
rm $OutDir/libXrandr.so.2
rm $OutDir/libxcb-shm.so.0
rm $OutDir/libfontconfig.so.1
rm $OutDir/libselinux.so.1
rm $OutDir/liblz4.so.1
rm $OutDir/libssl.so.1.1
rm $OutDir/libxkbcommon-x11.so.0
rm $OutDir/libXcomposite.so.1
rm $OutDir/libbsd.so.0
rm $OutDir/libsystemd.so.0
rm $OutDir/libgthread-2.0.so.0
rm $OutDir/libxcb-glx.so.0
rm $OutDir/libatspi.so.0
rm $OutDir/libepoxy.so.0
rm $OutDir/libgtk-3.so.0
rm $OutDir/libthai.so.0
rm $OutDir/libgdk-3.so.0
rm $OutDir/libgio-2.0.so.0
rm $OutDir/libpangoft2-1.0.so.0
rm $OutDir/libexpat.so.1
rm $OutDir/libfribidi.so.0
rm $OutDir/libpango-1.0.so.0
rm $OutDir/libgobject-2.0.so.0
rm $OutDir/libXcursor.so.1
rm $OutDir/libpcre2-8.so.0
rm $OutDir/libXrender.so.1
rm $OutDir/libpangocairo-1.0.so.0
rm $OutDir/libgcc_s.so.1
rm $OutDir/libxcb-sync.so.1
rm $OutDir/libXext.so.6
rm $OutDir/libxkbcommon.so.0
rm $OutDir/libbz2.so.1.0
rm $OutDir/libuuid.so.1
rm $OutDir/libXi.so.6
rm $OutDir/libz.so.1
rm $OutDir/libstdc++.so.6
rm $OutDir/libxcb-image.so.0
rm $OutDir/libharfbuzz.so.0
rm $OutDir/libdbus-1.so.3
rm $OutDir/libgcrypt.so.20
rm $OutDir/libxcb-keysyms.so.1
rm $OutDir/libxcb-xkb.so.1
rm $OutDir/libxcb-xfixes.so.0
rm $OutDir/libwayland-client.so.0
rm $OutDir/libxcb-randr.so.0
rm $OutDir/libpixman-1.so.0
rm $OutDir/libwayland-cursor.so.0
rm $OutDir/libglib-2.0.so.0
rm $OutDir/libXau.so.6
rm $OutDir/libgraphite2.so.3
rm $OutDir/libcairo-gobject.so.2
rm $OutDir/libwayland-egl.so.1
rm $OutDir/libxcb-xinerama.so.0
rm $OutDir/libxcb-util.so.1
rm $OutDir/libatk-bridge-2.0.so.0
rm $OutDir/libX11-xcb.so.1
rm $OutDir/libxcb-render.so.0
rm $OutDir/libXdmcp.so.6
rm $OutDir/libXinerama.so.1
rm $OutDir/libcairo.so.2
rm $OutDir/liblzma.so.5
rm $OutDir/libgdk_pixbuf-2.0.so.0
rm $OutDir/libxcb-icccm.so.4
rm $OutDir/libpng16.so.16
rm $OutDir/libX11.so.6
rm $OutDir/libgpg-error.so.0
rm $OutDir/libmount.so.1
rm $OutDir/libxcb-shape.so.0
rm $OutDir/libXfixes.so.3
rm $OutDir/libcrypto.so.1.1
rm $OutDir/libatk-1.0.so.0
rm $OutDir/lib-dynload/_opcode.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/_ssl.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/_uuid.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/termios.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/_ctypes.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/_hashlib.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/_decimal.cpython-39-x86_64-linux-gnu.so
rm $OutDir/lib-dynload/_bz2.cpython-39-x86_64-linux-gnu.so
rm $OutDir/yaml/_yaml.cpython-39-x86_64-linux-gnu.so
rm $OutDir/PyQt5/Qt5/plugins/iconengines/libqsvgicon.so
rm $OutDir/PyQt5/Qt5/plugins/imageformats/libqjpeg.so
rm $OutDir/PyQt5/Qt5/plugins/imageformats/libqwebp.so
rm $OutDir/PyQt5/Qt5/plugins/imageformats/libqgif.so
rm $OutDir/PyQt5/Qt5/plugins/imageformats/libqtga.so
rm $OutDir/PyQt5/Qt5/plugins/imageformats/libqico.so
rm $OutDir/PyQt5/Qt5/plugins/imageformats/libqwbmp.so
rm $OutDir/PyQt5/Qt5/plugins/imageformats/libqtiff.so
rm $OutDir/PyQt5/Qt5/plugins/imageformats/libqicns.so
rm $OutDir/PyQt5/Qt5/plugins/xcbglintegrations/libqxcb-glx-integration.so
rm $OutDir/PyQt5/Qt5/plugins/platforminputcontexts/libcomposeplatforminputcontextplugin.so
rm $OutDir/PyQt5/Qt5/plugins/platformthemes/libqgtk3.so


echo "Strip files"
strip -s $OutDir/libicui18n.so.56
strip -s $OutDir/libffi.so.7
strip -s $OutDir/libQt5Widgets.so.5
strip -s $OutDir/libQt5Svg.so.5
strip -s $OutDir/libicudata.so.56
strip -s $OutDir/libicuuc.so.56
strip -s $OutDir/libQt5Core.so.5
strip -s $OutDir/libpython3.9.so.1.0
strip -s $OutDir/libQt5DBus.so.5
strip -s $OutDir/libQt5XcbQpa.so.5
strip -s $OutDir/libQt5Gui.so.5
strip -s $OutDir/lib-dynload/_lzma.cpython-39-x86_64-linux-gnu.so
strip -s $OutDir/lib-dynload/_contextvars.cpython-39-x86_64-linux-gnu.so
strip -s $OutDir/pydantic_core/_pydantic_core.cpython-39-x86_64-linux-gnu.so
strip -s $OutDir/PyQt5/QtGui.abi3.so
strip -s $OutDir/PyQt5/QtWidgets.abi3.so
strip -s $OutDir/PyQt5/QtCore.abi3.so
strip -s $OutDir/PyQt5/sip.cpython-39-x86_64-linux-gnu.so
strip -s $OutDir/PyQt5/Qt5/plugins/imageformats/libqsvg.so
strip -s $OutDir/PyQt5/Qt5/plugins/platforms/libqxcb.so
strip -s $OutDir/galog

echo "Done"
