"""HTTP front for PHP-in-WASM: each request runs runner.php once via php-wasm-cli. Usage: wasm_shim.py <port> <webroot> <php-wasm-dir> <runner.php>"""
import email.parser, email.policy, json, os, subprocess, sys, tempfile, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT, ROOT, WASM, RUNNER = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
CLI = os.path.join(WASM, 'node_modules', '.bin', 'php-wasm-cli')

class H(BaseHTTPRequestHandler):
    def handle_any(self):
        url = urllib.parse.urlsplit(self.path)
        script = url.path.lstrip('/') or 'index.php'
        get = dict(urllib.parse.parse_qsl(url.query, keep_blank_values=True))
        post, files, tmp = {}, {}, tempfile.mkdtemp(dir=WASM)
        if self.command == 'POST':
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            ctype = self.headers.get('Content-Type', '')
            if ctype.startswith('multipart/form-data'):
                msg = email.parser.BytesParser(policy=email.policy.HTTP).parsebytes(
                    b'Content-Type: ' + ctype.encode() + b'\r\n\r\n' + body)
                for part in msg.iter_parts():
                    name = part.get_param('name', header='content-disposition')
                    filename = part.get_filename()
                    payload = part.get_payload(decode=True)
                    if filename is not None:
                        path = os.path.join(tmp, 'upload-' + name)
                        open(path, 'wb').write(payload)
                        files[name] = {'name': filename, 'type': part.get_content_type(), 'tmp_name': path,
                                       'error': 0, 'size': len(payload)}
                    else:
                        post[name] = payload.decode()
            else:
                post = dict(urllib.parse.parse_qsl(body.decode(), keep_blank_values=True))
        req = os.path.join(tmp, 'req.json')
        json.dump({'get': get, 'post': post, 'files': files, 'method': self.command, 'root': ROOT, 'script': script}, open(req, 'w'))
        r = subprocess.run([CLI, '-d', 'error_reporting=-1', '-d', 'display_errors=1', '-d', 'html_errors=1', RUNNER, req],
                           cwd=WASM, env=dict(os.environ, PHP='8.4'), capture_output=True)
        out = r.stdout + r.stderr
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(out)))
        self.end_headers()
        self.wfile.write(out)
    do_GET = do_POST = handle_any
    def log_message(self, *a):
        pass

HTTPServer(('127.0.0.1', PORT), H).serve_forever()
