## 1. Assignment Constraints

Requirements:

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

## 4. CVE Selection Rationale

All three CVEs were chosen from the module-approved CVE list (`INF2005-ACW3-CVE-List.pdf`). Together they demonstrate three distinct vulnerability classes — memory corruption, authentication bypass, and denial of service — while sharing a single Apache 2.4.68 target, which keeps the lab simple and realistic.

| CVE | Module | Weakness | CVSS | Why we chose it |
|---|---|---|---|---|
| **CVE-2026-93546** | `mod_dav_fs` | CWE-190 — Integer overflow | 8.8 (High) | A PROPPATCH with thousands of XML namespace declarations overflows a size counter, causing O(n²) memory blow-up and worker SIGSEGV. Shows how a single authenticated request can crash a service and corrupt on-disk data — a textbook availability + integrity impact. |
| **CVE-2026-73636** | `mod_auth_digest` | CWE-294 — Capture-replay | 8.1 (High) | When `AuthDigestNonceLifetime` is set to `0`, nonces never expire, letting an attacker replay a sniffed `Authorization: Digest` header indefinitely — no password cracking needed. Demonstrates a configuration-driven authentication bypass and chains naturally with CVE-2026-93546 (a replayed session grants WebDAV write access). |
| **CVE-2026-63686** | `mod_xml2enc` | CWE-476 — NULL pointer dereference | 7.5 (High) | A charset mismatch between a proxied backend's declared encoding and the actual body bytes triggers an unhandled `APR_INCOMPLETE` return code, setting a context pointer to NULL and crashing the worker. Requires no authentication — any external client can hit the proxy path — illustrating an unauthenticated remote DoS. |

The three form a complementary set: CVE-2026-73636 (sniff credentials) enables CVE-2026-93546 (authenticated write-path crash), while CVE-2026-63686 shows that even unauthenticated users can take down a worker through a different module. This lets the report cover the full identify → exploit → chain → remediate cycle the assignment requires.

---

## 5. Two Containers — Target + Backend

CVE-2026-63686 (mod_xml2enc crash) needs Apache to reverse-proxy a backend response. We built a small Python HTTP server as a second container:

- **`acw3-target`** — Apache 2.4.68, exposed on port 8080
- **`acw3-backend`** — Python server, no published ports, internal network only (`labnet`)

The backend accepts query parameters (`charset=`, `encode_as=`, `truncate=`) to shape responses that trigger the crash. Reachable only through Apache's `/proxy/` path.

---

## 6. Apache Configuration

One overlay config file — `conf/httpd-vuln.conf` — wires up all three CVE preconditions:

| CVE | Config | What It Enables |
|---|---|---|
| **CVE-2026-93546** (mod_dav_fs) | WebDAV on `/dav/`, digest auth, writable directory | Authenticated PROPPATCH triggers integer overflow |
| **CVE-2026-73636** (mod_auth_digest) | `AuthDigestNonceLifetime 0` | Nonces never expire — captured headers replay indefinitely |
| **CVE-2026-63686** (mod_xml2enc) | `/proxy/` reverse proxy with `ProxyHTMLCharsetOut *` | Charset conversion activates the NULL dereference path |

Single file = full traceability. Anyone can open it and map each block to its CVE.

---

## 7. Safety Guardrails

- **Memory cap:** `mem_limit: 512m` on the target container — the PROPPATCH payload amplifies ~1 MB into gigabytes; the cap keeps the demo laptop safe
- **Network isolation:** Internal Docker bridge (`labnet`), backend has no port mappings, target exposes only `localhost:8080`
- **No real data:** Every document, name, and company in the environment is fabricated
