import os


STYLES_DIR = os.path.join("assets", "styles")
HIGHLIGHTING_RULES_FILE = os.path.join("config", "highlighting_rules.yaml")

def imageFile(name: str):
    return os.path.join("assets", "images", name + ".png")

def iconFile(name: str):
    return os.path.join("assets", "icons", name + ".svg")

def stringsFile(lang: str):
    return os.path.join("config", "strings", lang + ".yaml")