"""Plain backend used behind the Apache reverse proxy (/proxy/ on the target).

This just serves ordinary HTML so the full stack (client -> Apache -> this
backend) runs end to end over Docker. Your team can extend or swap this
service out with your own content while researching the proxy path.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer

PAGE = b"""<!DOCTYPE html>
<html>
<head><title>ACW3 Backend</title></head>
<body>
<h1>Backend service</h1>
<p>Reached via the Apache reverse proxy at /proxy/.</p>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(PAGE)))
        self.end_headers()
        self.wfile.write(PAGE)

    def log_message(self, fmt, *args):
        print(f"[backend] {self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
