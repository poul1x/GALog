from contextlib import contextmanager

from PySide6.QtWidgets import QWidget


@contextmanager
def blockSignals(widget: QWidget):
    try:
        widget.blockSignals(True)
        yield
    finally:
        widget.blockSignals(False)
