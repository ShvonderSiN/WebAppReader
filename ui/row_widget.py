from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QSizePolicy

from constants import PagesConstants
from database.queries import delete_website
from settings import settings
from ui.context_menu import ContextMenu


class RowWidget(QtWidgets.QGroupBox):
    """
    Класс RowWidget, как отдельный виджет отрисовки источника из таблицы
    """

    double_click_signal = pyqtSignal(int)
    go_to_signal = pyqtSignal(int)

    def __init__(self, id_site, title, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.title = title  # Сохраняем полный текст здесь
        self.PAGES = PagesConstants()

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.id = id_site

        h_box = QtWidgets.QHBoxLayout(self)
        self.iconWidget = QtWidgets.QLabel("iconLabel")
        h_box.addWidget(self.iconWidget)
        self.nameWidget = QtWidgets.QLabel(self.title, parent=self)
        self.nameWidget.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.nameWidget.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.nameWidget.setMargin(5)
        h_box.addWidget(self.nameWidget, 1)

        h_box.setSpacing(1)
        h_box.setContentsMargins(0, 0, 0, 0)

        self.setFlat(True)
        self.setStyleSheet(
            """
            QGroupBox {
                border: none;  /* Корректно убираем границу */
            }
            """
        )

        self.mouseDoubleClickEvent = self.double_click_event

    def enterEvent(self, event):
        """
        The enterEvent function is called when the user enters an event.
        It sets the flag self.setFlat to False.

        Parameters:
            - event: An object that represents the event that the user is entering.

        Returns:
            None
        """

        self.setFlat(False)
        self.setStyleSheet(
            """
            QGroupBox {
                border: 1px solid #4C4F51;  /* Устанавливаем корректную границу */
            }
            """
        )

    def leaveEvent(self, event):
        """
        The leaveEvent function is called when the user leaves an event.
        It sets the flag self.setFlat to True.

        Parameters:
            - event: An object that represents the event from which the user is leaving.

        Returns:
            None
        """
        self.setFlat(True)
        self.setStyleSheet(
            """
            QGroupBox {
                border: none;  /* Корректно убираем границу */
            }
            """
        )

    def double_click_event(self, event) -> None:
        """
        Обработчик двойного клика мыши, запускает окно просмотра
        :param event: mouse double click
        :return: None
        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.double_click_signal.emit(self.id)

    def contextMenuEvent(self, event):
        contextMenu = ContextMenu(context="row_widget")
        action = contextMenu.exec(event.globalPos())

        if action:
            if action.text() == "EDIT":
                # self.parent.main.add_edit_page.site_id = self.id
                self.PAGES.EDIT_SITE_ID = self.id
                self.parent.main.go_to(self.PAGES.ADD_EDIT_PAGE)
            elif action.text() == "DELETE":
                # deleted_site = delete_website(self.id)
                result = delete_website(self.id)
                if result:
                    settings.remove(f"Browser_last_path/{str(self.id)}")
                    settings.remove(f"Browser_last_path/{str(self.id)}_home")
                # delete_icon(deleted_site.icon)
                # delete_data_from_website(deleted_site.url)
                self.parent.show_all_websites()

    def update_text_nameWidget(self, width):
        elided_text = self.fontMetrics().elidedText(
            self.title, QtCore.Qt.TextElideMode.ElideRight, width - 120
        )
        self.nameWidget.setText(elided_text)
