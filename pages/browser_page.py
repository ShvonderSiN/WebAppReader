import os
from datetime import datetime
from pathlib import Path

import requests
from PyQt6 import QtCore
from PyQt6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineProfile,
    QWebEngineSettings,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QMenu, QVBoxLayout, QWidget

from constants import APP_DATA_FOLDER, APP_TITLE, EASY_LIST, EASY_LIST_URL
from settings import settings
from ui.browser_bottom_menu import BottomBrowserMenu


class AdBlockingWebEnginePage(QWebEnginePage):
    OFFLINE: bool = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.your_blocked_domains_list: set = self.use_easy_list() or set()

    def use_easy_list(self):
        if not os.path.exists(EASY_LIST) or self.check_last_update(EASY_LIST):
            self.download_file(EASY_LIST_URL, EASY_LIST)
        return self.open_easy_list_file(EASY_LIST)

    @staticmethod
    def open_easy_list_file(file: str) -> set:
        try:
            with open(
                file,
                "r",
                encoding="utf-8",
            ) as f:
                your_blocked_domains_list = set(f.read().splitlines())
                return your_blocked_domains_list
        except FileNotFoundError:
            return set()

    @staticmethod
    def download_file(url: str, path: str):
        try:
            # Скачиваем файл
            response = requests.get(url)
            response.raise_for_status()  # Если статус не 200, то исключение

            # Сохраняем файл
            with open(path, "w") as file:
                file.write(response.text)

        except requests.exceptions.RequestException:
            return

    @staticmethod
    def check_last_update(file: str) -> bool:
        if os.path.exists(file):
            last_update = datetime.fromtimestamp(os.path.getmtime(file))
            now = datetime.now()
            if (now - last_update).days >= 1:
                return True
        return False

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if url.host() in self.your_blocked_domains_list:
            return False  # Блокировать запрос
        if not AdBlockingWebEnginePage.OFFLINE:
            return True  # Продолжить загрузку страницы
        if not url.isLocalFile():
            return False  # Блокировать запрос, если это не локальный файл
        return True  # Продолжить загрузку страницы


class MyWebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.context_menu = None
        self.menu_position = None

    def contextMenuEvent(self, event):
        self.menu_position = event.globalPos()  # Сохраняем позицию клика
        self.page().runJavaScript(
            "document.activeElement.tagName", self.show_context_menu
        )

    def show_context_menu(self, result):
        self.context_menu = QMenu(self)

        if self.page().selectedText():
            self.context_menu.addAction(
                self.page().action(QWebEnginePage.WebAction.Copy)
            )

        if result == "A":
            self.context_menu.addAction(
                self.page().action(QWebEnginePage.WebAction.CopyLinkToClipboard)
            )

        if not self.page().selectedText() and result != "A":
            self.context_menu.addAction(
                self.page().action(QWebEnginePage.WebAction.Reload)
            )

        self.context_menu.exec(self.menu_position)


