@echo off
setlocal

cd /d "%~dp0"

set "PORT=%~1"
if "%PORT%"=="" set "PORT=49152"

python "%~dp0server.py" %PORT% --open

pause
