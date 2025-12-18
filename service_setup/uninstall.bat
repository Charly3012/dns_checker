@echo off
set FOLDER=%~dp0
set PROJECT_ROOT=%FOLDER%..\
set NSSM="%FOLDER%nssm.exe"
set SERVICE_NAME=DnsChecker

%NSSM% stop %SERVICE_NAME% >nul 2>&1
%NSSM% remove %SERVICE_NAME% confirm >nul 2>&1

echo.
echo ===========================================
echo Finished process.
echo %SERVICE_NAME% deleted successfully.
echo ===========================================
pause