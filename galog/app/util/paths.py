import os


STYLES_DIR = os.path.join("assets", "styles")
HIGHLIGHTING_RULES_FILE = os.path.join("config", "highlighting_rules.yaml")

def iconFile(iconName: str):
    return os.path.join("assets", "icons", iconName + ".svg")

def stringsFile(lang: str):
    return os.path.join("config", "strings", lang + ".yaml")