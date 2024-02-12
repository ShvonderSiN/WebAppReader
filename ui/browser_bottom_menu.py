from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from constants import *
from ui.search_widget import SearchWidget


class BottomMenu(QWidget):

    def __init__(self, parent=None, menu_type="main_window"):
        super().__init__(parent=parent)
        self.nav_layout = QHBoxLayout(self)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)

        if menu_type == "main_window":
            self.create_button(CLOSE_ICON, parent.main.close, self.nav_layout)
        else:
            self.create_button(
                MENU_ICON, parent.main_page.close_browser, self.nav_layout
            )

            self.blank_widget = QWidget()
            self.nav_layout.addWidget(self.blank_widget)
            self.search_widget = SearchWidget(parent=self)
            self.nav_layout.addWidget(self.search_widget)

            self.search_button = self.create_button(
                SEARCH_ICON, self.search_box_activate, self.nav_layout
            )
            self.search_button.setToolTip("CTRL + F")
            self.create_button(BACK_ARROW_ICON, parent.browser.back, self.nav_layout)
            self.create_button(HOME_ICON, parent.go_home, self.nav_layout)
            self.create_button(
                FORWARD_ARROW_ICON, parent.browser.forward, self.nav_layout
            )

            self.nav_layout.setStretch(1, 1)

            if PLATFORM not in ["windows", "linux"]:
                self.create_button(
                    EXIT_ICON, parent.main_page.main_window.close, self.nav_layout
                )

    def create_button(self, icon_name: str, callback, layout, flat=True) -> QPushButton:
        icon = QIcon(os.path.join(BASE_DIR, "src", icon_name))
        btn = QPushButton(self)
        btn.setIcon(icon)
        btn.setFixedSize(30, 30)
        btn.setIconSize(btn.size())
        btn.setFlat(flat)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        return btn

    def search_box_activate(self, exit_=False):
        if self.search_widget.isVisible() or exit_:
            self.search_widget.hide()
            self.blank_widget.show()
            self.search_button.setFlat(True)

        else:
            self.search_widget.show()
            self.blank_widget.hide()
            self.search_widget.setFocus()
            self.search_button.setFlat(False)
            self.search_widget.search_box.setFocus()


class BottomMainMenu(BottomMenu):
    def __init__(self, parent=None):
        super().__init__(parent, menu_type="main_window")


class BottomBrowserMenu(BottomMenu):
    def __init__(self, parent=None):
        super().__init__(parent, menu_type="browser")
