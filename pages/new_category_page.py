from PyQt6 import QtGui
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel, QFormLayout, QLineEdit, QPushButton, \
    QDialogButtonBox

from constants import *
from database.queries import add_new_category, get_categories
from pages.add_edit_page import HEIGHT

import os

from ui.base_dialog_save import BaseDialogSave


class NewCategory(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.PAGES = PagesConstants()
        layout = QVBoxLayout(self)
        layout.addStretch(1)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(30, 0, 30, 0)
        form_layout.setSpacing(10)
        label = QLabel('NEW CATEGORY:')
        self.category_name = QLineEdit()
        form_layout.addRow(label, self.category_name)
        layout.addLayout(form_layout)

        self.dialog_box = BaseDialogSave()
        layout.addWidget(self.dialog_box)

        layout.addStretch(1)

        self.dialog_box.save_button.clicked.connect(self.on_yes_clicked)
        self.dialog_box.cancel_button.clicked.connect(self.on_cancel_clicked)

        self.category_name.textChanged.connect(self.__validate_field)

    def enterEvent(self, event: QtGui.QEnterEvent) -> None:
        # self.PAGES.NEW_CATEGORY_PAGE =
        self.category_name.clear()

    def on_yes_clicked(self):
        self.__save_to_db()
        self.parent.add_edit_page.update_category_combo_box()
        # self.PAGES.
        self.parent.go_back()

    def on_cancel_clicked(self):
        self.parent.go_back()

    def __save_to_db(self):
        category = self.category_name.text()
        if category.lower() in map(lambda x: x.title.lower(), get_categories()):
            pass
        else:
            add_new_category(category.capitalize())


    def __validate_field(self):
        if self.category_name.text():
            self.dialog_box.save_button.setEnabled(True)
        else:
            self.dialog_box.save_button.setEnabled(False)
