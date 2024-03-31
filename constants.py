import os
import platform
import subprocess
import sys

from PyQt6.QtCore import QStandardPaths

if getattr(sys, "frozen", False):
    # Если приложение запущено из исполняемого файла
    BASE_DIR = sys._MEIPASS
else:
    # Если приложение запущено из исходного кода
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VERSION = "1.2.0"

PLATFORM: str = platform.system().lower()
APP_TITLE: str = "WebAppReader"
APP_DATA_FOLDER: str = os.path.join(
    QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation),
    APP_TITLE,
)
ERROR_LOG = os.path.join(APP_DATA_FOLDER, "error_log.txt")
SOURCES_FOLDER: str = os.path.join(BASE_DIR, "src")
EASY_LIST: str = os.path.join(BASE_DIR, SOURCES_FOLDER, "easylist.txt")
APP_ICON: str = (
    os.path.join(SOURCES_FOLDER, "logo_128.png")
    if PLATFORM == "linux"
    else os.path.join(SOURCES_FOLDER, "logo.ico")
)
DATA_WEBSITES_FOLDER: str = "websites"
HOME_DIRECTORY = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.HomeLocation
)
CONFIG_FOLDER_PATH = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.AppConfigLocation
)

NO_IMAGE: str = "blank_image.png"
MENU_ICON: str = "menu.png"
HOME_ICON: str = "home.png"
BACK_ARROW_ICON: str = "back_arrow.png"
FORWARD_ARROW_ICON: str = "forward_arrow.png"
SAVE_ICON: str = "save.png"
APPLY_ICON: str = "apply.png"
CANCEL_ICON: str = "cancel.png"
CLOSE_ICON: str = "close.png"
EXIT_ICON: str = "exit.png"
ADD_ICON: str = "add.png"
OPEN_FILE_ICON: str = "open_file.png"
REMOVE_ICON: str = "remove.png"
LOCAL_ICON: str = "local.png"
REMOTE_ICON: str = "remote.png"
DOWNLOAD_ICON: str = "download.png"
SEARCH_ICON: str = "search.png"
UP_ICON: str = "up.png"
DOWN_ICON: str = "down.png"

ADD_NEW_CATEGORY_TEXT = "Add new..."
NO_CATEGORY_TEXT = "No category"

COPYRIGHTS = "Shekin © 2024, MintGuide.org. All rights reserved."


def get_wget() -> str | None:
    try:
        check_wget = subprocess.run(["wget2", "-V"], stdout=subprocess.PIPE)
        check_wget_output = check_wget.stdout.decode()
        if "wget2" in check_wget_output.lower()[0:20]:
            return "wget2"
        return "wget"
    except FileNotFoundError:
        return None


WGET = ""
if PLATFORM == "windows":
    WGET = os.path.join(BASE_DIR, "wget.exe")
elif PLATFORM == "linux":
    if get_wget() == "wget2":
        WGET = "wget2"
    else:
        WGET = "wget"


REQUEST_TIMEOUT_HTML: int = 3
REQUEST_TIMEOUT_ICON: int = 3


class PagesConstants:
    """Singleton"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_constants()
        return cls._instance

    def init_constants(self):
        self.MAIN_PAGE = None
        self.EXIT_PAGE = None
        self.ERROR_PAGE = None
        self.ADD_EDIT_PAGE = None
        self.NEW_CATEGORY_PAGE = None
        self.BROWSER_PAGE = None
        self.DELETE_PAGE = None
        self.EDIT_SITE_ID = None
        self.DOWNLOAD_PAGE = None
