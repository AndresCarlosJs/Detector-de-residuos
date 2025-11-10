# Virtual environment (venv) — quick guide

This repository contains a working virtual environment created at the project root: `.venv`.
Below are quick commands and notes to recreate or activate it on Windows using `cmd.exe`.

## Activate the venv (quick)
Run the activation helper (from the project root or anywhere):

```bat
# from repo root
scripts\activate_venv.cmd
```

This calls `.venv\Scripts\activate.bat` for you and prints tips. Run it in a `cmd.exe` session (it pauses at the end so you can see output).

## Create the venv (if missing)
If you need to recreate the environment from scratch:

```bat
cd /d C:\Users\Isaac\Downloads\Proyecto_Construccion
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip wheel setuptools
pip install -r ControlResiduos\requirements.txt
```

Notes:
- The repository includes a `ControlResiduos\requirements.txt` file with the packages used by the app. Installing it may download many packages (including `torch` and `opencv`).
- For project isolation, you may prefer to create the venv inside the subproject `ControlResiduos` instead of at the repo root. Example:

```bat
cd /d C:\Users\Isaac\Downloads\Proyecto_Construccion\ControlResiduos
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Verify imports (helper script)
A helper script exists at `scripts\check_venv_imports.py` which checks main modules used by the project (cv2, torch, flask, PIL, ultralytics, fpdf). Run after activation:

```bat
python scripts\check_venv_imports.py
```

## Bootstrap script (recommended)
To make the environment creation repeatable for other machines, use the included bootstrap script for Windows (`cmd.exe`):

```bat
scripts\bootstrap_env.cmd
```

What it does:
- Creates `.venv` at the repo root if missing
- Upgrades pip/wheel/setuptools inside the venv
- Installs packages from `ControlResiduos\requirements.txt`
- Runs `scripts\check_venv_imports.py` to validate critical modules

Run it from a `cmd.exe` prompt opened at the repository root. The script is idempotent and safe to re-run.

## Recommendations
- Use the activation script `scripts\activate_venv.cmd` when working in `cmd.exe`.
- If you use PowerShell, call the venv `Activate.ps1` instead:

```powershell
Set-Location C:\Users\Isaac\Downloads\Proyecto_Construccion
.\.venv\Scripts\Activate.ps1
```

- Add the venv path to your VS Code workspace settings for automatic interpreter discovery.

If you want, I can recreate the `.venv` inside `ControlResiduos` (recommended for cross-project cleanliness). Just tell me to proceed and I'll do it (I will remove the current root `.venv`, create `ControlResiduos\.venv`, install requirements and run the import-check script).