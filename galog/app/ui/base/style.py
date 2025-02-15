from PyQt5.QtWidgets import QProxyStyle, QStyle


class GALogStyle(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget):
        if element == QStyle.PE_FrameFocusRect:
            # Do not draw the focus frame (dots) around selected items
            return
        super().drawPrimitive(element, option, painter, widget)
