# GALog - Graphical Android Log

![](/assets/galog.gif)

##  [\[Win\]](#windows) [\[Linux\]](#linux--mac) [\[Mac\]](#linux--mac) [\[Docs\]](https://github.com/poul1x/galog/wiki)

**GALog** is a GUI program designed to retrieve and display Android log output for a specific app using the ADB server API.

<ins>Features</ins>:
- Nice-looking GUI
- Log output highlighting: additional formatting is applied to enhance log readability (very WIP).
- Live reloading: log output is automatically reloaded upon app restart.
- Ability to save log output to a file and read it later.
- Message filtering based on content.

## Installation

### Windows

> [!NOTE]
> Prebuilt executables are available for Windows 10 (x64 bit) on the [releases](https://github.com/poul1x/galog/releases) page.

Clone repository and install dependencies with powershell commands:

```powershell
git clone https://github.com/poul1x/galog.git
cd galog
py -3 -m venv venv
.\venv\Scripts\activate.ps1
pip install -r requirements-prod.txt
```

Run galog as a python module:

```powershell
python -m galog
```

Optionally, you can build and run an executable file:

```powershell
pyinstaller --name galog --onefile galog/__main__.py
Copy-Item -Path .\res -Destination .\dist -Recurse
.\dist\galog.exe
```

### Linux & Mac

Clone repository and install dependencies:

```bash
git clone https://github.com/poul1x/galog.git
cd galog
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements-prod.txt
```

Run galog as a python module:

```bash
python -m galog
```

Optionally, you can build and run an executable file:

```bash
pyinstaller --name galog --onefile galog/__main__.py
cp -r ./res -Destination ./dist
./dist/galog
```

## Documentation

Documentation can be found [there](https://github.com/poul1x/galog/wiki)

## OS support

**Windows**: Primary development system for fast feedback and efficient bug fixes.

**Linux**: Development on Linux involves utilizing a hypervisor, leading to slower feedback and bug fixes compared to the Windows environment.

**Mac**: Development on Mac involves utilizing a hypervisor (note: slow performance), resulting in the slowest feedback and bug fixes. Please be aware that there are known UI bugs on the Mac platform, and they may not be addressed in the near future.

