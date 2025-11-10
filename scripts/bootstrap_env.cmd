@echo off
REM Bootstrap the Python virtual environment and install dependencies (Windows cmd)
REM Usage: run this from the repository root: scripts\bootstrap_env.cmd

SET REPO_ROOT=%~dp0..
PUSHD %REPO_ROOT%

REM Create venv if missing
IF NOT EXIST "%CD%\.venv\Scripts\python.exe" (
    echo Creating virtual environment in %CD%\.venv
    python -m venv .venv
) ELSE (
    echo Virtual environment already exists at %CD%\.venv
)

REM Use venv python directly to avoid activation quirks
SET VENV_PY=%CD%\.venv\Scripts\python.exe
IF NOT EXIST "%VENV_PY%" (
    echo ERROR: Could not find venv python at %VENV_PY%
    POPD
    EXIT /B 1
)

echo Upgrading pip, wheel and setuptools...
"%VENV_PY%" -m pip install --upgrade pip wheel setuptools

echo Installing project requirements from ControlResiduos\requirements.txt ...
"%VENV_PY%" -m pip install -r ControlResiduos\requirements.txt

echo Running import checks (scripts\check_venv_imports.py)...
"%VENV_PY%" scripts\check_venv_imports.py

echo Bootstrap completed. To activate the venv in this shell run:
echo    .venv\Scripts\activate

POPD
PAUSE
