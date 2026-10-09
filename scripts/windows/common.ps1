# Shared helpers, dot-sourced by the other .ps1 scripts. Compatible with Windows PowerShell 5.1 and PowerShell 7.

$ErrorActionPreference = 'Stop'

function Read-Settings {
    $file = $env:MC_SETTINGS
    if (-not $file) { $file = Join-Path $PSScriptRoot 'settings.txt' }
    $s = @{}
    foreach ($line in Get-Content -LiteralPath $file) {
        if ($line -match '^\s*([A-Z_]+)\s*=(.*)$') { $s[$Matches[1]] = $Matches[2].Trim() }
    }
    return $s
}

$Settings = Read-Settings
$McDir = $Settings['MC_DIR']
$PhpExe = $Settings['PHP_EXE']
$WebPort = $Settings['WEB_PORT']
$DataDir = $Settings['MC_DATA']
if (-not $DataDir) { $DataDir = Join-Path $env:APPDATA 'MultiChain' }
if (-not $Chain) { $Chain = $Settings['CHAIN'] }   # a script's -Chain parameter wins
$ChainDir = Join-Path $DataDir $Chain
$Cli = Join-Path $McDir 'multichain-cli.exe'

function Write-Title([string]$Text) {
    Write-Host ''
    Write-Host ('=' * 70) -ForegroundColor DarkGray
    Write-Host " $Text" -ForegroundColor Yellow
    Write-Host ('=' * 70) -ForegroundColor DarkGray
}

# Runs multichain-cli with a raw Windows command line (so JSON written as "{\"a\":1}" reaches
# MultiChain intact on every PowerShell version). Prints the command and its output and
# returns the result text, or $null on error.
function Invoke-MC([string]$ArgLine, [switch]$Quiet) {
    if (-not $Quiet) { Write-Host "C:\> multichain-cli $Chain $ArgLine" -ForegroundColor Cyan }
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $Cli
    $psi.Arguments = "$Chain $ArgLine"
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $p = [System.Diagnostics.Process]::Start($psi)
    $errTask = $p.StandardError.ReadToEndAsync()
    $out = $p.StandardOutput.ReadToEnd().TrimEnd()
    $p.WaitForExit()
    $err = $errTask.Result
    if ($p.ExitCode -ne 0) {
        # stderr starts with the echoed request line, then the error text
        $msg = ($err -split "`r?`n" | Where-Object { $_ -and $_ -notmatch '^\{"method"' }) -join "`n"
        if (-not $Quiet) { Write-Host $msg -ForegroundColor Red }
        return $null
    }
    if (-not $Quiet -and $out) { Write-Host $out }
    return $out
}

function Test-NodeRunning {
    return [bool](Invoke-MC 'getinfo' -Quiet)
}

# Parses "name = value   # comment" lines of params.dat into a hashtable.
function Read-ParamsDat([string]$Path) {
    $p = [ordered]@{}
    foreach ($line in Get-Content -LiteralPath $Path) {
        if ($line -match '^([a-z0-9-]+)\s*=\s*(\S*)') { $p[$Matches[1]] = $Matches[2] }
    }
    return $p
}

# Parses key=value lines of multichain.conf into a hashtable.
function Read-Conf([string]$Path) {
    $c = @{}
    foreach ($line in Get-Content -LiteralPath $Path) {
        if ($line -match '^\s*([^#=\s]+)\s*=\s*(.*?)\s*$') { $c[$Matches[1]] = $Matches[2] }
    }
    return $c
}

function Stop-WithMessage([string]$Text) {
    Write-Host $Text -ForegroundColor Red
    exit 1
}

function Assert-ChainCreated {
    if (-not (Test-Path -LiteralPath (Join-Path $ChainDir 'params.dat'))) {
        Stop-WithMessage "Chain '$Chain' not found in $ChainDir. Run 01-create-chain.bat first."
    }
}

function Assert-NodeRunning {
    if (-not (Test-NodeRunning)) {
        Stop-WithMessage "Node '$Chain' is not running (or not ready yet). Run 02-start-node.bat and wait for 'Node ready.'"
    }
}
