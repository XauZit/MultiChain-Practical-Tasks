# Stops the node and deletes the chain's data folder so you can practise "multichain-util create" again.
param([string]$Chain)
. (Join-Path $PSScriptRoot 'common.ps1')

if (-not (Test-Path -LiteralPath $ChainDir)) {
    Write-Host "Nothing to delete: $ChainDir does not exist."
    return
}
Write-Host "This permanently deletes $ChainDir (blocks, wallet keys, params.dat)." -ForegroundColor Red
$answer = Read-Host "Type the chain name ($Chain) to confirm"
if ($answer -ne $Chain) { Write-Host 'Cancelled.'; return }

if (Test-NodeRunning) {
    Invoke-MC 'stop' | Out-Null
    for ($i = 0; $i -lt 30 -and (Test-NodeRunning); $i++) { Start-Sleep -Seconds 1 }
    Start-Sleep -Seconds 2   # let multichaind release its files
}
Remove-Item -LiteralPath $ChainDir -Recurse -Force
Write-Host "Deleted $ChainDir" -ForegroundColor Green
