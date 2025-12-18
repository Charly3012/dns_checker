@echo off
:: ===========================================
:: CONFIGURACIÓN - SET UP YOUR PYTHON PATH
:: ===========================================
:: Ecample: C:\Python312\python.exe or venv path
::set PYTHON_EXE=
set PYTHON_EXE="C:\Users\carlo\AppData\Local\Programs\Python\Python314\python.exe"
:: ===========================================

set FOLDER=%~dp0
set PROJECT_ROOT=%FOLDER%..\
set NSSM="%FOLDER%nssm.exe"
set MAIN_PY="%FOLDER%..\src\main.py"
set SERVICE_NAME=DnsChecker

echo ===========================================
echo Installing %SERVICE_NAME%...
echo ===========================================

:: Python path validation
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Missing variable PYTHON_EXE
    echo.
    echo Please, open this .bat file with a text editor
    echo and set up your PYTHON_EXE variable
    echo.
    echo "You must set up python path"
    pause
    exit /b
)

:: If exist, just in case :b
%NSSM% stop %SERVICE_NAME% >nul 2>&1
%NSSM% remove %SERVICE_NAME% confirm >nul 2>&1

:: Install
%NSSM% install %SERVICE_NAME% "%PYTHON_EXE%" main.py
%NSSM% set %SERVICE_NAME% AppDirectory "%PROJECT_ROOT%src"

:: Just in case again :bb
%NSSM% set %SERVICE_NAME% AppEnvironmentExtra PYTHONIOENCODING=utf-8
if not exist "%FOLDER%logs" mkdir "%FOLDER%logs"
%NSSM% set %SERVICE_NAME% AppStdout "%FOLDER%logs\nssm_out.log"
%NSSM% set %SERVICE_NAME% AppStderr "%FOLDER%logs\nssm_errors.log"

@REM D:\dns-checker-prueba\dns_checker\service_setup\..\service_setup\logs\nssm_out.log

:: Start
%NSSM% start %SERVICE_NAME%

echo.
echo ===========================================
echo Finished process.
echo Watch status with: nssm status %SERVICE_NAME%
echo ===========================================
pause