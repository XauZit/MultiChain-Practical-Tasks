#!/usr/bin/env bash
# Usage: crawl.sh <webroot> <php-port> <mock-port>
# Walks the web demo like a student would (new address, grant, label, issue, update, send, create stream,
# publish, view, filters) against mock_multichain.py and fails on any PHP notice/warning/error.
# Uses the local `php`; set PHPWASM=<dir with npm i @php-wasm/cli> to run the pages on PHP 8.4 instead.
# <webroot>/config.txt is pointed at the mock node for the run and restored afterwards.
set -u
ROOT=$1; WP=$2; MP=$3; TOOLS=$(cd "$(dirname "$0")" && pwd); LOGS=$(mktemp -d)
[ -f "$ROOT/config.txt" ] && mv "$ROOT/config.txt" "$LOGS/config.txt.orig"
printf "default.name=chain1 (mock)\ndefault.rpchost=127.0.0.1\ndefault.rpcsecure=0\ndefault.rpcport=%s\ndefault.rpcuser=multichainrpc\ndefault.rpcpassword=testpass\n" "$MP" > "$ROOT/config.txt"
python3 -I "$TOOLS/mock_multichain.py" "$MP" 2> "$LOGS/mock.log" & MOCK=$!
if [ -n "${PHPWASM:-}" ]; then
  python3 -I "$TOOLS/wasm_shim.py" "$WP" "$ROOT" "$PHPWASM" "$TOOLS/runner.php" > "$LOGS/php.log" 2>&1 & PHP=$!
else
  php -d display_errors=1 -d error_reporting=E_ALL -S 127.0.0.1:$WP -t "$ROOT" > "$LOGS/php.log" 2>&1 & PHP=$!