class Browser(QWidget):
    """
    Класс браузера просмотрщика веб-страниц.
    """

    def __init__(self, parent: QWidget = None, url=""):
        super().__init__(parent=parent)

        self.url = url
        self.home = url
        self.site_id = None
        self.old_page = None
        self.main_page = parent
        AdBlockingWebEnginePage.OFFLINE = (
            self.main_page.main.top_ui.offline_checkbox.isChecked()
        )

        self.browser = MyWebEngineView(self)
        self.browser.showMaximized()

        self.profile = QWebEngineProfile("myProfile", self)
        profile_path = Path(APP_DATA_FOLDER) / APP_TITLE / "myProfile"
        profile_path.mkdir(parents=True, exist_ok=True)
        self.profile.setPersistentStoragePath(str(profile_path))

        self.set_ = self.browser.page().settings()
        self.set_.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False
        )
        self.set_.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, False
        )
        self.set_.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.set_.setAttribute(
            QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True
        )
        self.set_.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        self.set_.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        # settings.setAttribute(QWebEngineCookieStore.loadAllCookies, True)
        self.set_.setAttribute(
            QWebEngineSettings.WebAttribute.LocalStorageEnabled, True
        )
        self.set_.setAttribute(
            QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True
        )
        self.set_.setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        self.set_.setAttribute(
            QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True
        )
        # self.disconnect(state=True)

        self.old_page = None
        self.new_page = None

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.browser)
        self.bottom_menu = BottomBrowserMenu(parent=self)
        layout.addWidget(self.bottom_menu)
        layout.setStretch(0, 1)

        self.__signals()
        self.set_url(url=self.url)

    def __signals(self):
        self.bottom_menu.search_widget.next_search_signal.connect(self.find_next)
        self.bottom_menu.search_widget.previous_search_signal.connect(self.find_prev)
        self.bottom_menu.search_widget.perform_search_signal.connect(
            self.perform_search
        )
        self.main_page.main.top_ui.offline_signal.connect(self.isOffline)

    @QtCore.pyqtSlot(bool, name="offline_signal")
    def isOffline(self):
        AdBlockingWebEnginePage.OFFLINE = (
            self.main_page.main.top_ui.offline_checkbox.isChecked()
        )

    def __handle_full_screen_requested(self, request):
        if request.toggleOn():
            self.main_page.showFullScreen()
            self.browser.page().showFullScreen()  # Переход в полноэкранный режим
            request.accept()
        else:
            self.browser.page().showNormal()  # Возврат к обычному режиму
            request.accept()

    @QtCore.pyqtSlot(str, name="perform_search")
    def perform_search(self, text: str):
        self.browser.findText(text)

    @QtCore.pyqtSlot(name="find_next")
    def find_next(self):
        self.browser.findText(self.bottom_menu.search_widget.search_box.text())

    @QtCore.pyqtSlot(name="find_prev")
    def find_prev(self):
        self.browser.findText(
            self.bottom_menu.search_widget.search_box.text(),
            QWebEnginePage.FindFlag.FindBackward,
        )

    def set_url(self, url, site_id: int = None, home_page: str = "") -> None:
        self.site_id = site_id

        self.new_page = AdBlockingWebEnginePage(self.profile, self.browser)
        self.new_page.loadFinished.connect(self.__path_viewer_handler)
        self.new_page.fullScreenRequested.connect(self.__handle_full_screen_requested)

        if self.old_page:
            self.browser.setPage(self.new_page)
            self.old_page.deleteLater()
            self.old_page = None

        self.old_page = self.new_page
        if os.path.isfile(url):
            path = Path(url).resolve()
            self.url = path.as_uri()
            self.browser.setUrl(QtCore.QUrl(self.url))
        else:
            self.url = url
            self.browser.setUrl(QtCore.QUrl(url))
        self.bottom_menu.search_box_activate(exit_=True)
        if home_page:
            self.home = home_page
        self.main_page.main.top_ui.path_viewer.setText(
            self.__new_path(self.browser.url().toString())
        )

    def go_home(self) -> None:
        if self.home:
            self.browser.setUrl(QtCore.QUrl(self.home))
        else:
            self.browser.setUrl(QtCore.QUrl(self.url))

    def keyPressEvent(self, event):
        if (
            event.key() == QtCore.Qt.Key.Key_F
            and event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier
        ):
            self.bottom_menu.search_box_activate()

    def __new_path(self, original_path) -> str:
        if not original_path:
            return str()
        path = Path(original_path).parts[-3:]
        new_path = str()
        if path:
            if "http" in path[0]:
                new_path = "/".join(path[1:])
            else:
                new_path = "/".join(path)
        return new_path

    def __path_viewer_handler(self):
        original_path = self.browser.url().toString()
        if settings.contains(f"Browser_last_path/{str(self.site_id)}"):
            if (
                settings.value(f"Browser_last_path/{str(self.site_id)}")
                != original_path
                and "" != original_path
            ):

                if "blank" not in original_path:
                    settings.setValue(
                        f"Browser_last_path/{str(self.site_id)}",
                        self.browser.url().toString(),
                    )
                new_path = self.__new_path(original_path)
                self.main_page.main.top_ui.path_viewer.setText(new_path)

        else:
            ...

    def __str__(self):
        return "browser"
