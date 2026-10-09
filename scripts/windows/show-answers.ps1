# Prints the answers to the sample exam question, read from the chain's own files
# (and from the running node, when it is up).
param([string]$Chain)
. (Join-Path $PSScriptRoot 'common.ps1')

Assert-ChainCreated
$paramsPath = Join-Path $ChainDir 'params.dat'
$confPath = Join-Path $ChainDir 'multichain.conf'
$p = Read-ParamsDat $paramsPath

Write-Title "Files in $ChainDir"
Get-ChildItem -LiteralPath $ChainDir | Select-Object Mode, LastWriteTime, Length, Name | Format-Table -AutoSize | Out-String | Write-Host

Write-Title 'Key lines of params.dat (exactly as written by multichain-util)'
Select-String -LiteralPath $paramsPath -Pattern '^(chain-name|protocol-version|default-network-port|default-rpc-port|mining-diversity|target-block-time|anyone-can-connect|setup-first-blocks) ' |
    ForEach-Object { Write-Host $_.Line }

Write-Title 'ANSWERS - Creating a MultiChain Instance'
$rows = @(
    @('chain-name', $p['chain-name']),
    @('protocol-version', $p['protocol-version']),
    @('network-port', "$($p['default-network-port'])   (default-network-port)"),
    @('rpc-port', "$($p['default-rpc-port'])   (default-rpc-port = network-port - 1)"),
    @('consensus mechanism', "Round-robin permissioned mining with 'mining diversity' (Proof-of-Authority style), mining-diversity = $($p['mining-diversity'])")
)
foreach ($r in $rows) { Write-Host ('  {0,-20}: {1}' -f $r[0], $r[1]) -ForegroundColor Green }

Write-Host ''
Write-Host '  Other default parameters worth mentioning:'
foreach ($k in 'target-block-time', 'anyone-can-connect', 'anyone-can-send', 'anyone-can-receive', 'anyone-can-mine',
               'root-stream-name', 'setup-first-blocks', 'admin-consensus-admin', 'maximum-block-size') {
    Write-Host ('    {0,-24} = {1}' -f $k, $p[$k])
}

if (Test-Path -LiteralPath $confPath) {
    $c = Read-Conf $confPath
    Write-Host ''
    Write-Host "  multichain.conf: rpcuser = $($c['rpcuser']), rpcpassword = $($c['rpcpassword'])"
}

if (Test-NodeRunning) {
    Write-Title 'Live values from the running node (getinfo)'
    $info = (Invoke-MC 'getinfo' -Quiet) | ConvertFrom-Json
    foreach ($k in 'chainname', 'version', 'protocolversion', 'port', 'nodeaddress', 'blocks', 'connections') {
        Write-Host ('  {0,-16}: {1}' -f $k, $info.$k)
    }
} else {
    Write-Host ''
    Write-Host '  (Node not running - start it with 02-start-node.bat to also see live getinfo values.)' -ForegroundColor DarkGray
}
