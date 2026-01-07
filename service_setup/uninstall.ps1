Param(
    [switch]$PreserveLogs
)

# Paths
$PROJECT_PATH = $PSScriptRoot
$NSSM = Join-Path -Path $PROJECT_PATH -ChildPath "nssm.exe"
$NSSM_LOGS_DIRECTORY = Join-Path -Path $PROJECT_PATH -ChildPath "\logs"
$APPLICATION_SERVICE_LOG = Join-Path -Path $PROJECT_PATH -ChildPath "..\src\service.log" 

#Service information
$SERVICE_NAME = "DnsChecker"

Try{
    & $NSSM stop $SERVICE_NAME 1> $null
    & $NSSM remove $SERVICE_NAME confirm 1> $null
    if ($LASTEXITCODE -ne 0) {
        Throw "Some fails trying uninstall $SERVICE_NAME. May be the service don't exist"
    }
}Catch{
    Write-Error "FAILURE uninstalling dependencies."
    Write-Host "Error Details: $($_.Exception.Message)" -ForegroundColor Red
    Exit 1
}

#Clean logs 
if($PreserveLogs){
    Write-Host "[-] PreserveLogs flag detected. Skipping logs deletion."
}else{
    Write-Host "[-] Cleaning logs..."
    if (Test-Path -Path $NSSM_LOGS_DIRECTORY) {
        Try {
            Remove-Item -Path $NSSM_LOGS_DIRECTORY -Recurse -Force -ErrorAction Stop
            Write-Host "NSSM logs directory deleted." -ForegroundColor Gray
        } Catch {
            Write-Warning "Could not delete NSSM logs folder. It might be in use."
        }
    }
    
    if (Test-Path -Path $APPLICATION_SERVICE_LOG) {
        Try {
            Remove-Item -Path $APPLICATION_SERVICE_LOG -Force -ErrorAction Stop
            Write-Host "Application log file deleted." -ForegroundColor Gray
        } Catch {
            Write-Warning "Could not delete application log file."
        }
    }
}

Write-Host "==========================================="
Write-Host "Finished process."
Write-Host "$SERVICE_NAME deleted successfully"
Write-Host "==========================================="

