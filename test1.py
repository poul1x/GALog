from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys


import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QListView,
    QVBoxLayout,
    QWidget,
    QLabel,
    QHBoxLayout,
    QSpinBox,
)
from PyQt5.QtCore import QIdentityProxyModel, QStringListModel, QModelIndex, Qt


class SliceProxyModel(QIdentityProxyModel):

    def rowCount(self, parent=QModelIndex()):
        if not self.sourceModel():
            return 0
        return self._row_max - self._row_min

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= self._row_max:
            return None

        source_index = self.mapToSource(index)
        return self.sourceModel().data(source_index, role)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        return (
            self.sourceModel().headerData(section, orientation, role)
            if self.sourceModel()
            else None
        )

    def mapToSource(self, proxyIndex):
        real_row = self._row_min + proxyIndex.row()
        if not proxyIndex.isValid() or real_row >= self._row_max:
            return QModelIndex()

        return self.sourceModel().index(real_row, proxyIndex.column())

    def __init__(self, parent=None):
        super().__init__(parent)
        self._row_min = 0
        self._row_max = 0

    def setVisibleRowCount(self, count):
        self.layoutAboutToBeChanged.emit()
        self._row_max = self._row_min + count
        self.layoutChanged.emit()

    def pageSize(self):
        return self._row_max - self._row_min

    # def currentPage(self):
    #     return self.sourceModel().rowCount() / self.pageSize()

    # def currentRow(self):
    #     return self.sourceModel().rowCount() % self.pageSize()

    def moveSlice(self, n):
        if self._row_min + n < 0:
            assert False, "less 0"

        if self._row_max + n > self.sourceModel().rowCount():
            assert False, "more than max"

        self._row_min += n
        self._row_max += n
        self.layoutChanged.emit()

    def isInFullRange(self, relRow, n):
        if relRow >= self.pageSize():
            assert False, "relRow >= self.pageSize"

        abs_row = self.mapToSource(self.index(relRow, 0)).row() + n
        return abs_row >= 0 and abs_row < self.sourceModel().rowCount()

    def isInSliceRange(self, relRow, n):
        if relRow >= self.pageSize():
            assert False, "relRow >= self.pageSize"

        abs_row = self.mapToSource(self.index(relRow, 0)).row() + n
        return abs_row >= self._row_min and abs_row < self._row_max

    def lastInRange(self, relRow, n):
        if relRow >= self.pageSize():
            assert False, "relRow >= self.pageSize"

        abs_row = self.mapToSource(self.index(relRow, 0)).row()
        abs_row_n = self.mapToSource(self.index(relRow, 0)).row() + n
        if abs_row_n >= self.sourceModel().rowCount():
            return self.sourceModel().rowCount() - 1 - abs_row
        else:
            return n

    def firstInRange(self, relRow, n):
        if relRow >= self.pageSize():
            assert False, "relRow >= self.pageSize"

        abs_row = self.mapToSource(self.index(relRow, 0)).row()
        abs_row_n = self.mapToSource(self.index(relRow, 0)).row() - n
        if abs_row_n < 0:
            return relRow
        else:
            return n

    # def mapFromSource(self, sourceIndex):
    #     rel_row = sourceIndex.row() - self._row_min
    #     if not sourceIndex.isValid() or sourceIndex.row() >= rel_row:
    #         return QModelIndex()
    #     return self.createIndex(rel_row, sourceIndex.column())


