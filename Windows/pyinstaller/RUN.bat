@echo off
chcp 65001
setlocal enabledelayedexpansion

:: Путь к директории виртуального окружения
set "VENV_PATH=..\..\venv"

:: Проверка существования виртуального окружения
if not exist "%VENV_PATH%" (
    echo Создание виртуального окружения...
    python -m venv "%VENV_PATH%"
    if %ERRORLEVEL% neq 0 (
        echo Не удалось создать виртуальное окружение.
        goto end
    )
)

:: Активация виртуального окружения
call "%VENV_PATH%\Scripts\activate.bat"

:: Обновление pip
python -m pip install --upgrade pip

:: Установка зависимостей из файла requirements.txt
echo Установка зависимостей...
python -m pip install -r ..\..\requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Не удалось установить зависимости.
    goto end
)

:: Установка PyInstaller
echo Установка PyInstaller...
python -m pip install pyinstaller
if %ERRORLEVEL% neq 0 (
    echo Не удалось установить PyInstaller.
    goto end
)

:: Активация виртуального окружения
call "%VENV_PATH%\Scripts\activate.bat"

::   Переменные для удобства
set "SPEC_FILE=windows.spec"
set "DIST_DIR=.\dist\webappreader"
set "SRC_DIR=.\dist\webappreader\_internal\src"
set "WGET_EXE=.\dist\webappreader\_internal\wget.exe"

:: Вызов PyInstaller для сборки приложения
python -OO -m PyInstaller --noconfirm  %SPEC_FILE%

:: Проверка на успешное выполнение предыдущей команды
if %ERRORLEVEL% neq 0 (
    echo Сборка не удалась, проверьте вывод консоли на наличие ошибок.
    goto end
)

:: Перемещение каталога и файла в директорию распределения
echo Перемещение файлов...

if not exist "%DIST_DIR%" (
    echo Директория распределения не найдена: %DIST_DIR%
    goto end
)

:: Перемещение каталога src с помощью robocopy
:: robocopy "%SRC_DIR%" "%DIST_DIR%\src" /E /MOVE

:: Перемещение файла wget.exe
:: move /Y "%WGET_EXE%" "%DIST_DIR%\"

:end
pause
endlocal
