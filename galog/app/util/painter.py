from PyQt5.QtGui import QPainter

class PainterStateContextManager:
    def __init__(self, painter: QPainter):
        self.painter = painter

    def __enter__(self):
        self.painter.save()
        return self.painter

    def __exit__(self, *unused):
        self.painter.restore()

def painterSaveRestore(painter: QPainter):
    return PainterStateContextManager(painter)