class MyListView(QListView):
    def keyPressEvent(self, event: QKeyEvent):
        """Override key press event for custom navigation"""
        if event.key() == Qt.Key_Up:
            self.custom_arrow_up()
            event.accept()
        elif event.key() == Qt.Key_Down:
            self.custom_arrow_down()
            event.accept()
        elif event.key() == Qt.Key_PageUp:
            self.custom_page_up()
            event.accept()
        elif event.key() == Qt.Key_PageDown:
            self.custom_page_down()
            event.accept()
        elif event.key() == Qt.Key_Home:
            self.custom_home()
            event.accept()
        elif event.key() == Qt.Key_End:
            self.custom_end()
            event.accept()
        else:
            # Let the base class handle other keys
            super().keyPressEvent(event)

    def setPageSize(self, pageSize: int):
        self._pageSize = pageSize

    def sliceRangeRow(self, row: int, n: int):
        step = 1 if n < 0 else -1
        for i in range(n, 0, step):
            if self.model().isInSliceRange(row, i):
                return i

        return 0

    def fullRangeRow(self, row: int, n: int):
        step = 1 if n < 0 else -1
        for i in range(n, 0, step):
            if self.model().isInFullRange(row, i):
                return i

        return 0

    def custom_arrow_down(self):
        current_index: QModelIndex = self.currentIndex()
        row = self.currentIndex().row()

        if not current_index.isValid():
            return

        if not self.model().isInFullRange(row, 1):
            return

        if self.model().isInSliceRange(row, 1):
            new_index = self.model().index(row + 1, 0)
            self.setCurrentIndex(new_index)
            return
        else:
            self.model().moveSlice(1)
            new_index = self.model().index(self.model().rowCount() - 1, 0)
            self.setCurrentIndex(new_index)

    def custom_arrow_up(self):
        current_index: QModelIndex = self.currentIndex()
        row = self.currentIndex().row()

        if not current_index.isValid():
            return

        if not self.model().isInFullRange(row, -1):
            return

        if self.model().isInSliceRange(row, -1):
            new_index = self.model().index(row - 1, 0)
            self.setCurrentIndex(new_index)
        else:
            self.model().moveSlice(-1)
            new_index = self.model().index(0, 0)
            self.setCurrentIndex(new_index)

    def custom_page_down(self):
        current_index: QModelIndex = self.currentIndex()
        row = self.currentIndex().row()

        if not current_index.isValid():
            return

        n = self.sliceRangeRow(row, 4)
        if n != 0:
            new_index = self.model().index(row + n, 0)
            self.setCurrentIndex(new_index)
            return

        n = self.fullRangeRow(row, 4)
        if n != 0:
            self.model().moveSlice(n)
            new_index = self.model().index(self.model().rowCount() - 1, 0)
            self.setCurrentIndex(new_index)
            return

    def custom_page_up(self):
        current_index: QModelIndex = self.currentIndex()
        row = self.currentIndex().row()

        if not current_index.isValid():
            return

        n = self.sliceRangeRow(row, -4)
        print(n)
        if n != 0:
            new_index = self.model().index(row + n, 0)
            self.setCurrentIndex(new_index)
            return

        n = self.fullRangeRow(row, -4)
        print(n)
        if n != 0:
            self.model().moveSlice(n)
            new_index = self.model().index(0, 0)
            self.setCurrentIndex(new_index)
            return


class DynamicRowListView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create controls
        control_layout = QHBoxLayout()

        self.calc_button = QPushButton("Calculate Visible Rows")
        self.calc_button.clicked.connect(self.calculate_visible_rows)
        control_layout.addWidget(self.calc_button)

        self.row_label = QLabel("Visible rows: 10")
        control_layout.addWidget(self.row_label)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Create list view
        self.list_view = MyListView()
        layout.addWidget(self.list_view)

        # Sample data
        items = [
            f"Item {i:03d} - Some longer text for testing visibility" for i in range(30)
        ]

        # Create model
        self.model = QStringListModel(items)

        # Create custom filter model
        self.proxy_model = SliceProxyModel()
        self.proxy_model.setSourceModel(self.model)

        # Set proxy model to list view
        self.list_view.setModel(self.proxy_model)
        self.list_view.setPageSize(4)

        # Connect resize event to recalculate visible rows
        self.list_view.resizeEvent = self.list_view_resize_event
        index = self.list_view.model().index(0, 0)
        self.list_view.setCurrentIndex(index)
        selection_model = self.list_view.selectionModel()
        selection_model.select(index, QItemSelectionModel.Select)

        # Window settings
        self.setWindowTitle("Dynamic Visible Row Filter")
        self.setGeometry(300, 300, 500, 400)

    def list_view_resize_event(self, event):
        """Override resize event to recalculate visible rows"""
        super(QListView, self.list_view).resizeEvent(event)
        self.calculate_visible_rows()

    def calculate_visible_rows(self):
        """Calculate how many rows can fit in the visible area"""
        if not self.list_view.model():
            return

        # Get viewport height
        viewport_height = self.list_view.viewport().height()

        # Get row height (approximate)
        font_metrics = QFontMetrics(self.list_view.font())
        row_height = font_metrics.height()

        # Calculate visible rows
        visible_rows = max(1, viewport_height // row_height)

        # Update filter
        self.proxy_model.setVisibleRowCount(visible_rows)
        # top_left = self.model.index(0, 0)
        # bottom_right = self.model.index(self.model.rowCount() - 1, 0)
        # self.model.dataChanged.emit(top_left, bottom_right)

        self.row_label.setText(f"Visible rows: {visible_rows}")


def main():
    app = QApplication(sys.argv)
    window = DynamicRowListView()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
