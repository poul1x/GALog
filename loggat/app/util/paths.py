import os


STYLES_DIR = os.path.join("resources", "styles")
HIGHLIGHTING_RULES_FILE = os.path.join("config", "highlighting_rules.yaml")

def iconFile(iconName: str):
    return os.path.join("resources", "icons", iconName + ".svg")
