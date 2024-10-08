import os
import sys
from threading import Thread

from PyQt6 import QtCore
from PyQt6.QtGui import QAction, QColor, QIcon, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QStackedWidget,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from constants import (
    APP_ICON,
    APP_TITLE,
    BASE_DIR,
    COPYRIGHTS,
    PLATFORM,
    PagesConstants,
    SOURCES_FOLDER,
    VERSION,
)
from database.database import startup
from pages.add_edit_page import AddEditPage
from pages.download_page import DownloadPage
from pages.error_page import ErrorPage
from pages.exit_page import ExitPage
from pages.main_page import MainWidget
from pages.new_category_page import NewCategory
from settings import settings
from ui.main_top_menu import TopUi
from ui.row_widget import RowWidget


def version_file():
    import pyinstaller_versionfile

    try:
        pyinstaller_versionfile.create_versionfile(
            output_file=os.path.join(BASE_DIR, "version_file.txt"),
            version=VERSION,
            company_name="Sergei Shekin",
            file_description="Offline web content reader",
            internal_name="WebAppReader",
            legal_copyright="© Sergei Shekin. All rights reserved.",
            original_filename="webappreader.exe",
            product_name="WebAppReader",
            translations=[0],
        )
    except FileNotFoundError:
        pass


class MainWindow(QMainWindow):
    """Главное окно"""

    GEOMETRY_SAVED: str = "Window/geometry_saved"
    GEOMETRY: str = "Window/geometry"
    MINIMUM_SIZE: str = "Window/minimumSize"

    def __init__(self, title, icon):
        super().__init__()
        self.title = title
        self.icon = icon

        self.page_history = []
        self.CURRENT_PAGE: None | int = None
        self.PREVIOUS_PAGE: None | int = None

        self.confirm_exit: bool = False
        self.error = None
        self.exit_ = None
        self.main_widget = None
        self.add_page = None
        self.new_category_page = None
        self.PAGES = PagesConstants()

        layout = QVBoxLayout()
        bottom_info_layout = QHBoxLayout()

        self.terminate_btn = QPushButton(text="X")
        self.terminate_btn.hide()
        self.terminate_btn.setStyleSheet(
            """background-color: white;
             color: red; 
             font-weight: bold;"""
        )
        self.terminate_btn.setFixedSize(QtCore.QSize(20, 20))

        self.lower_info_label = QLabel(text=COPYRIGHTS)
        self.lower_info_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
        )

        self.top_ui = TopUi(parent=self)
        layout.addWidget(self.top_ui)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.stacked_widget = QStackedWidget()
        self.stack_pages()
        self.stacked_widget.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked_widget)

        bottom_info_layout.addWidget(self.lower_info_label)
        bottom_info_layout.addWidget(self.terminate_btn)
        layout.addLayout(bottom_info_layout)

        self.__style_ui()

        self.go_to(self.PAGES.MAIN_PAGE)
        self.__signals()

        # self.__system_tray()

    def __system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(os.path.join(BASE_DIR, SOURCES_FOLDER, self.icon)))
        # контекстное меню для иконки трея
        tray_menu = QMenu()

        show_action = QAction("Show", self)
        show_action.triggered.connect(lambda: print("Show"))
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(lambda: print("Hide"))
        add_action = QAction("Add new source", self)
        add_action.triggered.connect(lambda: self.go_to(self.PAGES.ADD_EDIT_PAGE))
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit)
        tray_menu.addActions(
            (
                # show_action,
                # hide_action,
                add_action,
                tray_menu.addSeparator(),
                exit_action,
            )
        )

        # Устанавливаю контекстное меню для иконки трея
        self.tray_icon.setContextMenu(tray_menu)

        if QSystemTrayIcon.isSystemTrayAvailable() and PLATFORM != "android":
            self.tray_icon.show()

    def __style_ui(self):
        # Установка минимального размера окна
        if settings.contains(MainWindow.MINIMUM_SIZE):
            self.setMinimumSize(settings.value(MainWindow.MINIMUM_SIZE))

        # Восстановление геометрии окна
        if settings.contains(MainWindow.GEOMETRY_SAVED):
            self.restoreGeometry(settings.value(MainWindow.GEOMETRY_SAVED))
        elif settings.contains(MainWindow.GEOMETRY):
            self.setGeometry(settings.value(MainWindow.GEOMETRY))

        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR, SOURCES_FOLDER, self.icon)))

        if PLATFORM not in ["windows", "linux"]:
            self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)

        # if PLATFORM not in ['windows', 'linux']:
        #     self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        # self.title_bar = CustomTitleBar(parent=self, title='WebAppReader')
        # self.setMenuWidget(self.title_bar)

    def __signals(self) -> None:
        self.exit_.exit_signal.connect(self.exit)
        self.exit_.back_signal.connect(self.go_back)

        self.error.back_signal.connect(self.go_back)

        self.top_ui.go_to_add_page_signal.connect(self.go_to)
        self.top_ui.go_to_download_page_signal.connect(self.go_to)
        self.top_ui.on_top_signal.connect(self.on_top)

    def stack_pages(self) -> None:
        self.main_widget = MainWidget(parent=self)  # Main widget page
        self.exit_ = ExitPage(parent=self, text="Are you sure you want to exit?")
        self.error = ErrorPage(
            parent=self, text="Error"
        )  # TODO прикрутить сюда варнинги
        self.add_edit_page = AddEditPage(parent=self)  # Add page
        self.new_category_page = NewCategory(parent=self)

        # Add the widget pages to the stacked widget and store their indexes
        self.PAGES.MAIN_PAGE = self.stacked_widget.addWidget(self.main_widget)
        self.PAGES.EXIT_PAGE = self.stacked_widget.addWidget(self.exit_)
        self.PAGES.ERROR_PAGE = self.stacked_widget.addWidget(self.error)
        self.PAGES.ADD_EDIT_PAGE = self.stacked_widget.addWidget(self.add_edit_page)
        self.PAGES.NEW_CATEGORY_PAGE = self.stacked_widget.addWidget(
            self.new_category_page
        )

        self.download_page = DownloadPage(parent=self)
        self.PAGES.DOWNLOAD_PAGE = self.stacked_widget.addWidget(self.download_page)

    def resizeEvent(self, event) -> None:
        """
        Resize the event and update the text of all RowWidgets in the layout.
        Args:
            event (QResizeEvent): The resize event object.
        Returns:
            None
        """
        super().resizeEvent(event)
        toolbox = self.main_widget.scroll_layout.itemAt(0).widget()
        # Перебор всех toolbox'ов
        for i in range(toolbox.count()):
            catbox = toolbox.widget(i)
            layout = catbox.layout()

            # Перебор всех виджетов RowWidget и обновление текста
            for j in range(layout.count()):
                widget = layout.itemAt(j).widget()
                if isinstance(widget, RowWidget):
                    # Вызов метода для обновления текста с учетом новой ширины
                    widget.update_text_nameWidget(self.width())
        settings.setValue(MainWindow.GEOMETRY_SAVED, self.saveGeometry())

    def closeEvent(self, event) -> None:
        """
        Override the close event of the widget.

        Args:
            event (QCloseEvent): The close event object.

        Returns:
            None
        """
        # if not self.confirm_exit:
        #     # Set the current index of the stacked widget to the exit page
        #     self.go_to(self.PAGES.EXIT_PAGE)
        #     # Ignore the close event
        #     event.ignore()
        # else:
        # Остановка всех активных потоков скачивания перед выходом
        if self.active_threads:
            for thread in self.active_threads:
                if thread.isRunning():
                    thread.stop()
                    thread.wait()
            self.download_page.activeDownloadThreads.clear()
        # Accept the close event
        settings.setValue("Window/geometry_saved", self.saveGeometry())
        event.accept()

    @QtCore.pyqtSlot(bool, name="on_top")
    def on_top(self, state: bool) -> None:
        """
        Set the window to be always on top or not based on the given state.

        Args:
            state (bool): Whether the window should be on top or not.
        """
        if state:
            self.setWindowFlag(
                QtCore.Qt.WindowType.WindowStaysOnTopHint,
                True,
            )
        else:
            self.setWindowFlag(
                QtCore.Qt.WindowType.WindowStaysOnTopHint,
                False,
            )
        # self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, True)
        self.show()
        self.raise_()

    @property
    def active_threads(self) -> list[Thread] | None:
        if self.download_page and hasattr(self.download_page, "activeDownloadThreads"):
            return self.download_page.activeDownloadThreads

    @QtCore.pyqtSlot(int, name="go_to")
    def go_to(self, page: int | None = None) -> None:
        """
        Go to the specified page in the stacked widget.

        Args:
            page (int, None): The index of the page to go to. If None, go to the main_window page.
        """
        self.CURRENT_PAGE = self.stacked_widget.currentIndex()
        if page and page != self.CURRENT_PAGE:
            if (
                page != self.PAGES.MAIN_PAGE
                or self.CURRENT_PAGE != self.PAGES.MAIN_PAGE
            ):
                self.page_history.append(self.CURRENT_PAGE)
                self.PREVIOUS_PAGE = self.CURRENT_PAGE
            else:
                self.PREVIOUS_PAGE = None
        self.stacked_widget.setCurrentIndex(page if page else self.PAGES.MAIN_PAGE)
        if not self.active_threads:
            self.download_page.update_download_info(COPYRIGHTS)

        # Show or hide the path viewer
        self.top_ui.path_viewer.setVisible(page == self.PAGES.BROWSER_PAGE)

    @QtCore.pyqtSlot(name="go_back")
    def go_back(self) -> None:
        """Go back to the previous page."""
        self.CURRENT_PAGE = self.stacked_widget.currentIndex()
        self.PREVIOUS_PAGE = self.stacked_widget.currentIndex()
        if self.page_history:
            previous_page = self.page_history.pop()
            self.stacked_widget.setCurrentIndex(previous_page)
        else:
            self.stacked_widget.setCurrentIndex(self.PAGES.MAIN_PAGE)
        if not self.active_threads:
            self.download_page.update_download_info(COPYRIGHTS)
        self.top_ui.path_viewer.hide()

    @QtCore.pyqtSlot(name="exit")
    def exit(self):
        self.confirm_exit = True
        self.close()
        sys.exit(0)


