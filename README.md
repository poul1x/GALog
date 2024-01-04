# GALog - Graphical Android Log

![](/assets/galog.png)

##  [\[Win\]](#windows) [\[Linux\]](#linux--mac) [\[Mac\]](#linux--mac) [\[Docs\]](#documentation)

**GALog** is a GUI program designed to retrieve and display Android log output for a specific app using the ADB server API.

<ins>Features</ins>:
- Nice-looking GUI
- Log output highlighting: additional formatting is applied to enhance log readability (very WIP).
- Live reloading: log output is automatically reloaded upon app restart.
- Ability to save log output to a file and read it later.
- Message filtering based on content.

## Documentation

Documentation can be found [there](link)

## Installation

### Windows

> [!NOTE]  
> Prebuilt executables are available for windows 10 x64 bit on the [releases](https://github.com/poul1x/galog/releases) page.

Clone repository and install dependencies:

```powershell
git clone https://github.com/poul1x/galog.git
cd galog
python3 -m venv venv
.\venv\Scripts\activate.ps1
pip install -r requirements-prod.txt
```

Run galog as a python module:

```powershell
python3 -m galog
```

Optionally, build and run an executable file:

```powershell
pyinstaller --name galog --onefile galog/__main__.py
Copy-Item -Path .\res -Destination .\dist\galog -Recurse
.\dist\galog\galog.exe
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
python3 -m galog
```

Optionally, build and run an executable file:

```bash
pyinstaller --name galog --onefile galog/__main__.py
cp -r ./res -Destination ./dist/galog
./dist/galog/galog
```

## OS support

**Windows**: Main development system. Fast feedback and bug fixes.

**Linux**: Running in vmware. Slow feedback and bug fixes. 

**Mac**: Running in vmware (slow!!!). Slowest feedback and bug fixes. Has UI bugs which won't be fixed in the near future


