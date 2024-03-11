import os

from PyQt6 import QtCore
from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from constants import APPLY_ICON, BASE_DIR, CANCEL_ICON

HEIGHT = 40
WEIGHT = 70


class BaseDialogConfirm(QWidget):
    yes_signal = pyqtSignal()
    no_signal = pyqtSignal()

    def __init__(self, text="", parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.text = text.upper() or ""
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel(self.text)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.button_layout = QHBoxLayout()
        self.button_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(self.button_layout)

        self.apply_icon = QIcon(os.path.join(BASE_DIR, "src", APPLY_ICON))
        self.cancel_icon = QIcon(os.path.join(BASE_DIR, "src", CANCEL_ICON))
        self.apply_button = QPushButton()
        self.apply_button.setToolTip("Apply")
        self.cancel_button = QPushButton()
        self.cancel_button.setToolTip("Cancel")

        self.layout.setSpacing(25)

        self.buttons_ui()
        self.signals()

    def buttons_ui(self):
        self.apply_button.setFixedSize(QSize(WEIGHT, HEIGHT))
        # self.apply_button.setDefault(True)
        self.apply_button.setIcon(self.apply_icon)
        self.apply_button.setIconSize(self.apply_button.size())
        self.apply_button.setFlat(True)

        self.cancel_button.setFixedSize(QSize(WEIGHT, HEIGHT))
        self.cancel_button.setIcon(self.cancel_icon)
        self.cancel_button.setIconSize(self.cancel_button.size())
        self.cancel_button.setFlat(True)
        self.cancel_button.setDefault(True)

        self.button_layout.addWidget(self.apply_button)
        self.hidden_label = QLabel("        ")
        self.button_layout.addWidget(self.hidden_label)
        self.button_layout.addWidget(self.cancel_button)

    def signals(self):
        self.apply_button.clicked.connect(self.on_yes_clicked)
        self.cancel_button.clicked.connect(self.on_no_clicked)

    def on_yes_clicked(self):
        """Handle the event when the "yes" button is clicked."""
        self.yes_signal.emit()

    def on_no_clicked(self):
        """Handle the event when the "no" button is clicked."""
        self.no_signal.emit()
