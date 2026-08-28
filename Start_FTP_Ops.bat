@echo off
TITLE FTP Ops Server

echo ======================================
echo       Starting FTP Ops Server...
echo ======================================
echo.
echo Please keep this window open while using the app.
echo You can minimize it, but closing it will stop the server.
echo.

:: Start the browser slightly delayed so the server has time to boot
start "" "http://127.0.0.1:8000"

:: Start the Django server
call venv\Scripts\python.exe manage.py runserver

pause
