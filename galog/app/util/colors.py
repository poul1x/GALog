from PyQt5.QtGui import QColor


def rowSelectedColor():
    return QColor("#EBF8FF")


def logLevelColor(logLevel: str):
    if logLevel == "F":
        return QColor("#ffa8ae")
    elif logLevel == "E":
        return QColor("#ffa8ae")
    elif logLevel == "W":
        return QColor("#ffdd7f")
    elif logLevel == "I":
        return QColor("#c7cfff")
    elif logLevel == "V":
        return QColor("#ffc27a")
    elif logLevel == "D":
        return QColor("#99cc99")
    else:  # logLevel == "S":
        return QColor("#EEEEEE")


def logLevelColorDarker(logLevel: str):
    if logLevel == "F":
        return QColor("#DF7C7C")
    elif logLevel == "E":
        return QColor("#DF7C7C")
    elif logLevel == "W":
        return QColor("#AC8F3D")
    elif logLevel == "I":
        return QColor("#6D72B7")
    elif logLevel == "V":
        return QColor("#B7965D")
    elif logLevel == "D":
        return QColor("#66A262")
    else:  # logLevel == "S":
        return QColor("#838383")
