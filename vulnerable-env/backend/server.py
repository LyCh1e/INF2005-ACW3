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
<html lang="en">
<head>
<meta charset="utf-8">
<title>Fieldstone News Mirror</title>
<style>
 body { font-family: Georgia, "Times New Roman", serif; max-width: 760px;
        margin: 36px auto; padding: 0 18px; color: #1b1f24; line-height: 1.55; }
 header { border-bottom: 2px solid #0f1a2b; padding-bottom: 10px; margin-bottom: 24px; }
 header h1 { margin: 0; font-size: 1.6em; letter-spacing: 0.3px; }
 header .sub { color: #5a6372; font-size: 0.9em; margin-top: 4px; }
 article { padding: 18px 0; border-bottom: 1px solid #e2e5ea; }
 article:last-child { border-bottom: none; }
 article h2 { margin: 0 0 4px; font-size: 1.18em; }
 article .byline { color: #5a6372; font-size: 0.85em; margin-bottom: 8px; }
 article p { margin: 0 0 8px; }
 .tag { display: inline-block; background: #eef1f5; color: #22508f;
        font-size: 0.75em; padding: 1px 7px; border-radius: 10px;
        font-family: sans-serif; }
 footer { color: #5a6372; font-size: 0.85em; margin-top: 24px;
          border-top: 1px solid #e2e5ea; padding-top: 10px; }
</style>
</head>
<body>
<header>
  <h1>Fieldstone News Mirror</h1>
  <div class="sub">Public feed, resynced hourly &middot; last sync 2026-10-22 14:48 SGT</div>
</header>

<article>
  <h2>Port of Singapore clears record container volume for third quarter</h2>
  <div class="byline">Reuters wire &middot; 22 Oct 2026 &middot; <span class="tag">economy</span></div>
  <p>
    PSA handled 10.9 million twenty-foot equivalent units between July and
    September, up 4.2 percent year-on-year, the port authority said on
    Wednesday. The result was helped by a rebound in intra-Asia transshipment
    traffic and a steadier flow of goods out of mainland Chinese factories.
  </p>
  <p>
    Analysts cautioned that the Q4 outlook remains tied to how quickly
    retailers in the United States and Europe draw down inventories ahead of
    the holiday season.
  </p>
</article>

<article>
  <h2>Cyber agency flags fresh batch of Apache HTTP Server advisories</h2>
  <div class="byline">The Register &middot; 22 Oct 2026 &middot; <span class="tag">security</span></div>
  <p>
    The Apache Software Foundation published updates to httpd 2.4 covering
    issues in <code>mod_dav_fs</code>, <code>mod_auth_digest</code>, and
    <code>mod_xml2enc</code>. Administrators running the 2.4.68 build are
    being asked to move to 2.4.69 or later; shops that still rely on
    WebDAV with digest auth are first in line to patch.
  </p>
</article>

<article>
  <h2>Fieldstone-related brief: platform migration to run through Q4</h2>
  <div class="byline">Internal wire &middot; 21 Oct 2026 &middot; <span class="tag">company</span></div>
  <p>
    The platform team will stand up a staging mirror of the public news
    service by 27 Oct so Arcwell's integration lead can validate the
    end-to-end flow. The current mirror at <code>/proxy/</code> keeps
    serving in the meantime, with a known rendering issue when the
    upstream returns a mismatched charset.
  </p>
</article>

<article>
  <h2>MRT Thomson-East Coast Line extension opens two new stations</h2>
  <div class="byline">Channel News Asia &middot; 20 Oct 2026 &middot; <span class="tag">transport</span></div>
  <p>
    Commuters on the Thomson-East Coast Line can now board at the two new
    eastern stations that opened to passengers over the weekend. Service
    frequency on the full line has been adjusted; LTA says peak-hour trains
    will run every 2 minutes 45 seconds.
  </p>
</article>

<footer>
  Fieldstone News Mirror &middot; resynced from upstream once per hour.
  Not an original news source; links point to the publishers' own sites.
</footer>
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
