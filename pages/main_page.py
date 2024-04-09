from collections import defaultdict

from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QGroupBox,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QToolBox,
    QVBoxLayout,
    QWidget,
)

from constants import *
from database.queries import get_all_websites, get_single_website
from pages.browser_page import Browser
from tools import validate_url
from ui.browser_bottom_menu import BottomMainMenu
from ui.row_widget import RowWidget


class MainWidget(QWidget):
    """Виджет каталога"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.main = parent
        self.browser = Browser(self, url="")
        self.PAGES = PagesConstants()
        self.layout = QVBoxLayout(self)
        self.layout.setStretch(1, 1)
        self.layout.setStretch(0, 0)
        self.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)

        self.show_all_websites()

        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)

        if PLATFORM not in ["windows", "linux"]:
            bottom_menu = BottomMainMenu(parent=self)
            self.layout.addWidget(bottom_menu)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def create_website_row_widget(self, site):
        """Создает виджет строки для отдельного веб-сайта."""
        rowBox = RowWidget(id_site=site.id, title=site.title, parent=self)
        rowBox.double_click_signal.connect(
            lambda id_site=site.id: self.open_browser(id_site)
        )

        if not site.icon or not os.path.exists(
            os.path.join(BASE_DIR, SOURCES_FOLDER, site.icon)
        ):
            rowBox.iconWidget.setPixmap(
                QPixmap(os.path.join(BASE_DIR, SOURCES_FOLDER, NO_IMAGE)).scaled(40, 40)
            )
        else:
            rowBox.iconWidget.setPixmap(
                QPixmap(os.path.join(BASE_DIR, SOURCES_FOLDER, site.icon)).scaled(
                    40, 40
                )
            )

        return rowBox

    def create_category_group_box(self, title=None, websites=None):
        """Создает QGroupBox для категории с заданным названием и веб-сайтами."""
        catbox = QGroupBox()
        catbox.setContentsMargins(0, 0, 0, 0)
        catbox.setLayout(QVBoxLayout())
        catbox.setFlat(True)

        if websites:
            for site in websites:
                row_widget = self.create_website_row_widget(site)
                catbox.layout().addWidget(row_widget)

        spacer = QSpacerItem(
            10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        catbox.layout().addItem(spacer)

        return catbox

    def show_all_websites(self) -> None:
        self.clear_layout(self.scroll_layout)

        toolbox = QToolBox()
        toolbox.setStyleSheet(
            """
                    QToolBox::tab {
                        background-color: rgb(255, 255, 255);
                        color: rgb(0, 0, 0);
                        font-size: 16px;
                        max-width: 100%;
                        font-weight: bold;
                    }
                    """
        )
        self.scroll_layout.addWidget(toolbox)

        db_websites = get_all_websites() or []

        if not db_websites:
            catbox = self.create_category_group_box("Have no any sources".upper())
            toolbox.addItem(catbox, "Have no any sources".upper())

        else:
            # Сортируем веб-сайты по категориям
            websites_by_category = defaultdict(list)

            for site in db_websites:
                category_title = site.category.title
                websites_by_category[category_title].append(site)

            # Добавляем общий бокс для всех сайтов
            all_sites_box = self.create_category_group_box("ALL", db_websites)
            toolbox.addItem(all_sites_box, "ALL")

            # выбираю (category_title, обеъект сайта -> sites_in_category.ID) сортирую
            sorted_categories = sorted(
                websites_by_category.items(),
                key=lambda x: x[1][0].category.id,
                reverse=True,
            )

            # Создаем бокс для каждой категории
            for category_title, sites_in_category in sorted_categories:
                category_box = self.create_category_group_box(
                    category_title.upper(), sites_in_category
                )
                toolbox.addItem(category_box, category_title.upper())

    @QtCore.pyqtSlot(name="open_browser")
    def open_browser(self, site_id: int) -> None:
        """
        Open the browser and navigate to a specified website.
        Parameters:
            site_id (int): The ID of the website to navigate to.
        Returns:
            None
        """
        site = get_single_website(site_id=site_id)
        url = site.url

        # тут надо проверить существует ли по пути локальному файл
        if not validate_url(url):

            if PLATFORM == "linux":
                name = url.split("/")
                new_name = "/" + "/".join((name[-3], name[-2], name[-1]))
            elif PLATFORM == "windows":
                name = url.split("\\")
                new_name = "\\" + "\\".join((name[-2], name[-1]))
            else:
                pass
            # new_name = '/' + '/'.join((name[-2], name[-1]))
            self.main.lower_info_label.setText(f"Unable to open {new_name}")

        else:
            self.PAGES.BROWSER_PAGE = self.main.stacked_widget.addWidget(self.browser)
            self.browser.set_url(url)
            self.main.go_to(self.PAGES.BROWSER_PAGE)
            self.browser.show()
            self.main.lower_info_label.setText(COPYRIGHTS)

    def close_browser(self) -> None:
        """
        Close the browser widget and remove it from the stacked widget.
        """
        self.main.go_back()
        self.browser.set_url("")
        self.browser.hide()

    def __str__(self):
        return "main_page"
