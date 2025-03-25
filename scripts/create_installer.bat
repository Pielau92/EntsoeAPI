@echo off
setlocal

rem -------------------- BEFORE YOU START --------------------

rem Make sure you have created Inno Setup script beforehand
rem use the Inno Setup Compiler for this (install Inno Setup if need be)

rem ----------------------------------------------------------

rem Load variables
call set_variables.bat

rem Build executable .exe-file
call build_executable.bat nopause

rem If needed, copy files from one location to another (use/copy&paste example below)
rem example: xcopy PATH1 PATH2 /y

if %errorlevel% neq 0 (
    echo An error occured while creating executable .exe-file, setup aborted!
    exit /b %errorlevel%
)

rem Create installation .setup-file
echo Creating installation .setup-file with Inno Setup...

cd %PROJECT_PATH%
%INNO_SETUP_EXE_PATH% %INNO_SETUP_SCRIPT_PATH%

if %errorlevel% neq 0 (
    echo An error occured while creating installation .setup-file
    exit /b %errorlevel%
)

echo installation .setup file created successfully!
endlocal
pause
