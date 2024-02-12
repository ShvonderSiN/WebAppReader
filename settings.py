import logging

from PyQt6.QtCore import QStandardPaths, QSettings, QCoreApplication, QRect, QSize

from constants import ERROR_LOG

logging.basicConfig(filename=ERROR_LOG, level=logging.ERROR)


settings = QSettings('WebAppReader', 'WebAppReader')

settings.beginGroup("Window")
# Установка размера окна по умолчанию, если он не задан
if not settings.contains("minimumSize"):
    settings.setValue("minimumSize", QSize(450, 600))
# Установка геометрии окна по умолчанию, если она не задана
if not settings.contains('geometry'):
    settings.setValue('geometry', QRect(250, 150, 450, 600))
settings.endGroup()


settings.beginGroup("Paths")
# settings.setValue('settings')
settings.endGroup()

status = settings.status()
if status != QSettings.Status.NoError:
    logging.error(f'Error saving settings', exc_info=False)

