"""Applies PHP 8.x compatibility fixes to a checkout of MultiChain/multichain-web-demo (commit 582476b)."""
import re, sys, pathlib

root = pathlib.Path(sys.argv[1])

def edit(name, pairs, regex=()):
    p = root / name
    s = p.read_text()
    for old, new in pairs:
        if old not in s:
            sys.exit('patch target not found in %s: %r' % (name, old))
        s = s.replace(old, new)
    for pat, rep in regex:
        s = re.sub(pat, rep, s)
    p.write_text(s)

# strlen()/htmlspecialchars() no longer accept null quietly; count() throws on null.
STRLEN_POST = (r"strlen\(@\$_POST\[([^\]]+)\]\)", r"strlen((string)@$_POST[\1])")
HTML_POST = (r"html\(\$_POST\[", r"html(@$_POST[")

edit('functions.php', [
    ("return htmlspecialchars($string);",
     "return htmlspecialchars(is_array($string) ? json_encode($string) : (string)$string);"),
    ("if (strlen($page))", "if (strlen((string)$page))"),
    ("if (strlen($link)) {", "if (strlen((string)$link)) {"),
    ("""				foreach ($items as $item)
					$multichain_labels[$item['publisher']]=pack('H*', $item['last']['data']);""",
     """				foreach ($items as $item) {
					$data=$item['last']['data'];
					if (is_string($data)) // label set by this demo, published as raw hex
						$multichain_labels[$item['publisher']]=pack('H*', $data);
					elseif (isset($data['text'])) // text item published to the root stream
						$multichain_labels[$item['publisher']]=$data['text'];
				}"""),
])
edit('index.php', [
    ("$chain=@$_GET['chain'];", "$chain=(string)@$_GET['chain'];"),
    ("""	if (strlen($chain))
		$name=@$config[$chain]['name'];""", """	if (strlen($chain))
		$name=(string)@$config[$chain]['name'];"""),
])
edit('page-default.php', [
    ("if (count(@$addresspermissions[$address]))", "if (!empty($addresspermissions[$address]))"),
])
for page in ('page-issue.php', 'page-update.php'):
    edit(page, [("if (strlen($upload_file)) {", "if (strlen((string)$upload_file)) {")],
         [STRLEN_POST, HTML_POST, (r"(?:@)?count\(@\$detailshistory\['@file'\]\)", "!empty($detailshistory['@file'])")])
edit('page-publish.php', [
    ("if (strlen($upload_file)) {", "if (strlen((string)$upload_file)) {"),
    ("if (strlen($_POST['json'])) {", "if (strlen((string)@$_POST['json'])) {"),
    ("if ($_POST['offchain'])", "if (@$_POST['offchain'])"),
], [HTML_POST])
edit('page-send.php', [("if (strlen($_POST['metadata']))", "if (strlen((string)@$_POST['metadata']))")], [HTML_POST])
edit('page-streamfilter.php', [
    ("'options' => $_POST['offchain'] ? 'offchain' : ''", "'options' => @$_POST['offchain'] ? 'offchain' : ''"),
    ("if ($_POST['callbacks'])", "if (@$_POST['callbacks'])"),  # unticked checkbox is not posted
    ("if (@count($filterkeystreams[$filter['createtxid']])) {", "if (!empty($filterkeystreams[$filter['createtxid']])) {"),
], [STRLEN_POST, HTML_POST])
edit('page-txfilter.php', [
    ("$showcallbacks=$_POST['sendcallbacks'];", "$showcallbacks=@$_POST['sendcallbacks'];"),
    ("$showcallbacks=$_POST['rawcallbacks'];", "$showcallbacks=@$_POST['rawcallbacks'];"),
], [STRLEN_POST, HTML_POST])
edit('page-label.php', [("html($labels[$address])", "html(@$labels[$address])")])
for page in ('page-create.php', 'page-permissions.php', 'page-offer.php', 'page-accept.php', 'page-approve.php', 'page-view.php'):
    edit(page, [], [STRLEN_POST, HTML_POST])
print('PHP 8 patches applied to', root)
