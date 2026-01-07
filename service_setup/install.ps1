Param(
    [string]$PYTHON_EXE = ""
)

# Paths
$PROJECT_PATH = $PSScriptRoot
$NSSM = Join-Path -Path $PROJECT_PATH -ChildPath "nssm.exe"

#Service information
$SERVICE_NAME = "DnsChecker"

Write-Host "==========================================="
Write-Host "Installing $SERVICE_NAME..."
Write-Host "==========================================="

#Steap 1 - Detect python exe instance
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

# Step 2 - Install requirements 
Write-Host "[-] Installing python requirements..."
Try{
    $rawPath = Join-Path -Path $PROJECT_PATH -ChildPath "..\requirements.txt"
    $requirements_path = (Resolve-Path $rawPath -ErrorAction Stop).Path

    & $PYTHON_EXE -m pip install -qq -r $requirements_path
    if ($LASTEXITCODE -ne 0) {
        Throw "PIP fails with exit code: $LASTEXITCODE"
    }
    
    Write-Host "Dependencies install success." -ForegroundColor Green
}Catch{
    Write-Error "CRITICAL FAILURE installing dependencies."
    Write-Host "Error Details: $($_.Exception.Message)" -ForegroundColor Red
    Exit 1
}

#Step 3 - Install service 
Write-Host "[-] Installing service..."
& $NSSM stop $SERVICE_NAME 2> $null | Out-Null #Just in case :b
& $NSSM remove $SERVICE_NAME confirm 2> $null | Out-Null
& $NSSM install $SERVICE_NAME $PYTHON_EXE main.py 1> $null

#Set app directory to use config.json
$RawAppDirectory = Join-Path -Path $PROJECT_PATH -ChildPath "..\src" 
$AppDirectory = (Resolve-Path $RawAppDirectory -ErrorAction Stop).Path
& $NSSM set $SERVICE_NAME AppDirectory $AppDirectory 1> $null
Write-Host "App directory: $AppDirectory" -ForegroundColor Green

#Logs configuration
$LogsDirectory = Join-Path -Path $PROJECT_PATH -ChildPath "\logs"
if (-not (Test-Path -Path $LogsDirectory -PathType Container)) {
    & mkdir $LogsDirectory 1> $null
}

$Stdout_log = Join-Path -Path $LogsDirectory -ChildPath "nssm_out.log"
& $NSSM set $SERVICE_NAME AppStdout $Stdout_log 1> $null
$Stderr_log = Join-Path -Path $LogsDirectory -ChildPath "nssm_errors.log"
& $NSSM set $SERVICE_NAME AppStderr $Stderr_log 1> $null
& $NSSM set $SERVICE_NAME AppEnvironmentExtra PYTHONIOENCODING=utf-8 1> $null

& $NSSM start $SERVICE_NAME

Write-Host "==========================================="
Write-Host "Finished process."
Write-Host "Watch status with: $NSSM status $SERVICE_NAME"
Write-Host "==========================================="
