from PySide6.QtWidgets import QProxyStyle, QStyle


class CustomStyle(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget):
        if element == QStyle.PE_FrameFocusRect:
            # Do not draw the focus frame (dots) around selected items
            return
        super().drawPrimitive(element, option, painter, widget)
