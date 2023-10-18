from PyQt5.QtGui import QColor

def logLevelColor(logLevel: str):
    if logLevel == "S":
        color = QColor("#CECECE")
        color.setAlphaF(0.4)
    elif logLevel == "F":
        color = QColor("#FF2635")
        color.setAlphaF(0.4)
    elif logLevel == "E":
        color = QColor("#FF2635")
        color.setAlphaF(0.4)
    elif logLevel == "I":
        color = QColor("#C7CFFF")
    elif logLevel == "W":
        color = QColor("#FFBC00")
        color.setAlphaF(0.5)
    elif logLevel == "D":
        color = QColor("green")
        color.setAlphaF(0.4)
    else:  # V
        color = QColor("orange")
        color.setAlphaF(0.4)

    return color
