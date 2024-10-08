import logging
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse
from venv import logger

import requests
from PyQt6.QtWidgets import QLineEdit
from bs4 import BeautifulSoup
from fake_headers import Headers

from constants import (
    APP_DATA_FOLDER,
    BASE_DIR,
    ERROR_LOG,
    NO_IMAGE,
    REQUEST_TIMEOUT_HTML,
    SOURCES_FOLDER,
)

logging.basicConfig(filename=ERROR_LOG, level=logging.ERROR)


class Request:
    def __init__(self):
        self.params = Headers().generate()
        self.session = requests.Session()

    def get(
        self,
        url: str,
        pretty_html: bool = False,
        xmltodict=None,
        binary=False,
        timeout=2,
    ) -> None | bytes | str | Any:
        """
        Для получения содержимого веб страниц и прочих данных
        :param proxies: {'https://': 'IP:port'}
        :param url: Ссылка на ресурс в виде строки
        :param pretty_html: Вернуть ли содержимое в виде теста вместе с хтмл
        :return: возвращает строку
        """
        try:
            response = self.session.get(url=url, params=self.params, timeout=timeout)
        except requests.Timeout:
            raise TimeoutError(
                f"Запрос к {url} превысил установленный таймаут.", Request.__name__
            )

        if response.status_code == 200:
            headers = response.headers
            if "json" in headers["Content-Type"].lower():
                return response.json(indent=4, ensure_ascii=False)
            elif "xml" in headers["Content-Type"].lower():
                return xmltodict.parse(response.content)
            elif binary or any(
                img_format in headers["Content-Type"]
                for img_format in ["image/jpeg", "image/png", "image/gif"]
            ):
                return response.content
            else:
                if pretty_html:
                    return BeautifulSoup(response.text, "html5lib").prettify()
                return response.text
        else:
            logger.error(
                f"Ответ сервера: {response.status_code}, {validate_url.__name__}",
                exc_info=False,
            )
            return None

    def __repr__(self):
        return f"Объект запроса класса Request"


def validate_url(url):
    """
    Проверяет URL на валидность.

    Параметры:
        url (str): URL для проверки.

    Возвращает:
        bool: True, если URL валидный, в противном случае False.
    """
    try:
        result = urlparse(url)
        if result.scheme in ("http", "https"):
            return True
        elif result.scheme == "file" or result.scheme == "" or bool(Path(url).drive):
            file_path = result.path if result.scheme == "file" else url
            if os.path.isfile(file_path):
                file_extension = Path(file_path).suffix.lower()
                supported_extensions = [".html", ".htm"]
                if file_extension in supported_extensions:
                    return True
            return False
        else:
            return False
    except Exception as e:
        logger.error(f"Error {e}, {validate_url.__name__}", exc_info=False)
        return False


def has_internet_connection(url="https://www.google.com"):
    """
    Проверяет, есть ли интернет-соединение.

    Возвращает:
        bool: True, если есть соединение, иначе False.
    """
    try:
        # Попытка выполнить запрос к Google
        response = requests.get(url, timeout=1)
        return True if response.status_code == 200 else False
    except requests.RequestException:
        raise ConnectionError(
            "No internet connection", has_internet_connection.__name__
        )


def is_html_source(source):
    """
    Проверяет, является ли источник HTML-файлом или веб-страницей.

    Параметры:
        source (str): Путь к файлу или URL для проверки.

    Возвращает:
        bool: True, если источник является HTML, в противном случае False.
    """
    source = source.lower()
    if source.startswith("http://") or source.startswith("https://"):
        return True
    else:
        _, ext = os.path.splitext(source)
        return ext.lower() in (".html", ".htm")


def open_file(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8", newline="") as file:
            #  TODO добавить открытие pdf файлов и возможно картинок шрапгалок
            return file.read()
    except UnicodeDecodeError as er:
        logging.error(
            f"UnicodeDecodeError {str(er)} in function: {open_file.__name__}",
            exc_info=False,
        )
        return None


def download_and_save_icon(icon_url, save_dir):
    response = requests.get(icon_url)
    response.raise_for_status()

    icon_filename = Path(icon_url).name
    target_path = Path(save_dir) / icon_filename

    # Сохраняем иконку локально
    with open(target_path, "wb") as f:
        f.write(response.content)

    return target_path


def get_domain(url):
    parsed_url = urlparse(url)
    domain_url = urlunparse((parsed_url.scheme, parsed_url.netloc, "", "", "", ""))
    return domain_url


def get_new_title_icon(path) -> tuple:
    """Retrieve the page title and icon for a given HTML path or URL."""
    local = os.path.isfile(path)
    if local:
        html = open_file(path)
    else:
        req = Request()
        html = req.get(url=path, pretty_html=True, timeout=REQUEST_TIMEOUT_HTML)

    try:
        soup = BeautifulSoup(html, "html5lib")
    except TypeError:
        return "", os.path.join(BASE_DIR, SOURCES_FOLDER, NO_IMAGE)

    title = soup.title.string.strip() if soup.title else ""
    title_result = re.sub(r"\s+", " ", title).strip()

    # Expanding the icon search to include various rel attributes
    icons = soup.find_all(
        "link", href=True, rel=re.compile(r"(apple-touch-icon|icon|shortcut icon)")
    )

    # Improved sorting: prioritize PNG, then other popular formats, and place ICO last
    icons_sorted = sorted(
        icons,
        key=lambda x: (
            x["href"].endswith(".ico"),
            not x["href"].endswith(".png"),
            x["rel"],
        ),
    )

    icon_href = next(
        (icon["href"] for icon in icons_sorted if icon.has_attr("href")), "/favicon.ico"
    )

    # Handle URLs starting with '//'
    if icon_href.startswith("//"):
        icon_href = "http:" + icon_href

    if not icon_href.startswith(("http", "//")):
        if local:
            icon_path = os.path.normpath(os.path.join(os.path.dirname(path), icon_href))
        else:
            icon_path = urljoin(path, icon_href)
    else:
        icon_path = icon_href

    if (
        local
        and os.path.isfile(icon_path)
        or not local
        and icon_path.startswith("http")
    ):
        return title_result, icon_path

    return title_result or "Enter title", os.path.join(BASE_DIR, "src", NO_IMAGE)


def widgets_value_cleaner(self, page: int):
    line_edit = self.stacked_widget.widget(page).findChildren(QLineEdit)
    for child_widget in line_edit:
        if isinstance(child_widget, QLineEdit):
            child_widget.clear()


def create_folders():
    if not os.path.exists(APP_DATA_FOLDER):
        os.makedirs(APP_DATA_FOLDER)


def is_wayland() -> bool:
    wayland_display = "wayland-0"

    if os.environ.get("WAYLAND_DISPLAY", None) == wayland_display:
        return True
    return False
