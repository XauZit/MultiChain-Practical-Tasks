<?php
// Executes one web-demo request under the CLI: argv[1] is a JSON request description written by wasm_shim.py
$req=json_decode(file_get_contents($argv[1]), true);
$_GET=$req['get']; $_POST=$req['post']; $_FILES=$req['files'];
$_REQUEST=array_merge($_GET, $_POST);
$_SERVER['REQUEST_METHOD']=$req['method'];
chdir($req['root']);
include $req['root'].'/'.$req['script'];
