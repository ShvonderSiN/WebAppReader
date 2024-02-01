from PyQt6 import QtCore
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFormLayout,
    QLabel, QFileDialog, QComboBox, QHBoxLayout)

from tools import *
from database.queries import (
    get_categories, submit_new_website, get_single_website,
    update_single_website, delete_category)
import os

from ui.base_dialog_save import BaseDialogSave

HEIGHT = 35
WEIGHT = 40


class AddEditPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.icon = None
        self.main = parent
        self.PAGES = PagesConstants()
        layout = QVBoxLayout(self)
        layout.addStretch(1)

        # form layout
        form_layout = QFormLayout()
        form_layout.setContentsMargins(20, 0, 20, 0)
        form_layout.setSpacing(15)
        self.file_btn = QPushButton()
        open_file_icon = QIcon(os.path.join(BASE_DIR, SOURCES_FOLDER, OPEN_FILE_ICON))
        self.file_btn.setFixedSize(WEIGHT, HEIGHT)
        self.file_btn.setIconSize(self.file_btn.size())
        self.file_btn.setIcon(open_file_icon)
        self.file_btn.setFlat(True)
        self.path_line_edit = QLineEdit()
        self.path_line_edit.setPlaceholderText('<-- Select index.html or paste url link here')
        self.path_line_edit.setFixedHeight(HEIGHT)

        form_layout.addRow(self.file_btn, self.path_line_edit)

        title_label = QLabel('TITLE')
        title_label.setFixedHeight(HEIGHT)
        self.title_line_edit = QLineEdit()
        self.title_line_edit.setFixedHeight(HEIGHT)
        self.title_line_edit.setPlaceholderText('Enter title here')
        form_layout.addRow(title_label, self.title_line_edit)

        icon_label = QLabel('ICON')
        icon_label.setFixedHeight(HEIGHT)
        self.icon_btn = QPushButton()
        self.default_icon = QIcon(os.path.join(BASE_DIR, 'src', NO_IMAGE))
        self.icon_btn.setIcon(self.default_icon)
        self.icon_btn.setFixedSize(WEIGHT, HEIGHT)
        self.icon_btn.setIconSize(self.icon_btn.size())
        form_layout.addRow(icon_label, self.icon_btn)

        category_label = QLabel('CATEGORY')
        category_label.setFixedHeight(HEIGHT)

        # Создаем горизонтальный контейнер
        hbox = QHBoxLayout()

        self.category_combo_box = QComboBox()
        self.category_combo_box.setFixedHeight(HEIGHT)
        self.update_category_combo_box()
        hbox.addWidget(self.category_combo_box)  # Добавляем в контейнер

        self.category_combo_box.currentIndexChanged.connect(self.on_category_combo_box_changed)

        self.remove_cat_btn = QPushButton()
        del_cat_icon = QIcon(os.path.join(BASE_DIR, 'src', REMOVE_ICON))
        self.remove_cat_btn.setIcon(del_cat_icon)
        self.remove_cat_btn.setFixedSize(WEIGHT, HEIGHT)
        self.remove_cat_btn.setIconSize(self.remove_cat_btn.size())
        self.remove_cat_btn.setFlat(True)
        hbox.addWidget(self.remove_cat_btn)  # Добавляем в контейнер
        form_layout.addRow(category_label, hbox)

        self.dialog_box = BaseDialogSave()

        layout.addLayout(form_layout)
        layout.addWidget(self.dialog_box)
        layout.addStretch(1)

        self.file_btn.clicked.connect(self.new_website_dialog)
        self.icon_btn.clicked.connect(self.new_icon_dialog)

        self.dialog_box.save_button.clicked.connect(self.on_yes_clicked)
        self.dialog_box.cancel_button.clicked.connect(self.on_cancel_clicked)

        self.path_line_edit.textChanged.connect(self.__validate_field)
        self.title_line_edit.textChanged.connect(self.__validate_field)

        self.remove_cat_btn.clicked.connect(self.__remove_category)

    def __remove_category(self) -> None:
        """
        Removes the selected category from the category combo
        box and updates the combo box with the latest categories.
        """
        text = self.category_combo_box.currentText()
        if text.lower() != ADD_NEW_CATEGORY_TEXT.lower() and text.lower() != 'no category':
            delete_category(text.capitalize())
        self.update_category_combo_box()

    def showEvent(self, event):
        """Override the showEvent method to return the default icon each time it is displayed."""

        # print(self.parent.CURRENT_PAGE, self.PAGES.ADD_EDIT_PAGE)
        if self.PAGES.EDIT_SITE_ID:
            site = get_single_website(self.PAGES.EDIT_SITE_ID)
            self.path_line_edit.setText(site.url)
            self.title_line_edit.setText(site.title)

            if site.icon:
                self.icon_btn.setIcon(QIcon(site.icon))
                self.icon = site.icon
            if site.category:
                index = self.category_combo_box.findText(site.category.title.upper(), QtCore.Qt.MatchFlag.MatchExactly)
                self.category_combo_box.setCurrentIndex(index)

        elif (self.main.PREVIOUS_PAGE != self.PAGES.NEW_CATEGORY_PAGE
              and self.main.CURRENT_PAGE != self.PAGES.ADD_EDIT_PAGE):

            self.title_line_edit.clear()
            self.path_line_edit.clear()
            self.icon_btn.setIcon(self.default_icon)
            self.update_category_combo_box()

        else:
            if not self.icon:
                self.icon_btn.setIcon(self.default_icon)
            pass

    def on_yes_clicked(self) -> None:
        """
        Executes when the "Yes" button is clicked.

        This function saves the data to the database by calling the private method "__save_to_db()".
        It then updates the main widget to display all websites by calling the "show_all_websites()" method of the parent widget.
        After that, it navigates to a specific page by calling the "go_to()" method of the parent widget.
        Finally, it sets the text of the lower info label to the value of the "COPYRIGHTS" constant.

        """
        self.__save_to_db()
        self.main.main_widget.show_all_websites()
        self.main.go_to()
        self.main.lower_info_label.setText(COPYRIGHTS)

    def on_cancel_clicked(self) -> None:
        """
        Handles the event when the cancel button is clicked.

        This function sets the `EDIT_SITE_ID` attribute of the `PAGES` object to `None`,
        indicating that no site is currently being edited. It then calls the `show_all_websites`
        method of the `main_widget` attribute of the `main` object to display all websites.
        Finally, it calls the `go_back` method of the `main` object to navigate back to the
        previous page.
        """
        self.PAGES.EDIT_SITE_ID = None
        self.main.main_widget.show_all_websites()
        self.main.go_back()

    @QtCore.pyqtSlot(name='file_dialog')
    def new_website_dialog(self) -> None:
        """
        Display a file dialog to select an HTML file for a new website.
        """
        path = QFileDialog().getOpenFileName(self,
                                             caption='Select file',
                                             directory='',
                                             options=QFileDialog.Option.ReadOnly,
                                             filter='Page (*.html *.htm)')[0]
        path = os.path.normpath(path) or None
        if path and os.path.isfile(path):
            self.path_line_edit.setText(path)
            title, self.icon = get_new_title_icon(path)
            self.icon_btn.setIcon(QIcon(self.icon))
            self.title_line_edit.setText(title)
            #  TODO делать фокус на кнопке потом на сейв
            # self.dialog_box.setFocus()

    @QtCore.pyqtSlot(name='icon_dialog')
    def new_icon_dialog(self) -> None:
        """
        Generates a new icon dialog for selecting an image file to be used as the application's icon.
        """
        iconUrl = QFileDialog().getOpenFileName(self,
                                                caption='Open file',
                                                directory='',
                                                filter='Image (*.png *.svg *.jpg *.ico *.gif *.tiff  *.webp)')[0]
        iconUrl = os.path.normpath(iconUrl) or None
        if iconUrl and os.path.isfile(iconUrl):
            pixmap = QPixmap(iconUrl)
            scaled_pixmap = pixmap.scaled(self.icon_btn.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                          QtCore.Qt.TransformationMode.SmoothTransformation)
            self.icon_btn.setIcon(QIcon(scaled_pixmap))
            self.icon = iconUrl

    def update_category_combo_box(self) -> None:
        """
        Updates the category combo box with the categories retrieved from the database.
        """
        self.category_combo_box.clear()
        db_categories = get_categories()
        self.category_combo_box.addItems([cat.title.upper() for cat in db_categories])
        self.category_combo_box.addItem(ADD_NEW_CATEGORY_TEXT)

    def on_category_combo_box_changed(self) -> None:
        """
        A function that is called when the category combo box is changed.

        This function checks if the current text of the category combo box
        is equal to the constant ADD_NEW_CATEGORY_TEXT.
        If it is, it calls the go_to() method of the main object with the argument
        self.PAGES.NEW_CATEGORY_PAGE to navigate to the new category page.
        It then calls the update_category_combo_box() method to update the category combo box.
        """
        if self.category_combo_box.currentText() == ADD_NEW_CATEGORY_TEXT:
            self.main.go_to(self.PAGES.NEW_CATEGORY_PAGE)
            self.update_category_combo_box()

    def __save_to_db(self) -> None:
        """
        Saves the current data to the database.

        This function retrieves the path from the text input field and checks if an icon is available.
        If an icon is not available, it tries to fetch the title and icon using the path.
        If an icon is available, it uses the provided title and icon.
        It also retrieves the selected category from the combo box.

        If the `PAGES.EDIT_SITE_ID` is set, it updates the existing website in the database with the provided information.
        Otherwise, it submits a new website to the database.
        """

        path = self.path_line_edit.text()
        if not self.icon:
            try:
                title, icon = get_new_title_icon(path)
            except Exception:
                title, icon = self.title_line_edit.text(), self.icon
        else:
            title, icon = self.title_line_edit.text(), self.icon
        category_text = self.category_combo_box.currentText().capitalize()

        # Проверка режима
        if self.PAGES.EDIT_SITE_ID:
            update_single_website(
                site_id=self.PAGES.EDIT_SITE_ID,
                title=title, url=path,
                category=category_text, icon=icon
            )
            self.PAGES.EDIT_SITE_ID = None
        else:
            # Режим добавления
            submit_new_website(title=title, url=path, category=category_text, icon=icon)

        self.icon = None

    def __validate_field(self):
        """
        Validates the field inputs by checking if the title text
        and path text are not empty and if the path text is a valid HTML source.
        """
        title_text = self.title_line_edit.text()
        path_text = self.path_line_edit.text()

        if title_text and is_html_source(path_text):
            self.dialog_box.save_button.setEnabled(True)
        else:
            self.dialog_box.save_button.setEnabled(False)
