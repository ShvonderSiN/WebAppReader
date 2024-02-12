from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QWidget

from constants import *


class SearchWidget(QWidget):

    next_search_signal = pyqtSignal()
    previous_search_signal = pyqtSignal()
    perform_search_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.browser = parent
        layout = QHBoxLayout(self)

        self.prev_button = QPushButton(self)
        down_icon = QIcon(os.path.join(BASE_DIR, SOURCES_FOLDER, UP_ICON))
        self.prev_button.setIcon(down_icon)
        self.prev_button.setFlat(True)
        self.prev_button.clicked.connect(self.previous_search_signal.emit)
        layout.addWidget(self.prev_button)

        self.next_button = QPushButton(self)
        up_icon = QIcon(os.path.join(BASE_DIR, SOURCES_FOLDER, DOWN_ICON))
        self.next_button.setIcon(up_icon)
        self.next_button.setFlat(True)
        self.next_button.clicked.connect(self.next_search_signal.emit)
        layout.addWidget(self.next_button)

        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("START TYPING")
        self.search_box.textChanged.connect(
            lambda: self.perform_search_signal.emit(self.search_box.text())
        )
        layout.addWidget(self.search_box)

        layout.setStretch(2, 2)
        layout.setContentsMargins(0, 0, 0, 0)
        self.hide()
