import os


def stylesPath():
    return os.path.join("resources", "styles")


def iconPath(iconName: str):
    return os.path.join("resources", "icons", iconName + ".svg")
