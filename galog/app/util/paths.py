import os


FONTS_DIR = os.path.join("res", "fonts")
STYLES_DIR = os.path.join("res", "styles")
HIGHLIGHTING_RULES_FILE = os.path.join("config", "highlighting_rules.yaml")


def styleSheetFile(name: str):
    return os.path.join("res", "styles", "manual", name + ".qss")


def iconFile(name: str):
    return os.path.join("res", "icons", name + ".svg")


def stringsFile(lang: str):
    return os.path.join("config", "strings", lang + ".yaml")
