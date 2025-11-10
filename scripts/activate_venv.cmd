@echo off
rem Activate the project's virtual environment located at the repository root (.venv)
rem Usage: run this file from cmd.exe (double-click won't keep the shell open)

set SCRIPT_DIR=%~dp0
rem PROJECT_ROOT is parent dir of scripts\
set PROJECT_ROOT=%SCRIPT_DIR%..
set VENV_ACTIVATE=%PROJECT_ROOT%\.venv\Scripts\activate.bat

if exist "%VENV_ACTIVATE%" (
  echo Activating virtualenv at %PROJECT_ROOT%\.venv
  call "%VENV_ACTIVATE%"
  echo Virtualenv activated. To verify, run: python -V
) else (
  echo No virtualenv found at %PROJECT_ROOT%\.venv
  echo To create one, run the following in a cmd.exe shell:
  echo.
  echo    python -m venv "%PROJECT_ROOT%\.venv"
  echo    call "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
  echo    python -m pip install --upgrade pip wheel setuptools
  echo    pip install -r ControlResiduos\requirements.txt
)

pause
