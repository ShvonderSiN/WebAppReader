@echo off
chcp 65001
setlocal enabledelayedexpansion

:: Путь к директории виртуального окружения
set "VENV_PATH=..\..\venv"

:: Активация виртуального окружения
call "%VENV_PATH%\Scripts\activate.bat"

:: Задайте переменные для удобства
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
