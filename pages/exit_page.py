from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from ui.base_dialog_confirm import BaseDialogConfirm


class ExitPage(QWidget):
    exit_signal = pyqtSignal()
    back_signal = pyqtSignal()

    def __init__(self, text='', parent=None):
        super().__init__(parent=parent)
        self.parent = parent

        layout = QVBoxLayout(self)
        exit_widget = BaseDialogConfirm(parent=self, text=text)
        layout.addWidget(exit_widget)


        # сигал из основного диалога подключил тут
        exit_widget.yes_signal.connect(self.on_yes_clicked)
        exit_widget.no_signal.connect(self.on_no_clicked)

    @QtCore.pyqtSlot()
    def on_yes_clicked(self):
        # self.parent.exit()
        self.exit_signal.emit()

    @QtCore.pyqtSlot()
    def on_no_clicked(self):
        self.parent.confirm_exit = False
        # self.parent.go_back()
        self.back_signal.emit()