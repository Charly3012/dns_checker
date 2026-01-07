Param(
    [string]$PYTHON_EXE = ""
)

#Paths
$PROJECT_PATH = $PSScriptRoot
$NSSM = Join-Path -Path $PROJECT_PATH -ChildPath "nssm.exe"

#Service information
$SERVICE_NAME = "DnsChecker"

Write-Host "===========================================" 
Write-Host "Updating $SERVICE_NAME..." 
Write-Host "===========================================" 

Write-Host "`nWARNING: All manual changes made to the server's .py files will be lost." -ForegroundColor Red
$Confirmation = Read-Host "Are you sure? (Y/N)"
if ($Confirmation -notmatch "^[yYsS]$") {
    Write-Host "Update cancelled." -ForegroundColor Yellow
    Exit 0
}

#Detect python exe instance
Write-Host "[-] Finding python..."
Try {
    if([string]::IsNullOrWhiteSpace($PYTHON_EXE)){
        Write-Host "Python path auto-detection"
        $PythonExeFromPython = python -c "import sys; print(sys.executable)"
        $PYTHON_EXE = $PythonExeFromPython
    }
    Write-Host "Python found: $PYTHON_EXE" -ForegroundColor Green
}
Catch {
    if([string]::IsNullOrWhiteSpace($PYTHON_EXE)){
        Throw "Error. Can't find python in system PATH. You must to add absolute path in ps1 script in PYTHON_EXE param. (example: .\install.ps1 C:\path\to\python)"
    }else{
        Throw "Error. Can't find python in system with the param $PYTHON_EXE. "
    }
}

#Update from github
Write-Host "[-] Cleaning up local changes (.py) and stopping the service..."
git restore .
& $NSSM stop $SERVICE_NAME 2> $null | Out-Null

Write-Host "[-] Download changes from respository..."
git pull origin main --ff-only

if ($LASTEXITCODE -ne 0) {
    Write-Host "CRITICAL: Error doing git pull." -ForegroundColor Red
    & $NSSM start $SERVICE_NAME 
    Exit 1
}


Write-Host "[-] Running the installer to refresh dependencies and paths..."
& "$PSScriptRoot\install.ps1" -PYTHON_EXE $PYTHON_EXE


Write-Host "==========================================="
Write-Host "Update completed successfully"
Write-Host "Watch status with: $NSSM status $SERVICE_NAME"
Write-Host "==========================================="