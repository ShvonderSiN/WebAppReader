from PyQt6 import QtWidgets, QtGui, QtCore
import os

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QStyle


class CustomTitleBar(QtWidgets.QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent=parent)
        self.title = title
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)

        self.title = QtWidgets.QLabel(title)
        self.layout.addWidget(self.title)

        self.layout.setStretch(0, 1)

        self.minimize_button = self.create_button('', QStyle.StandardPixmap.SP_TitleBarMinButton, parent.showMinimized)
        self.layout.addWidget(self.minimize_button)

        self.maximize_button = self.create_button('', QStyle.StandardPixmap.SP_TitleBarMaxButton, self.toggle_maximize)
        self.layout.addWidget(self.maximize_button)

        self.close_button = self.create_button('',
                                               QStyle.StandardPixmap.SP_TitleBarCloseButton,
                                               lambda: parent.stacked_widget.setCurrentIndex(parent.EXIT_PAGE))
        self.layout.addWidget(self.close_button)

        # Стилизация
        self.setStyleSheet("""
                    color: white; 
                    border: none;
                    font-size: 16px;
                """)
        self.title.setStyleSheet("padding: 10px;")

        self.mousePressPosition = None

    def create_button(self, text, icon_pixmap, callback):
        button = QtWidgets.QPushButton(text)
        button.setFixedSize(QSize(25, 25))
        button.setStyleSheet("background-color: none")
        if icon_pixmap:
            icon = self.style().standardIcon(icon_pixmap)
            button.setIcon(icon)
            button.setIconSize(button.size())
        button.setFlat(True)
        button.clicked.connect(callback)
        return button

    def toggle_maximize(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
        else:
            self.parent().showMaximized()

    def mousePressEvent(self, event):
        self.mousePressPosition = event.globalPosition().toPoint() - self.parent().frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.mousePressPosition:
            self.parent().move(event.globalPosition().toPoint() - self.mousePressPosition)

    def mouseReleaseEvent(self, event):
        self.mousePressPosition = None

    def mouseDoubleClickEvent(self, event):
        self.toggle_maximize()
