These files were updated manually and have more accurate type hints for PySide6

Backup commands:

```shell
cp ./venv/Lib/site-packages/PySide6/QtCore.pyi ./pyi
cp ./venv/Lib/site-packages/PySide6/QtGui.pyi ./pyi
cp ./venv/Lib/site-packages/PySide6/QtWidgets.pyi ./pyi
```

Restore commands:

```shell
cp ./pyi/QtCore.pyi ./venv/Lib/site-packages/PySide6
cp ./pyi/QtGui.pyi ./venv/Lib/site-packages/PySide6
cp ./pyi/QtWidgets.pyi ./venv/Lib/site-packages/PySide6
```