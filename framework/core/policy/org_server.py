from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from typing import Tuple


class OrgHTTPServer:
    def __init__(self, host: str, port: int, verifier):
        """
        verifier: callable(token: str) -> bool
        """
        self.host = host
        self.port = port
        self.verifier = verifier

    def serve(self) -> Tuple[str, int]:
        parent = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                if parsed.path == "/verify":
                    qs = parse_qs(parsed.query or "")
                    token = (qs.get("token") or [""])[0]
                    ok = bool(token) and parent.verifier(token)
                    self.send_response(200 if ok else 400)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    if ok:
                        self.wfile.write(b"<h3>Organization verified successfully.</h3>")
                    else:
                        self.wfile.write(b"<h3>Verification failed. Invalid or missing token.</h3>")
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                # suppress default stdout logging
                return

        httpd = HTTPServer((self.host, self.port), Handler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            httpd.server_close()
        return self.host, self.port