@echo off
setlocal

cd /d "%~dp0"
if not "%PYGETDATE_QUERY%"=="" (
    python "%~dp0pyGetDate.py" "%PYGETDATE_QUERY%"
) else (
    python "%~dp0pyGetDate.py" %*
)

if "%~1"=="" if "%PYGETDATE_QUERY%"=="" pause
