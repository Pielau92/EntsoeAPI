@echo off
setlocal

rem Load variables
call set_variables.bat

rem Change directory
cd %PROJECT_PATH%

echo Creating .exe file with PyInstaller...
%PYINSTALLER_PATH% %MAIN_PATH% --clean --onefile --paths=%SRC_PATH% --add-binary "%VENV_PATH%/DLLs/pyexpat.pyd;dlls" --add-binary "%VENV_PATH%/Library/bin/libexpat.dll;." --add-binary "%VENV_PATH%/Library/bin/libcrypto-3-x64.dll;." --add-binary "%VENV_PATH%/Library/bin/libssl-3-x64.dll;." --add-binary "%VENV_PATH%/Library/bin/liblzma.dll;." --add-binary "%VENV_PATH%/Library/bin/LIBBZ2.dll;." --add-binary "%VENV_PATH%/Library/bin/sqlite3.dll;." --add-binary "%VENV_PATH%/Library/bin/tk86t.dll;." --add-binary "%VENV_PATH%/Library/bin/tcl86t.dll;." --add-binary "%VENV_PATH%/Library/bin/ffi.dll;."

rem Check for error
if %errorlevel% neq 0 (
    echo An error occured while creating executable .exe-file
    exit /b %errorlevel%
)

echo Copying executable into %PROJECT_PATH%\%PROJECT_NAME%
xcopy %PROJECT_PATH%\dist\main.exe %PROJECT_PATH%\src\%PROJECT_NAME% /y || (exit /b %errorlevel%)

echo Executable created successfully!
endlocal

rem Do not pause if batch file was called by an other batch file
if "%1" neq "nopause" pause
