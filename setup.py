import sys

from cx_Freeze import Executable, setup

from constants import APP_ICON, SOURCES_FOLDER
from webappreader import version

# Определение путей к недостающим библиотекам и включение Qt плагинов
libraries_path = [
    # ("/home/test/Downloads/qtbase/lib/libQt6WebView.so.6", "./lib/libQt6WebView.so.6"),
]

include_files = [(SOURCES_FOLDER, "src")] + libraries_path
bin_path_includes = ["/home/test/Downloads/qtbase/lib"]

# Попытка импортировать функцию для определения путей к Qt плагинам
try:
    from cx_Freeze.hooks import get_qt_plugins_paths
except ImportError:
    get_qt_plugins_paths = None

if get_qt_plugins_paths:
    # Включение дополнительных Qt плагинов
    for plugin_name in (
        "wayland-decoration-client",
        "wayland-graphics-integration-client",
        "wayland-shell-integration",
    ):
        include_files += get_qt_plugins_paths("PyQt6", plugin_name)


# Платформо-специфичные настройки
if sys.platform == "win32":
    # Добавляем файл только для Windows
    include_files.append(("wget.exe", "wget.exe"))
    bin_path_includes = []


# Зависимости приложения и настройки сборки
build_exe_options = {
    "zip_include_packages": [
        "sqlalchemy",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWidgets",
        "Qt6",
    ],
    "packages": [
        "sqlalchemy",
        "html5lib",
        "PyQt6",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWidgets",
    ],
    "excludes": [
        "tk8.6",
        "tkinter",
        "unittest",
        "black",
    ],
    "include_files": include_files,
    "bin_path_includes": bin_path_includes,
}

# base="Win32GUI" должен использоваться только для графических приложений Windows
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="WebAppReader",
    version=version,
    description="Offline web content reader",
    options={"build_exe": build_exe_options},
    executables=[Executable("webappreader.py", base=base, icon=APP_ICON, targetname)],
)
