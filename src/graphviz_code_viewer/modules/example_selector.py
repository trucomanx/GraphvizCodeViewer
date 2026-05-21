#!/usr/bin/python3

import os

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QSpinBox,
    QWidget,
    QSizePolicy
)

from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtCore import Qt, QSize, QRectF, QTimer
from PyQt5.QtSvg import QSvgRenderer

# ------------------------------------------------------------
# SVG thumbnail helper
# ------------------------------------------------------------

def svg_to_pixmap(svg_path, width=180, height=140):

    renderer = QSvgRenderer(svg_path)

    default_size = renderer.defaultSize()

    if default_size.width() <= 0 or default_size.height() <= 0:
        default_size = QSize(100, 100)

    # calcula escala preservando aspect ratio
    scale = min(
        width / default_size.width(),
        height / default_size.height()
    )

    new_width = int(default_size.width() * scale)
    new_height = int(default_size.height() * scale)

    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)

    # centraliza
    x = (width - new_width) // 2
    y = (height - new_height) // 2

    renderer.render(
        painter,
        QRectF(x, y, new_width, new_height)
    )

    painter.end()

    return pixmap

# ------------------------------------------------------------
# Main dialog
# ------------------------------------------------------------

class ExampleSelectorDialog(QDialog):

    def __init__(self, dir_base, parent=None):
        super().__init__(parent)

        self.dir_base = os.path.abspath(dir_base)
        self.selected_svg = None

        self.setWindowTitle("Select example")
        self.resize(1100, 700)

        self.main_layout = QVBoxLayout(self)

        # ----------------------------------------------------
        # top controls
        # ----------------------------------------------------

        controls_layout = QHBoxLayout()

        label = QLabel("Columns:")
        self.columns_spin = QSpinBox()
        self.columns_spin.setMinimum(1)
        self.columns_spin.setMaximum(12)
        self.columns_spin.setValue(4)

        self.columns_spin.valueChanged.connect(self.update_grid_size)

        controls_layout.addWidget(label)
        controls_layout.addWidget(self.columns_spin)
        controls_layout.addStretch()

        self.main_layout.addLayout(controls_layout)

        # ----------------------------------------------------
        # list widget
        # ----------------------------------------------------

        self.list_widget = QListWidget()

        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setMovement(QListWidget.Static)

        self.list_widget.setSpacing(16)

        self.list_widget.setSelectionMode(QListWidget.SingleSelection)

        self.list_widget.itemDoubleClicked.connect(self.accept)

        self.main_layout.addWidget(self.list_widget)

        # ----------------------------------------------------
        # buttons
        # ----------------------------------------------------

        buttons_layout = QHBoxLayout()

        buttons_layout.addStretch()

        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)

        self.main_layout.addLayout(buttons_layout)

        # load content
        self.populate()

        # initial grid update
        QTimer.singleShot(0, self.update_grid_size)
    # --------------------------------------------------------

    def populate(self):

        self.list_widget.clear()

        if not os.path.isdir(self.dir_base):
            return

        files = sorted(os.listdir(self.dir_base))

        for filename in files:

            if not filename.lower().endswith(".svg"):
                continue

            svg_path = os.path.join(self.dir_base, filename)

            item = QListWidgetItem()

            item.setText(os.path.splitext(filename)[0])

            item.setData(Qt.UserRole, svg_path)

            item.setTextAlignment(Qt.AlignCenter)

            self.list_widget.addItem(item)
    # --------------------------------------------------------

    def update_grid_size(self):

        columns = self.columns_spin.value()

        viewport_width = self.list_widget.viewport().width()

        spacing = self.list_widget.spacing()

        total_spacing = spacing * (columns + 1)

        cell_width = int((viewport_width - total_spacing) / columns)

        cell_width = max(140, cell_width)

        thumbnail_width = cell_width - 20
        thumbnail_height = int(cell_width * 0.75)

        icon_size = QSize(
            thumbnail_width,
            thumbnail_height
        )

        grid_size = QSize(
            cell_width,
            thumbnail_height + 50
        )

        self.list_widget.setIconSize(icon_size)
        self.list_widget.setGridSize(grid_size)

        # ----------------------------------------------------
        # regenerate thumbnails
        # ----------------------------------------------------

        for i in range(self.list_widget.count()):

            item = self.list_widget.item(i)

            svg_path = item.data(Qt.UserRole)

            pixmap = svg_to_pixmap(
                svg_path,
                width=thumbnail_width,
                height=thumbnail_height
            )

            item.setIcon(QIcon(pixmap))
    # --------------------------------------------------------

    def resizeEvent(self, event):

        super().resizeEvent(event)

        self.update_grid_size()

    # --------------------------------------------------------

    def get_selected_dot_path(self):

        item = self.list_widget.currentItem()

        if item is None:
            return ""

        svg_path = item.data(Qt.UserRole)

        dot_path = os.path.splitext(svg_path)[0] + ".dot"

        return dot_path


# ------------------------------------------------------------
# public function
# ------------------------------------------------------------

def open_window_example_selector(dir_base, parent=None):

    dialog = ExampleSelectorDialog(
        dir_base=dir_base,
        parent=parent
    )

    result = dialog.exec_()

    if result == QDialog.Accepted:
        return dialog.get_selected_dot_path()

    return ""