fi
trap 'kill $MOCK $PHP 2>/dev/null; rm -f "$ROOT/config.txt"; [ -f "$LOGS/config.txt.orig" ] && mv "$LOGS/config.txt.orig" "$ROOT/config.txt"' EXIT
sleep 1
B="http://127.0.0.1:$WP/"
stx() { curl -sS -d '{"method":"liststreams","params":["'"$1"'"]}' http://127.0.0.1:$MP/ | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"][0]["createtxid"])'; }
fails=0
check() { # name, curl args...
  local name=$1; shift
  local out; out=$(curl -sS "$@" | tr -d '\000')
  local errs; errs=$(printf '%s' "$out" | sed 's/<[^>]*>//g' | grep -E "Fatal error|Warning:|Deprecated:|Notice:|Uncaught|bg-danger" | sort -u | head -5)
  local errdiv; errdiv=$(printf '%s' "$out" | grep -o 'class="bg-danger"[^<]*<[^<]*' | head -3)
  [ -n "${EXPECT_RED:-}" ] && errdiv=""  # step whose correct outcome is a red message (e.g. filter blocks item)
  if [ -n "$errs$errdiv" ]; then echo "FAIL  $name"; printf '%s\n%s\n' "$errs" "$errdiv" | sed '/^$/d; s/^/      /'; fails=$((fails+1)); else echo "ok    $name"; fi
  LAST="$out"
}
expect() { # text, name, curl args...
  local text=$1; shift; check "$@"
  if printf '%s' "$LAST" | grep -q -- "$text"; then echo "      ✓ found: $text"; else echo "      ✗ MISSING: $text"; fails=$((fails+1)); fi
}
check "home (no chain)"            "$B"
check "node page"                  "$B?chain=default"
check "get new address"            "$B?chain=default" -d getnewaddress=1
A0=$(curl -sS -X POST -d '{"method":"getaddresses","params":[]}' http://127.0.0.1:$MP/ | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"][0])')
NEW=$(curl -sS -X POST -d '{"method":"getaddresses","params":[]}' http://127.0.0.1:$MP/ | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"][-1])')
echo "      admin=$A0 new=$NEW"
check "node page with new address" "$B?chain=default"
check "permissions page"           "$B?chain=default&page=permissions&address=$NEW"
check "grant send,receive"         "$B?chain=default&page=permissions" -d grantrevoke=1 -d operation=grant -d from=$A0 -d to=$NEW -d send=on -d receive=on
check "label page"                 "$B?chain=default&page=label&address=$A0"
check "set label"                  "$B?chain=default&page=label" -d setlabel=1 -d address=$A0 -d label=Admin
check "node page with label"       "$B?chain=default"
check "issue page"                 "$B?chain=default&page=issue"
check "issue asset (multipart)"    "$B?chain=default&page=issue" -F issueasset=1 -F from=$A0 -F to=$A0 -F name=asset1 -F qty=1000 -F units=0.01 -F key0=origin -F value0=lab
check "issue asset w/ file"        "$B?chain=default&page=issue" -F issueasset=1 -F from=$A0 -F to=$A0 -F name=asset3 -F qty=10 -F units=1 -F upload=@$TOOLS/mock_multichain.py
check "issue asset (urlencoded)"   "$B?chain=default&page=issue" --data-urlencode issueasset=1 --data-urlencode from=$A0 --data-urlencode to=$A0 --data-urlencode name=asset2 --data-urlencode qty=500 --data-urlencode units=1
check "issue page after issue"     "$B?chain=default&page=issue"
check "update page"                "$B?chain=default&page=update"
check "update asset"               "$B?chain=default&page=update" -F updateasset=1 -F issuetxid=$(curl -sS -X POST -d '{"method":"listassets","params":[]}' http://127.0.0.1:$MP/ | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"][0]["issuetxid"])') -F to=$A0 -F qty=10 -F key0=batch -F value0=2
check "issue page after update"    "$B?chain=default&page=issue"
check "send page"                  "$B?chain=default&page=send"
check "send asset"                 "$B?chain=default&page=send" -d sendasset=1 -d from=$A0 -d to=$NEW -d asset=asset2 -d qty=50
check "send asset w/ metadata"     "$B?chain=default&page=send" -d sendasset=1 -d from=$A0 -d to=$NEW -d asset=asset2 -d qty=5 -d metadata=note
check "node page after send"       "$B?chain=default"
check "create page"                "$B?chain=default&page=create"
check "create stream"              "$B?chain=default&page=create" -d createstream=1 -d from=$A0 -d name=stream1 -d open=on
expect "Successfully subscribed"  "subscribe stream1"      "$B?chain=default&page=view" -d "subscribe_$(stx stream1)=Subscribe"
check "publish page"               "$B?chain=default&page=publish"
check "publish text item"          "$B?chain=default&page=publish" -d publish=1 -d from=$A0 -d name=stream1 -d key=key1 -d text=hello
check "publish json item"          "$B?chain=default&page=publish" -d publish=1 -d from=$A0 -d name=stream1 -d key=key2 -d json='{"a":1}'
check "publish json to root"       "$B?chain=default&page=publish" -d publish=1 -d from=$A0 -d name=root -d key=k -d json='{"a":1}'
check "node page after json root"  "$B?chain=default"
check "publish file item"          "$B?chain=default&page=publish" -F publish=1 -F from=$A0 -F name=stream1 -F key=file -F upload=@$TOOLS/crawl.sh
check "publish offchain item"      "$B?chain=default&page=publish" -F publish=1 -F from=$A0 -F name=stream1 -F key=off -F text=x -F offchain=on
check "publish multi-key item"     "$B?chain=default&page=publish" -F publish=1 -F from=$A0 -F name=stream1 -F $'key=a\nb' -F text=two-keys
check "view streams"               "$B?chain=default&page=view"
check "view stream1"               "$B?chain=default&page=view&stream=$(stx stream1)"
check "view stream1 by key"        "$B?chain=default&page=view&stream=$(stx stream1)&key=key1"
check "view stream1 by publisher"  "$B?chain=default&page=view&stream=$(stx stream1)&publisher=$A0"
check "offer page"                 "$B?chain=default&page=offer"
check "accept page"                "$B?chain=default&page=accept"
check "txfilter page"              "$B?chain=default&page=txfilter"
check "streamfilter page"          "$B?chain=default&page=streamfilter"
FCODE='function filterstreamitem() { var item=getfilterstreamitem(); if (!item.data.json || item.data.json.a !== 1) return "a must be 1"; }'
expect "successfully compiled"    "streamfilter compile test" "$B?chain=default&page=streamfilter" --data-urlencode teststreamfiltercode=1 --data-urlencode "code=$FCODE"
expect "allowed this stream item" "streamfilter test, no callbacks" "$B?chain=default&page=streamfilter" --data-urlencode teststreamfilterpublish=1 --data-urlencode "code=$FCODE" --data-urlencode sendfrom=$A0 --data-urlencode stream=$(stx stream1) --data-urlencode keys=k1 --data-urlencode format=json --data-urlencode 'data={"a":1}'
EXPECT_RED=1 expect "blocked this stream item" "streamfilter test, callbacks" "$B?chain=default&page=streamfilter" --data-urlencode teststreamfilterpublish=1 --data-urlencode "code=$FCODE" --data-urlencode sendfrom=$A0 --data-urlencode stream=$(stx stream1) --data-urlencode keys=k1 --data-urlencode format=json --data-urlencode 'data={"a":2}' --data-urlencode callbacks=1
expect "Filter successfully created" "create stream filter"  "$B?chain=default&page=streamfilter" --data-urlencode createstreamfilter=1 --data-urlencode "code=$FCODE" --data-urlencode createfrom=$A0 --data-urlencode name=filter1
FTX=$(curl -sS -d '{"method":"liststreamfilters","params":[]}' http://127.0.0.1:$MP/ | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"][0]["createtxid"])')
check "approve page"               "$B?chain=default&page=approve&streamfilter=$FTX"
expect "Approval successfully changed" "approve stream filter" "$B?chain=default&page=approve&streamfilter=$FTX" -d approvestreamfilter=1 -d approvefrom=$A0 -d stream=$(stx stream1)
expect "Item successfully published" "publish blocked item" "$B?chain=default&page=publish" -F publish=1 -F from=$A0 -F name=stream1 -F key=blocked -F 'json={"a":2}'
expect "rejected by a stream filter" "view shows rejected item" "$B?chain=default&page=view&stream=$(stx stream1)&key=blocked"
expect "allowed this transaction" "txfilter raw test, no callbacks" "$B?chain=default&page=txfilter" --data-urlencode testtxfilterraw=1 --data-urlencode rawtx=00 --data-urlencode 'code=function filtertransaction() {}'
expect "Permissions successfully changed" "grant again"   "$B?chain=default&page=permissions" -d grantrevoke=1 -d operation=grant -d from=$A0 -d to=$NEW -d issue=on
expect "send, receive, issue"     "node shows new perms"   "$B?chain=default"
expect "Label successfully updated" "relabel after json"  "$B?chain=default&page=label" -d setlabel=1 -d address=$A0 -d label=Admin
expect "Admin"                    "node shows label"       "$B?chain=default"
expect "Admin"                    "view stream1 has label" "$B?chain=default&page=view&stream=$(stx stream1)"
expect "two-keys"                 "multi-key item shown"   "$B?chain=default&page=view&stream=$(stx stream1)&key=b"
expect "a&quot;:1\|&quot;a&quot;"      "json item shown"        "$B?chain=default&page=view&stream=$(stx stream1)&key=key2"
expect "Asset successfully issued" "issue asset4"          "$B?chain=default&page=issue" -F issueasset=1 -F from=$A0 -F to=$A0 -F name=asset4 -F qty=100 -F units=0.1 -F key0=origin -F value0=lab
expect "asset4"                   "issue page lists asset4" "$B?chain=default&page=issue"
expect "Asset successfully sent"  "send asset4"            "$B?chain=default&page=send" -d sendasset=1 -d from=$A0 -d to=$NEW -d asset=asset4 -d qty=7
expect "Stream successfully created" "create stream2"      "$B?chain=default&page=create" -d createstream=1 -d from=$A0 -d name=stream2 -d open=on
expect "Successfully subscribed"  "subscribe stream2"      "$B?chain=default&page=view" -d "subscribe_$(stx stream2)=Subscribe"
expect "Item successfully published" "publish to stream2"  "$B?chain=default&page=publish" -F publish=1 -F from=$A0 -F name=stream2 -F key=k1 -F text=hello-world
expect "hello-world"              "view stream2"           "$B?chain=default&page=view&stream=$(stx stream2)"
echo "TOTAL FAILURES: $fails"
