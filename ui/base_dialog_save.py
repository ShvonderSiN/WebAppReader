from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QDialogButtonBox
from PyQt6.QtGui import QIcon
import os

from constants import *

HEIGHT = 40
WEIGHT = 40


class BaseDialogSave(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        # Создание и стилизация кнопок диалога
        self.yes_icon = QIcon(os.path.join(BASE_DIR, SOURCES_FOLDER, SAVE_ICON))
        self.cancel_icon = QIcon(os.path.join(BASE_DIR, SOURCES_FOLDER, CANCEL_ICON))

        self.save_button = QPushButton()
        self.save_button.setFixedSize(QSize(WEIGHT, HEIGHT))
        self.cancel_button = QPushButton()
        self.cancel_button.setFixedSize(WEIGHT, HEIGHT)
        self.save_button.setIcon(self.yes_icon)
        self.save_button.setIconSize(self.save_button.size())
        self.save_button.setFlat(True)
        self.save_button.setEnabled(False)
        self.cancel_button.setIcon(self.cancel_icon)
        self.cancel_button.setIconSize(self.cancel_button.size())
        self.cancel_button.setFlat(True)

        self.dialog_box = QDialogButtonBox()
        self.dialog_box.setContentsMargins(30, 30, 30, 0)
        self.dialog_box.addButton(self.save_button, QDialogButtonBox.ButtonRole.AcceptRole)
        self.dialog_box.addButton(self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.dialog_box)
        self.setLayout(self.layout)



