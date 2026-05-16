@echo off
setlocal

cd /d "%~dp0"

set "PORT=%~1"
if "%PORT%"=="" set "PORT=49152"

start "" "http://127.0.0.1:%PORT%/"
python "%~dp0server.py" %PORT%

pause
