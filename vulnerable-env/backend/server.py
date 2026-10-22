"""Backend used behind the Apache reverse proxy (/proxy/ on the target).

Serves ordinary HTML by default so the full stack (client -> Apache -> this
backend) runs end to end over Docker. It also accepts a few query parameters
so the team can shape the response (declared charset, actual byte encoding,
truncation, transfer-encoding) while researching what response the
`proxy-html` / mod_xml2enc filter chain needs to see for CVE-2026-63686.
This is a *test harness*, not an exploit: it only varies otherwise-ordinary
HTTP response properties. Working out the exact trigger condition is still
on the team, per the CVE record and the Apache 2.4.68->2.4.69 changelog.

Query parameters on GET /:
  charset=<name>     Charset declared in the Content-Type header
                      (default: utf-8). Try values httpd's xml2enc/iconv
                      support, e.g. utf-8, iso-8859-1, utf-16, shift_jis.
  encode_as=<name>    Charset the body bytes are *actually* encoded with
                      (default: same as `charset`). Set this different from
                      `charset` to send a mismatched/declared-vs-actual
                      encoding, which is the general shape of input that
                      charset-conversion filters mis-handle.
  truncate=<n>        Cut the encoded body to its first n bytes, useful for
                      producing a response that ends mid multi-byte sequence.
  chunked=1           Send the body using chunked transfer-encoding instead
                      of Content-Length.
  content_type=<ct>   Override the MIME type portion of Content-Type
                      (default: text/html, so the proxy-html filter applies).

Examples once the stack is up:
  curl "http://localhost:8080/proxy/?charset=utf-16&encode_as=utf-8"
  curl "http://localhost:8080/proxy/?charset=utf-8&truncate=5"
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

DEFAULT_BODY = """<!DOCTYPE html>
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
        params = parse_qs(urlparse(self.path).query)

        declared_charset = params.get("charset", ["utf-8"])[0]
        actual_charset = params.get("encode_as", [declared_charset])[0]
        content_type = params.get("content_type", ["text/html"])[0]
        truncate = params.get("truncate", [None])[0]
        chunked = params.get("chunked", ["0"])[0] == "1"

        try:
            body = DEFAULT_BODY.encode(actual_charset, errors="replace")
        except LookupError:
            # Unknown codec name - fall back but keep it visible in the response.
            body = f"<!-- unknown encode_as charset: {actual_charset} -->\n".encode(
                "utf-8"
            ) + DEFAULT_BODY.encode("utf-8", errors="replace")

        if truncate is not None:
            try:
                body = body[: int(truncate)]
            except ValueError:
                pass

        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset={declared_charset}")

        if chunked:
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()
            self._write_chunked(body)
        else:
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def _write_chunked(self, body, chunk_size=16):
        for i in range(0, len(body), chunk_size):
            chunk = body[i : i + chunk_size]
            self.wfile.write(f"{len(chunk):x}\r\n".encode("ascii"))
            self.wfile.write(chunk)
            self.wfile.write(b"\r\n")
        self.wfile.write(b"0\r\n\r\n")

    def log_message(self, format, *args):
        print(f"[backend] {self.address_string()} - {format % args}")


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
