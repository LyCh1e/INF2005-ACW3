## 1. Assignment Constraints

The ACW3 spec requires a **live 30-minute demo** with no setup time and only one attempt. This drove three hard requirements:

- **Instant startup** — no manual installs on demo day
- **Complete isolation** — real exploits must not leak to the university network
- **Reproducible** — tear down and rebuild from scratch in under a minute

**One command:** `docker compose up -d --build` brings the entire lab up. `docker compose down` tears it down cleanly.

---

## 2. Why Docker Over VMs

| Docker | Traditional VM |
|---|---|
| Starts in **seconds** | Takes **minutes** to boot |
| Compose file fits in a **Git repo** — all 6 members clone and run | Multi-GB `.ova` image distribution |
| **Pinned base image** (`httpd:2.4.68`) — every build is identical | State drifts over time |
| Minimal overhead — Apache runs on host kernel | 2–4 GB RAM + virtual disk per guest OS |

**Trade-off:** Containers share the host kernel, but all three CVEs are application-level bugs in Apache userspace — the container boundary is sufficient.

---

## 3. One Target, Three CVEs

All three CVEs affect **Apache HTTP Server 2.4.68** (fixed in 2.4.69). Running them on one server:

- **Reduces failure points** — one container vs three separate machines
- **Mirrors reality** — an unpatched server has *every* vulnerability in that version, not just one

Pinned to the stock `httpd:2.4.68` Docker Hub image — no source patches, no custom builds.

---

## 4. Two Containers — Target + Backend

CVE-2026-63686 (mod_xml2enc crash) needs Apache to reverse-proxy a backend response. We built a small Python HTTP server as a second container:

- **`acw3-target`** — Apache 2.4.68, exposed on port 8080
- **`acw3-backend`** — Python server, no published ports, internal network only (`labnet`)

The backend accepts query parameters (`charset=`, `encode_as=`, `truncate=`) to shape responses that trigger the crash. Reachable only through Apache's `/proxy/` path.

---

## 5. Apache Configuration

One overlay config file — `conf/httpd-vuln.conf` — wires up all three CVE preconditions:

| CVE | Config | What It Enables |
|---|---|---|
| **CVE-2026-93546** (mod_dav_fs) | WebDAV on `/dav/`, digest auth, writable directory | Authenticated PROPPATCH triggers integer overflow |
| **CVE-2026-73636** (mod_auth_digest) | `AuthDigestNonceLifetime 0` | Nonces never expire — captured headers replay indefinitely |
| **CVE-2026-63686** (mod_xml2enc) | `/proxy/` reverse proxy with `ProxyHTMLCharsetOut *` | Charset conversion activates the NULL dereference path |

Single file = full traceability. Anyone can open it and map each block to its CVE.

---

## 6. Safety Guardrails

- **Memory cap:** `mem_limit: 512m` on the target container — the PROPPATCH payload amplifies ~1 MB into gigabytes; the cap keeps the demo laptop safe
- **Network isolation:** Internal Docker bridge (`labnet`), backend has no port mappings, target exposes only `localhost:8080`
- **No real data:** Every document, name, and company in the environment is fabricated
