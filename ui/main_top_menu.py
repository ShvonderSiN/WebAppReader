import os

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from constants import (
    ADD_ICON,
    BASE_DIR,
    BROWSER_REMOTES,
    DOWNLOAD_ICON,
    PLATFORM,
    PagesConstants,
    SOURCES_FOLDER,
)
from settings import settings


# from tools import is_wayland


class TopUi(QWidget):
    go_to_add_page_signal = pyqtSignal(int)
    go_to_download_page_signal = pyqtSignal(int)
    on_top_signal = pyqtSignal(bool)
    offline_signal = pyqtSignal(bool)

    NOW_ONLINE: str = "NOW ONLINE"
    NOW_OFFLINE: str = "NOW OFFLINE"

    def __init__(self, parent: QMainWindow = None):
        super().__init__(parent=parent)
        self.main = parent
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.PAGES = PagesConstants()

        btn_add_source = QPushButton()
        btn_add_source.setToolTip("Add new source".upper())
        add_site_icon = QIcon(os.path.join(BASE_DIR, SOURCES_FOLDER, ADD_ICON))
        btn_add_source.clicked.connect(
            lambda: self.go_to_add_page_signal.emit(self.PAGES.ADD_EDIT_PAGE)
        )

        btn_download_site = QPushButton()
        btn_download_site.setToolTip("Download new site".upper())
        download_site_icon = QIcon(
            os.path.join(BASE_DIR, SOURCES_FOLDER, DOWNLOAD_ICON)
        )
        btn_download_site.clicked.connect(
            lambda: self.go_to_download_page_signal.emit(self.PAGES.DOWNLOAD_PAGE)
        )

        for widget, icon in zip(
            [btn_add_source, btn_download_site], [add_site_icon, download_site_icon]
        ):
            widget.setIcon(icon)
            widget.setFixedSize(40, 40)
            widget.setIconSize(widget.size())
            widget.setFlat(True)
            layout.addWidget(widget)

        spacer = QSpacerItem(
            10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.path_viewer = QLabel()
        self.path_viewer.hide()

        layout.addItem(spacer)
        layout.addWidget(self.path_viewer)

        self.on_top_checkbox = self.on_top_checkbox()
        self.offline_checkbox = self.offline_checkbox()
        CHECKBOX_STYLESHEET = f"""
                                                QCheckBox::indicator {{
                                                    width: {btn_add_source.size().width() / 2}px;
                                                    height: {btn_add_source.size().height() / 2}px;
                                                    background-color: none;
                                                                    }}
                                                """
        self.on_top_checkbox.setStyleSheet(CHECKBOX_STYLESHEET)
        self.offline_checkbox.setStyleSheet(CHECKBOX_STYLESHEET)
        # layout.addWidget(self.on_top_checkbox) if not is_wayland() else None
        (
            layout.addWidget(self.on_top_checkbox)
            if PLATFORM
            not in [
                "linux",
            ]
            else None
        )
        layout.addWidget(self.offline_checkbox)
        # TODO следить за обновлениями pyqt6 может пофиксят
        # if CAN_DOWNLOAD is False:
        #     btn_download_site.hide()

    def on_checkbox_state_changed(self, state):
        if state:
            # self.main.on_top(True)
            self.on_top_signal.emit(True)
        else:
            # self.main.on_top(False)
            self.on_top_signal.emit(False)

    def on_checkbox_offline_changed(self, state):
        if state:
            self.offline_signal.emit(True)
            self.offline_checkbox.setText(TopUi.NOW_OFFLINE)
            self.offline_checkbox.setToolTip("Can't view remotes".upper())
            settings.setValue(BROWSER_REMOTES, 1)
        else:
            self.offline_signal.emit(False)
            self.offline_checkbox.setText(TopUi.NOW_ONLINE)
            self.offline_checkbox.setToolTip("Can view remotes".upper())
            settings.setValue(BROWSER_REMOTES, 0)

    def on_top_checkbox(self) -> QCheckBox:
        on_top_checkbox = QCheckBox(text="ON TOP")
        on_top_checkbox.setToolTip("Keep window on top".upper())
        # self.on_top_checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        on_top_checkbox.stateChanged.connect(self.on_checkbox_state_changed)
        return on_top_checkbox

    def offline_checkbox(self) -> QCheckBox:
        offline_checkbox = QCheckBox()

        if settings.value(BROWSER_REMOTES) == "1" or not settings.contains(
            BROWSER_REMOTES
        ):
            offline_checkbox.setText(TopUi.NOW_OFFLINE)
            offline_checkbox.setToolTip("Can't view remotes".upper())
            offline_checkbox.setChecked(True)
        else:
            offline_checkbox.setText(TopUi.NOW_ONLINE)
            offline_checkbox.setToolTip("Can view remotes".upper())
            offline_checkbox.setChecked(False)
        # self.on_top_checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        offline_checkbox.stateChanged.connect(self.on_checkbox_offline_changed)
        return offline_checkbox

    def set_path_viewer(self, path: str):
        self.path_viewer.setText(path)
        self.path_viewer.show()
