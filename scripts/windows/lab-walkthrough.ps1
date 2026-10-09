# Runs the common MultiChain lab commands one by one against a running node, printing each
# command exactly as you would type it in Command Prompt. Safe to re-run (skips what exists).
param([string]$Chain, [switch]$NoPause)
. (Join-Path $PSScriptRoot 'common.ps1')

function Step([string]$Title) {
    if (-not $NoPause -and $script:stepNo) { [void](Read-Host "`nPress Enter for the next step") }
    $script:stepNo++
    Write-Title "Step $($script:stepNo): $Title"
}

Assert-ChainCreated
Assert-NodeRunning

Step 'Node information'
Invoke-MC 'getinfo' | Out-Null

Step 'Blockchain parameters (same values as params.dat)'
Invoke-MC 'getblockchainparams' | Out-Null

Step 'Addresses in this node''s wallet - the first one is the admin (genesis) address'
$admin = @((Invoke-MC 'getaddresses') | ConvertFrom-Json)[0]
Write-Host "admin address = $admin" -ForegroundColor Green

Step 'Permissions of the admin address'
Invoke-MC "listpermissions all $admin" | Out-Null

Step 'Create a second address and grant it connect, send, receive'
$addresses = @((Invoke-MC 'getaddresses' -Quiet) | ConvertFrom-Json)
if ($addresses.Count -ge 2) {
    $user = $addresses[1]
    Write-Host "(reusing existing second address $user)" -ForegroundColor DarkGray
} else {
    $user = Invoke-MC 'getnewaddress'
}
Invoke-MC "grant $user connect,send,receive" | Out-Null
Invoke-MC "listpermissions connect,send,receive $user" | Out-Null

Step 'Issue an asset (asset1: 1000 units, smallest unit 0.01, open for issuemore)'
if (Invoke-MC 'listassets asset1' -Quiet) {
    Write-Host '(asset1 already exists - skipping issue)' -ForegroundColor DarkGray
} else {
    Invoke-MC "issue $admin ""{\""name\"":\""asset1\"",\""open\"":true}"" 1000 0.01" | Out-Null
}
Invoke-MC 'listassets asset1' | Out-Null
Invoke-MC 'gettotalbalances' | Out-Null

Step 'Send 100 asset1 to the second address and check its balance'
Invoke-MC "sendasset $user asset1 100" | Out-Null
Invoke-MC "getaddressbalances $user" | Out-Null

Step 'Issue 500 more units of asset1'
Invoke-MC "issuemore $admin asset1 500" | Out-Null
Invoke-MC 'gettotalbalances' | Out-Null

Step 'Create a stream (stream1, open to all writers) and subscribe'
if (Invoke-MC 'liststreams stream1' -Quiet) {
    Write-Host '(stream1 already exists - skipping create)' -ForegroundColor DarkGray
} else {
    Invoke-MC 'create stream stream1 true' | Out-Null
}
Invoke-MC 'subscribe stream1' | Out-Null

Step 'Publish items: raw hex, JSON and text'
Invoke-MC 'publish stream1 key1 48656c6c6f20576f726c64' | Out-Null
Invoke-MC 'publish stream1 key2 "{\"json\":{\"name\":\"Ali\",\"marks\":85}}"' | Out-Null
Invoke-MC 'publish stream1 key3 "{\"text\":\"MultiChain lab\"}"' | Out-Null

Step 'Read the stream back'
Invoke-MC 'liststreamitems stream1' | Out-Null
Invoke-MC 'liststreamkeyitems stream1 key2' | Out-Null
Invoke-MC 'liststreamkeys stream1' | Out-Null
Invoke-MC 'liststreampublishers stream1' | Out-Null

Step 'Blocks and network'
$height = Invoke-MC 'getblockcount'
Invoke-MC "getblock $height" | Out-Null
Invoke-MC 'getmempoolinfo' | Out-Null
Invoke-MC 'getpeerinfo' | Out-Null

Write-Title 'Done - every command above can be typed exactly as shown in Command Prompt'
