import logging

from PyQt6.QtCore import QRect, QSettings, QSize

from constants import ERROR_LOG

logging.basicConfig(filename=ERROR_LOG, level=logging.ERROR)


settings = QSettings(
    "WebAppReader",
    "WebAppReader",
)

# settings.setDefaultFormat(QSettings.Format.IniFormat)

settings.beginGroup("Window")
# Установка размера окна по умолчанию
# if not settings.contains("minimumSize"):
settings.setValue("minimumSize", QSize(400, 400))
# Установка геометрии окна по умолчанию, если она не задана
if not settings.contains("geometry"):
    settings.setValue("geometry", QRect(250, 150, 450, 600))
settings.endGroup()


settings.beginGroup("Paths")
# settings.setValue('settings')
settings.endGroup()

status = settings.status()
if status != QSettings.Status.NoError:
    logging.error("Error saving settings", exc_info=False)
