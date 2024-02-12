from PyQt6 import QtWidgets


class ContextMenu(QtWidgets.QMenu):
    def __init__(self, parent=None, context=None):
        super().__init__(parent=parent)
        self.parent = parent

        # Создаем действия для контекстного меню в зависимости от контекста
        if context == "row_widget":
            self.editAct = self.addAction("EDIT")
            self.deleteAct = self.addAction("DELETE")
            # self.openAct = self.addAction("Open for Context1")
        # elif context == "Context2":
        #     self.newAct = self.addAction("New for Context2")
        #     self.openAct = self.addAction("Open for Context2")

        # Добавляем общие действия
        # self.exitAct = self.addAction("Exit")

        # Подключаем действия к слотам (методам)

    #     self.editAct.triggered.connect(self.edit_method)
    #     self.deleteAct.triggered.connect(self.delete_method)
    #     # self.exitAct.triggered.connect(self.exit_method)
    #
    # def edit_method(self):
    #     print('edit')
    #
    # def delete_method(self):
    #     print('deleted')
