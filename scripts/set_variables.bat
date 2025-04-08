rem ---------------FILL OUT THE FOLLOWING VARIABLES MANUALLY---------------

rem Name of Inno Setup Script
set INNO_SETUP_SCRIPT_NAME=DUMMY.iss

rem Name of Project
set PROJECT_NAME=DUMMY

rem Are you using miniconda3 or anaconda3?
set CONDA=miniconda3

rem Name of your virtual environment (for main modules)
set VENV_NAME=DUMMY

rem ---------------DO NOT CHANGE BATCH FILE AFTER THIS LINE----------------

rem Set path variables

for %%i in ("%CD%\..") do set PROJECT_PATH=%%~fi
for %%i in ("%CD%\..") do set PROJECT_NAME=%%~nxi
set MAIN_PATH=%PROJECT_PATH%\%PROJECT_NAME%\main.py
set CONDA_PATH=%USERPROFILE%\%CONDA%
set VENV_PATH=%CONDA_PATH%\envs\%VENV_NAME%
set PYTHON_PATH=%VENV_PATH%\python.exe
set PYINSTALLER_PATH=%VENV_PATH%\Scripts\pyinstaller.exe
set INNO_SETUP_EXE_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
set INNO_SETUP_SCRIPT_PATH=%CD%\%INNO_SETUP_SCRIPT_NAME%
