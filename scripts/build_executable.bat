@echo off
setlocal

rem Load variables
call set_variables.bat

rem Change directory
cd %PROJECT_PATH%

echo Creating .exe file with PyInstaller...
%PYINSTALLER_PATH% %MAIN_PATH% --clean --onefile

rem Check for error
if %errorlevel% neq 0 (
    echo An error occured while creating executable .exe-file
    exit /b %errorlevel%
)

echo Copying executable into %PROJECT_PATH%\%PROJECT_NAME%
xcopy %PROJECT_PATH%\dist\main.exe %PROJECT_PATH%\%PROJECT_NAME% /y || (exit /b %errorlevel%)

echo Executable created successfully!
endlocal

rem Do not pause if batch file was called by an other batch file
if "%1" neq "nopause" pause
