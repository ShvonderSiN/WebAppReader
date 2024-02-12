import shutil
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urljoin, urlunparse
import re
import requests

from PyQt6.QtWidgets import QLineEdit
from bs4 import BeautifulSoup
from fake_headers import Headers

from constants import *
from database.models import Website


class Request:
    def __init__(self):
        self.params = Headers().generate()
        self.session = requests.Session()

    def get(self, url: str, pretty_html: bool = False, xmltodict=None, binary=False,
            timeout=2) -> None | bytes | str | Any:
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
            raise TimeoutError(f'Запрос к {url} превысил установленный таймаут.', Request.__name__)

        if response.status_code == 200:
            headers = response.headers
            if 'json' in headers['Content-Type'].lower():
                return response.json(indent=4, ensure_ascii=False)
            elif 'xml' in headers['Content-Type'].lower():
                return xmltodict.parse(response.content)
            elif binary or any(
                    img_format in headers['Content-Type'] for img_format in ['image/jpeg', 'image/png', 'image/gif']):
                return response.content
            else:
                if pretty_html:
                    return BeautifulSoup(response.text, 'html5lib').prettify()
                return response.text
        else:
            print(f'Ответ сервера: {response.status_code}', Request.__name__)
            # sys.exit(0)

    def __repr__(self):
        return f'Объект запроса класса Request'


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
        if result.scheme in ('http', 'https'):
            return True
        elif result.scheme == 'file' or result.scheme == '' or bool(Path(url).drive):
            file_path = result.path if result.scheme == 'file' else url
            if os.path.isfile(file_path):
                file_extension = Path(file_path).suffix.lower()
                supported_extensions = ['.html', '.htm']
                if file_extension in supported_extensions:
                    return True
            return False
        else:
            return False
    except Exception as e:
        print(f'Error {e}', validate_url.__name__)
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
        raise ConnectionError('No internet connection', has_internet_connection.__name__)


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
        # if not has_internet_connection():
        #     return False  # Возвращает False, если нет интернет-соединения

        return True
    else:
        _, ext = os.path.splitext(source)
        return ext.lower() in ('.html', '.htm')


def open_file(path: str) -> str | None:
    try:
        with open(path, encoding='utf-8', newline='') as file:
            #  TODO добавить открытие pdf файлов и возможно картинок шрапгалок
            return file.read()
    except UnicodeDecodeError as er:
        print(f'UnicodeDecodeError {str(er)} in function: {open_file.__name__}')
        return None


def delete_icon(path: str) -> None:
    path = str(path)
    icon_name = os.path.basename(path)

    icon_folder = os.path.join(BASE_DIR, DATA_FOLDER, DATA_ICONS_FOLDER, icon_name)
    if icon_folder == path and os.path.exists(path):
        os.remove(path)


def get_domain(url):
    parsed_url = urlparse(url)
    domain_url = urlunparse((parsed_url.scheme, parsed_url.netloc, "", "", "", ""))
    return domain_url


def delete_data_from_website(path: str) -> None:
    if not path.startswith('http'):
        path_parts = path.split(os.sep)
        try:
            websites_index = path_parts.index(DATA_WEBSITES_FOLDER)
            domain_folder = path_parts[websites_index + 1]
            folder_to_remove = os.path.join(BASE_DIR, DATA_FOLDER, DATA_WEBSITES_FOLDER, domain_folder)
            from database.database import session
            db_site = session.query(Website).filter(Website.url.ilike(f"%{domain_folder}%")).first()

            if not db_site and os.path.exists(folder_to_remove):
                shutil.rmtree(folder_to_remove)
        except ValueError:
            pass


def get_new_title_icon(path) -> tuple:
    """ Получаю введенный заголовок для вывода в окне добавления"""
    local = os.path.isfile(path)
    if local:
        html = open_file(path)
    else:
        req = Request()
        html = req.get(url=path, pretty_html=True, timeout=REQUEST_TIMEOUT_HTML)
    try:
        soup = BeautifulSoup(html, "html5lib")
    except TypeError:
        return '', os.path.join(BASE_DIR, SOURCES_FOLDER, NO_IMAGE)

    title = soup.title.string.strip() if soup.title else ''
    title_result = re.sub(r"\s+", ' ', title).strip()

    # Попробуем найти иконку в различных местах
    icon_link = (soup.find('link', rel='apple-touch-icon') or
                 soup.find('link', rel='icon') or
                 soup.find('link', attrs={'rel': re.compile(r'(^|\s)icon(\s|$)')}) or
                 soup.find('link', href='/favicon.ico'))

    icon_href = icon_link['href'] if icon_link and icon_link.has_attr('href') else '/favicon.ico'
    if local:
        # Формируем путь к иконке относительно пути к HTML файлу
        icon_path = os.path.normpath(os.path.join(os.path.dirname(path), icon_href))

        # Проверяем, существует ли файл по данному пути
        if os.path.isfile(icon_path):
            return title_result, icon_path
        return title_result or os.path.dirname(icon_path).capitalize(), os.path.join(BASE_DIR, 'src', NO_IMAGE)
    else:
        base_url = path
        absolute_icon_url = urljoin(base_url, icon_href)
        domain_name = urlparse(absolute_icon_url).netloc
        file_name = domain_name + os.path.basename(absolute_icon_url)
        req = Request()
        img = req.get(url=absolute_icon_url, binary=True, timeout=REQUEST_TIMEOUT_ICON)
        with open(os.path.join(BASE_DIR, DATA_FOLDER, DATA_ICONS_FOLDER, file_name), 'wb') as file:
            file.write(img)
            return title_result or domain_name.capitalize(), os.path.join(BASE_DIR, DATA_FOLDER, DATA_ICONS_FOLDER,
                                                                          file_name)


def widgets_value_cleaner(self, page: int):
    line_edit = self.stacked_widget.widget(page).findChildren(QLineEdit)
    for child_widget in line_edit:
        if isinstance(child_widget, QLineEdit):
            child_widget.clear()


def create_folders():
    # if not os.path.exists(os.path.join(BASE_DIR, DATA_FOLDER)):
    #     os.mkdir(os.path.join(BASE_DIR, DATA_FOLDER))
    # if not os.path.exists(os.path.join(BASE_DIR, DATA_FOLDER, DATA_ICONS_FOLDER)):
    #     os.mkdir(os.path.join(BASE_DIR, DATA_FOLDER, DATA_ICONS_FOLDER))
    # if not os.path.exists(os.path.join(BASE_DIR, DATA_FOLDER, DATA_WEBSITES_FOLDER)):
    #     os.mkdir(os.path.join(BASE_DIR, DATA_FOLDER, DATA_WEBSITES_FOLDER))
    if not os.path.exists(APP_DATA_FOLDER):
        os.makedirs(APP_DATA_FOLDER)


def is_wayland() -> bool:
    wayland_display = 'wayland-0'

    if os.environ.get('WAYLAND_DISPLAY', None) == wayland_display:
        return True
    return False
