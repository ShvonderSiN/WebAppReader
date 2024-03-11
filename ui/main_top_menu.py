from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from constants import *
from tools import is_wayland


class TopUi(QWidget):
    go_to_add_page_signal = pyqtSignal(int)
    go_to_download_page_signal = pyqtSignal(int)
    on_top_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
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

        layout.addItem(spacer)

        self.on_top_checkbox = QCheckBox(text="ON TOP")
        self.on_top_checkbox.setToolTip("Keep window on top".upper())
        if PLATFORM in ["windows", "linux"]:
            # self.on_top_checkbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.on_top_checkbox.stateChanged.connect(self.on_checkbox_state_changed)

            self.on_top_checkbox.setStyleSheet(
                f"""
                                                QCheckBox::indicator {{
                                                    width: {btn_add_source.size().width() / 2}px;
                                                    height: {btn_add_source.size().height() / 2}px;
                                                    background-color: none;
                                                                    }}
                                                """
            )

            layout.addWidget(self.on_top_checkbox) if not is_wayland() else None
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
