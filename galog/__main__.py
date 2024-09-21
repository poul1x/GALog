from galog.app import runApp
import os

# Disable PyQt6 high dpi scaling
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

if __name__ == "__main__":
    runApp()
