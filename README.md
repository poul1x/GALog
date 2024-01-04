# GALog - Graphical Android Log

![](/assets/galog.png)

**GALog** is a GUI program designed to retrieve and display Android log output for a specific app using the ADB server API.

<u>Features</u>:
- Nice-looking GUI
- Log output highlighting: additional formatting is applied to enhance log readability.
- Live reloading: log output is automatically reloaded upon app restart.
- Ability to save log output to a file and read it later.
- Message filtering based on content.

## Local development

### Install and run

Using python 3.7+

```cmd
py -3 -m venv venv
./venv/bin/activate.ps
pip install -r requirements-dev.txt

py -3 main.py
```

TODO

### Code documentation

TODO

### Running tests

TODO

### Spell checking

TODO

### Build

```bash
pyinstaller --onefile "galog\__main__.py"
# Copy logging.yaml
```

### Fonts

Roboto Mono

```
https://github.com/googlefonts/RobotoMono/tree/main/fonts/ttf
```

### VSCode extensions

- `ms-python.python`
- `ms-python.vscode-pylance`
- `streetsidesoftware.code-spell-checker`
- `streetsidesoftware.code-spell-checker-russian`
- `seanwu.vscode-qt-for-python`
