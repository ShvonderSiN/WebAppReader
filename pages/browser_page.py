import os
from pathlib import Path

from PyQt6 import QtCore
from PyQt6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineProfile,
    QWebEngineSettings,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QMenu, QVBoxLayout, QWidget

from constants import APP_TITLE, EASY_LIST
from settings import app_data_path, settings
from ui.browser_bottom_menu import BottomBrowserMenu


class AdBlockingWebEnginePage(QWebEnginePage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.your_blocked_domains_list = self._get_blocked_domains_list()

    @staticmethod
    def _get_blocked_domains_list():
        with open(
            EASY_LIST,
            "r",
            encoding="utf-8",
        ) as f:
            your_blocked_domains_list = set(f.read().splitlines())
            return your_blocked_domains_list

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if url.host() in self.your_blocked_domains_list:
            return False  # Блокировать запрос
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

    def __init__(self, parent: QWidget = None, url="https://google.com"):
        super().__init__(parent=parent)
        self.url = url
        self.home = url
        self.site_id = None
        self.old_page = None
        self.main_page = parent

        self.browser = MyWebEngineView(self)
        self.browser.showMaximized()

        self.profile = QWebEngineProfile("myProfile", self)
        profile_path = Path(app_data_path) / APP_TITLE / "myProfile"
        profile_path.mkdir(parents=True, exist_ok=True)
        self.profile.setPersistentStoragePath(str(profile_path))

        set_ = self.browser.page().settings()
        set_.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False
        )
        set_.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, False
        )
        set_.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        set_.setAttribute(
            QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True
        )
        set_.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        set_.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        # settings.setAttribute(QWebEngineCookieStore.loadAllCookies, True)
        set_.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        set_.setAttribute(
            QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True
        )
        set_.setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )

        self.old_page = None

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

    def __handle_full_screen_requested(self, request):
        print("Handle full screen requested")  # Отладочный вывод
        if request.toggleOn():
            self.main_page.showFullScreen()
            self.browser.page().showFullScreen()  # Переход в полноэкранный режим
            request.accept()
            print("full screen")
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

        new_page = AdBlockingWebEnginePage(self.profile, self.browser)
        new_page.loadFinished.connect(self.__path_viewer_handler)
        new_page.fullScreenRequested.connect(self.__handle_full_screen_requested)

        if self.old_page:
            self.browser.setPage(new_page)
            self.old_page.deleteLater()
            self.old_page = None

        self.old_page = new_page
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
        path = Path(original_path).parts[-3:]
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
            ):

                if not "blank" in original_path:
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
