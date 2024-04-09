import logging
import threading
from datetime import datetime
from typing import IO

from PyQt6 import QtCore
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from fake_headers import Headers  # type: ignore

from constants import *
from settings import settings
from tools import get_domain, has_internet_connection, is_html_source
from ui.base_dialog_save import BaseDialogSave

logging.basicConfig(filename=ERROR_LOG, level=logging.ERROR)

HEIGHT = 35
WEIGHT = 40
EXAMPLE_URL = "https://example.com"
EXAMPLE_URL_PARENTS = "https://example.com/en/blog"


class DownloadThread(QThread):
    finished = pyqtSignal()
    update_info = pyqtSignal(str)

    def __init__(self, command, parent=None, base_path=None, url=None):
        super().__init__(parent=parent)
        self.process = None
        self.parent = parent
        self.command = command
        self.path_text = base_path
        self.domain = get_domain(url).split("//")[-1]

    def _read_output(self, pipe: IO[str], emit_signal) -> None:
        count: int = 0
        dots: str = ""
        try:
            for line in iter(pipe.readline, ""):
                print(line)
                if "saved" in line.lower() or "downloading" in line.lower():
                    count += 1
                    message_line = f"saving files:  {count}"
                elif "converting" in line.lower():
                    message_line = f"converting links   {dots}"
                    if len(dots) > 3:
                        dots = ""
                    else:
                        dots += "."
                else:
                    continue
                emit_signal.emit(f"{self.domain}:   {message_line}")
        except Exception as e:
            logging.error(f"Error reading from stream: {e}")
            emit_signal.emit("Error reading data")

    def run(self):
        try:
            if PLATFORM == "windows":
                flag = subprocess.CREATE_NO_WINDOW
            else:
                flag = 0
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=flag,
            )

        except Exception as e:
            logging.error(f"Error starting the process: {e}")
            self.update_info.emit("Error starting the process")
            self.finished.emit()
            return

        # Создание и запуск потоков для чтения stdout и stderr
        stdout_thread = threading.Thread(
            target=self._read_output, args=(self.process.stdout, self.update_info)
        )
        stderr_thread = threading.Thread(
            target=self._read_output, args=(self.process.stderr, self.update_info)
        )

        stdout_thread.start()
        stderr_thread.start()

        # Ожидание завершения процесса
        self.process.wait()

        # Ожидание завершения потоков чтения
        stdout_thread.join()
        stderr_thread.join()

        self.finished.emit()
        self.command.clear()

    def stop(self):
        if self.process:
            self.process.terminate()  # Пытаемся корректно завершить процесс
            self.process.wait(timeout=5)  # Даем время на завершение
            if self.process.poll() is None:  # Если процесс все еще не завершился
                self.process.kill()  # Принудительно завершаем процесс
                self.process.wait()  # Дожидаемся его завершения
        self.quit()  # Завершаем поток


class DownloadPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.main = parent
        self.PAGES = PagesConstants()

        self.activeDownloadThreads = []
        self.download_thread = None

        layout = QVBoxLayout(self)
        layout.addStretch(1)

        label_info = QLabel(
            "Here you can download the website in its entirety or partially.\n".upper()
        )
        label_info.setWordWrap(True)
        label_info.setContentsMargins(60, 0, 60, 0)
        label_info.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        layout_form = QFormLayout()
        layout_form.setSpacing(15)
        self.url_line_edit = QLineEdit()
        self.url_line_edit.setFixedHeight(HEIGHT)
        self.url_line_edit.setPlaceholderText(EXAMPLE_URL)
        self.url_line_edit.textChanged.connect(self.__validate_field)
        self.url_line_edit.setToolTip(
            "Enter the URL of the website you want to download."
        )
        self.no_parents_checkbox = QCheckBox("No parents".upper())
        self.no_parents_checkbox.setFixedHeight(HEIGHT)
        self.no_parents_checkbox.setToolTip(
            "Restrict recursive download to the specified directory, without ascending to the "
            "parent directory.".upper()
        )
        self.no_parents_checkbox.stateChanged.connect(lambda: self.no_parents)

        self.path_line_edit = QLineEdit()
        self.path_line_edit.setFixedHeight(HEIGHT)
        self.path_line_edit.setToolTip("Enter the path to save the downloaded files.")
        self.path_text = settings.value("Paths/download_path") or None

        if self.path_text:
            self.path_line_edit.setText(settings.value("Paths/download_path"))
        else:
            self.path_line_edit.setPlaceholderText(HOME_DIRECTORY)
        self.file_btn = QPushButton()
        self.file_btn.setToolTip(
            "Click to choose the path to save the downloaded files."
        )
        open_file_icon = QIcon(os.path.join(BASE_DIR, SOURCES_FOLDER, OPEN_FILE_ICON))
        self.file_btn.setFixedSize(WEIGHT, HEIGHT)
        self.file_btn.setIconSize(self.file_btn.size())
        self.file_btn.setIcon(open_file_icon)
        self.file_btn.setFlat(True)
        self.file_btn.clicked.connect(self.select_download_directory)
        layout_form.addRow(label_info)
        layout_form.addRow(self.no_parents_checkbox, self.url_line_edit)
        layout_form.addRow(self.file_btn, self.path_line_edit)
        layout.addLayout(layout_form)

        self.dialog_save = BaseDialogSave(self)
        self.dialog_save.save_button.setIcon(
            QIcon(os.path.join(BASE_DIR, "src", DOWNLOAD_ICON))
        )
        self.dialog_save.save_button.clicked.connect(self.__start_download)
        self.dialog_save.cancel_button.clicked.connect(self.__cancel_clicked)
        layout.addWidget(self.dialog_save)
        layout.addStretch(1)
        layout.setContentsMargins(30, 0, 30, 0)
        if get_wget() == "wget2":
            self.command_default = [
                WGET,
                "--recursive",
                "--page-requisites",
                "--level=7",
                "--limit-rate=1500K",
                "--no-check-certificate",
                "--force-directories",
                "--restrict-file-names=windows",
                "--adjust-extension",
                "--convert-links",
                "--random-wait",
            ]

        else:
            self.command_default = [
                WGET,
                "-r",
                "-k",
                "--level=7",
                "--limit-rate=1500K",
                "-p",
                "-E",
                "--restrict-file-names=windows",
                # '-nc',
                "--no-check-certificate",
            ]

    def __cancel_clicked(self):
        self.url_line_edit.clear()
        self.no_parents_checkbox.setChecked(False)
        self.main.go_back()

    @property
    def headers(self) -> list[str]:
        """
        Return a list of headers for the API request.

        :return: a list of headers for the API request
        :rtype: list[str]
        """
        headers_list = [
            "--header=" + key + ": " + value
            for key, value in Headers(headers=True).generate().items()
        ]
        headers_list.append("--header=Accept-Encoding: identity")
        return headers_list

    @property
    def no_parents(self) -> bool:
        """
        Returns a boolean value indicating whether the 'no_parents' checkbox is checked.
        """
        if self.no_parents_checkbox.isChecked():
            return True
        return False

    def __validate_field(self) -> None:
        """
        Validates the field by checking if the URL line edit contains an HTML source.
        """
        if is_html_source(self.url_line_edit.text()):
            self.dialog_save.save_button.setEnabled(True)
        else:
            self.dialog_save.save_button.setEnabled(False)

    def __start_download(self) -> None:
        """
        Initializes the download process by retrieving the URL from the text input field and setting up the command for download.
        """
        self.url = self.url_line_edit.text()
        self.command = self.command_default.copy()

        if self.no_parents:
            self.command.insert(4, "-np")
            if get_wget() == "wget2":
                self.command.remove("--page-requisites")
        self.path_text = self.path_line_edit.text() or HOME_DIRECTORY
        settings.setValue("Paths/download_path", self.path_text)
        self.command.append("-P")
        self.command.append(self.path_text)
        self.command.append(self.url.lower())
        self.command += self.headers
        print(" ".join(self.command))
        """wget -r -k --level=7 -np --limit-rate=1500K -p -E --restrict-file-names=windows --no-check-certificate -P /home/shekin/Documents/HTML/111 https://developer.apple.com/fonts/ --header=Accept: */* --header=Connection: keep-alive --header=User-Agent: Mozilla/5.0 (Windows NT 6.1; rv:57.0.1) Gecko/20100101 Firefox/57.0.1 --header=Accept-Language: en-US;q=0.5,en;q=0.3 --header=Cache-Control: max-age=0 --header=Referer: https://google.com --header=Pragma: no-cache --header=Accept-Encoding: identity"""

        try:
            if has_internet_connection(self.url):
                self.download_thread = DownloadThread(
                    self.command, parent=self, base_path=self.path_text, url=self.url
                )
                self.download_thread.finished.connect(self.download_finished)
                self.download_thread.update_info.connect(self.update_download_info)
                self.start_time = datetime.now()
                self.download_thread.start()
        except ConnectionError:
            self.update_download_info(f"Unable connect to {self.url}")
        except Exception as e:
            logging.error(f"Error during download: {e}", exc_info=True)
            QMessageBox.information(
                self,
                title="Information",
                text=f"Error during download: \n{e}",
            )
            self.update_download_info(f"Error: {e}")

        if self.download_thread is not None:
            self.activeDownloadThreads.append(self.download_thread)
        self.main.go_to()

    def update_download_info(self, info: str = "") -> None:
        """
        Update the download information label with the provided text.

        Parameters:
            info (str): The text to be displayed on the download information label.

        Returns:
            None
        """
        self.main.lower_info_label.setText(info)

    def download_finished(self) -> None:
        """
        This function updates the lower info label in the main UI to display a message indicating that
        the download has finished. It also calls a function to show all websites in the main widget.

        Returns:
            None: This function does not return anything.
        """
        try:
            message = f"{get_domain(self.url)} fully saved. ADD IT BY PRESS + BUTTON"
        except IndexError:
            message = "Download complete. ADD IT BY PRESS + BUTTON"
        if (datetime.now() - self.start_time).total_seconds() < 1:
            message = (
                f"Possible {get_domain(self.url)} may have rejected the connection"
            )
        self.update_download_info(message)
        self.main.main_widget.show_all_websites()
        if self.download_thread in self.activeDownloadThreads:
            self.activeDownloadThreads.remove(self.download_thread)

    def select_download_directory(self) -> None:
        """
        Sets the path for saving files.

        This function opens a file dialog window to allow the user
        to choose a directory for saving files. If a directory is selected,
        the path_line_edit widget is updated with the selected directory path,
        and the 'Paths/download_path' setting is updated with the same.

        Returns:
        None
        """
        try:
            directory_from_settings = settings.value("Paths/download_path")
            selected_directory = QFileDialog.getExistingDirectory(
                self, "Choose folder", directory_from_settings
            )
            if selected_directory:
                self.path_text = selected_directory
                self.path_line_edit.setText(selected_directory)
                settings.setValue("Paths/download_path", selected_directory)
            else:
                self.path_line_edit.setText(directory_from_settings)
        except Exception as e:
            logging.error(f"Error selecting download directory: {e}")
            # Отображение сообщения об ошибке пользователю
            QMessageBox.critical(
                self,
                title="Error",
                text="An error occurred while selecting the download directory.",
            )