if __name__ == "__main__":
    if "FLATPAK_ID" not in os.environ:
        version_file()

    if PLATFORM == "windows":
        try:
            from ctypes import windll  # Only exists on Windows.

            myappid: str = f"org.mintguide.WebbAppReader.{VERSION}"
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except ImportError:
            windll = None
            ...

    startup()

    app = QApplication(sys.argv)
    palette = QPalette(QtCore.Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Window, QColor("#2B2B2B"))  # Цвет фона окна
    palette.setColor(
        QPalette.ColorRole.WindowText, QColor("#A9B7C6")
    )  # Цвет текста окна
    palette.setColor(
        QPalette.ColorRole.Base, QColor("#1A1A1A")
    )  # Цвет фона для элементов ввода
    palette.setColor(
        QPalette.ColorRole.AlternateBase, QColor("#2A2A2A")
    )  # Цвет фона для элементов ввода при чередовании
    palette.setColor(
        QPalette.ColorRole.ToolTipBase, QColor("#353535")
    )  # Цвет фона подсказок
    palette.setColor(
        QPalette.ColorRole.ToolTipText, QColor("#A9B7C6")
    )  # Цвет текста подсказок

    palette.setColor(QPalette.ColorRole.Text, QColor("#A9B7C6"))  # Цвет текста
    palette.setColor(QPalette.ColorRole.Button, QColor("#3C3F41"))  # Цвет фона кнопок
    palette.setColor(
        QPalette.ColorRole.ButtonText, QColor("#A9B7C6")
    )  # Цвет текста кнопок
    palette.setColor(
        QPalette.ColorRole.BrightText, QColor("#FFFFFF")
    )  # Яркий цвет текста
    palette.setColor(QPalette.ColorRole.Link, QColor("#859DD6"))  # Цвет ссылок
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#4C4F51"))  # Цвет подсветки
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))

    app.setPalette(palette)

    main_window: MainWindow = MainWindow(APP_TITLE, APP_ICON)
    main_window.show()

    sys.exit(app.exec())

    # TODO Мобильный сделать без рамки
    # TODO Мобильный сделать кнопку закрытия программы

    # TODO Сделать ограничение скорости, выбор для пользователя
    # TODO Сделать возможность органичения выхода в интернет (только оффлайн)
    # TODO сделать в классах slots для экономии памяти только там, где не меняются переменные
