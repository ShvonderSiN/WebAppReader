from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from ui.base_dialog_confirm import BaseDialogConfirm


class ErrorPage(QWidget):
    back_signal = pyqtSignal()

    def __init__(self, text='', parent=None):
        super().__init__(parent=parent)
        self.parent = parent

        layout = QVBoxLayout(self)
        error_widget = BaseDialogConfirm(parent=self, text=text)
        error_widget.apply_button.hide()
        error_widget.hidden_label.hide()
        layout.addWidget(error_widget)

        # сигал из основного диалога подключил тут
        error_widget.no_signal.connect(self.on_no_clicked)

    @QtCore.pyqtSlot()
    def on_no_clicked(self):
        self.back_signal.emit()

    def set_text(self, text):
        self.text = text