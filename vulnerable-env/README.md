# ACW3 Target Environment (Group P1-6)

A minimal Apache HTTP Server 2.4.68 target (fixed in 2.4.69) for the three approved CVEs.
This folder sets up the **server only** — WebDAV, digest auth, and a reverse proxy enabled,
matching the affected version and the preconditions each CVE record lists. It does not
include exploit scripts; per the spec, use the official CVE record and any online guide to
work out the actual identification/exploitation steps yourselves.

## Vulnerabilities in this environment

| CVE | Component | Severity | CVSS | Weakness (CWE) | Official record |
|---|---|---|---|---|---|
| CVE-2026-93546 | Apache mod_dav_fs | High | 8.8 | CWE-190 (Integer overflow) | https://www.cve.org/CVERecord?id=CVE-2026-93546 |
| CVE-2026-73636 | Apache mod_auth_digest | High | 8.1 | CWE-294 (Auth bypass by capture-replay) | https://www.cve.org/CVERecord?id=CVE-2026-73636 |
| CVE-2026-63686 | Apache mod_xml2enc | High | 7.5 | CWE-476 (NULL pointer dereference) | https://www.cve.org/CVERecord?id=CVE-2026-63686 |

**Total CVSS: 24.4** (report minimum is 20). Vendor advisory for all three:
https://httpd.apache.org/security/vulnerabilities_24.html

Preconditions already wired up in `conf/httpd-vuln.conf` so your environment matches each
record:
- **mod_dav_fs (CVE-2026-93546):** WebDAV is on, and `labuser` has write access to `/dav/`.
- **mod_auth_digest (CVE-2026-73636):** `AuthDigestNonceLifetime` is set to 0, as the record requires.
- **mod_xml2enc (CVE-2026-63686):** `/proxy/` reverse-proxies to a backend you still need to
  stand up yourselves — see the CVE record for what response triggers the NULL pointer
  dereference.

## What each CVE lets an attacker do

Plain-English impact of each vulnerability wired up in this lab.

### CVE-2026-93546 — `mod_dav_fs` integer overflow (CVSS 8.8)

**What it is:** A size-counter bug in Apache's WebDAV code. When it parses the XML body
of a `PROPPATCH` / `PROPFIND` request, a length field wraps past `INT_MAX` and the server
writes out of bounds.

**What you can do with it:**
- **Crash the Apache worker on demand** — one crafted `PROPPATCH` kills the child process
  with SIGSEGV. Repeat it and `/dav/` is effectively down (DoS).
- **Potentially execute code** — CWE-190 integer overflows that corrupt heap state are a
  classic path to RCE. The CVSS 8.8 vector (I:H, A:H) says the server considers
  code-execution plausible, not just a crash.
- **Pivot into the box** — if RCE lands, you're running as the Apache user inside the
  container, with reach into the backend and the Docker network.

**Catch:** you need a valid DAV account first — hence the pairing with CVE-2026-73636.

**Think of it as:** *"Any authenticated DAV user can crash or compromise the web server."*

### CVE-2026-73636 — `mod_auth_digest` nonce replay (CVSS 8.1)

**What it is:** With `AuthDigestNonceLifetime 0`, the server-issued nonce never expires.
HTTP Digest auth is designed so the hashed credential in the `Authorization:` header stops
working after a few minutes — here it works forever.

**What you can do with it:**
- **Steal a session without ever cracking the password** — one Wireshark capture of a
  legitimate `GET /dav/` from a real user hands you a reusable `Authorization: Digest ...`
  header.
- **Impersonate that user indefinitely** — replay the header a day or a week later, same
  result; the server treats you as `labuser`.
- **Read everything that user can read** — browse the entire WebDAV share, download Q3
  financials, client briefs, meeting notes, etc.
- **Write things that user can write** (with a bit more work — capture a `PUT`/`DELETE`
  instead of a `GET`, since the digest `response` hash includes the HTTP method).
- **Chain into CVE-2026-93546** — now you have the authenticated session the DAV
  overflow needs.

**Catch:** needs network position to sniff traffic (any plain-HTTP LAN, open Wi-Fi,
mirrored switch port, compromised router).

**Think of it as:** *"Anyone who sniffs a single legitimate request becomes that user,
forever."*

### CVE-2026-63686 — `mod_xml2enc` NULL pointer dereference (CVSS 7.5)

**What it is:** The charset-conversion filter Apache applies to proxied HTML responses
dereferences a NULL pointer when the body's declared charset and actual byte encoding
disagree (or when the body ends mid-multibyte sequence).

**What you can do with it:**
- **Crash the Apache worker remotely with no authentication** — just send
  `GET /proxy/?charset=utf-16&encode_as=utf-8&truncate=7`. Segfault.
- **Take `/proxy/` offline for everyone** — loop that request and the reverse-proxied path
  stays unavailable for the duration of the attack; httpd keeps respawning children into
  the same crash.
- **No login required, no network foothold required** — anyone who can reach the HTTP port
  can do it. This is the "scariest" of the three in exposure terms even though its CVSS
  is the lowest, because the attacker bar is literally zero.

**Catch:** availability-only (CVSS A:H, C:N, I:N) — no data theft, no code execution.
Pure denial of service.

**Think of it as:** *"Any random person on the internet can keep your proxied path down."*

### How the three fit together

| CVE | Attacker needs | Attacker gets | Attacker trajectory |
|---|---|---|---|
| **73636** (digest replay) | sniff one request | a free `labuser` session | **Foothold** — "I am now a logged-in user" |
| **93546** (DAV overflow) | an authenticated DAV user | server crash, maybe RCE | **Escalation** — "I can break or own the server" |
| **63686** (xml2enc deref) | nothing | `/proxy/` unavailable | **Independent DoS** — "I can keep your site down" |

So the lab tells two attack stories: an **unauthenticated DoS** of `/proxy/` is one path;
the **digest-replay + DAV-overflow combo** is a second path that goes from
no-credentials-at-all to data theft and possible server compromise. Both come from the
same unpatched Apache 2.4.68 build — upgrading to 2.4.69 closes all three.

Full walkthroughs for each CVE live in [`guides/`](guides/).

## Quick start

1. Make sure Docker Desktop is running.
2. From this folder, build and start both containers:

   ```
   cd vulnerable-env
   docker compose up -d --build
   ```

3. Create the digest-auth user (first run only). Apache's `htdigest` only
   prompts interactively for a password, so generate the credentials file
   directly instead (format: `username:realm:MD5(username:realm:password)`):

   ```
   printf '%s' 'labuser:acw3-dav:labpass123' | md5sum | awk '{print "labuser:acw3-dav:" $1}' > conf/digest.passwd
   ```

   This creates user `labuser` / password `labpass123` in the `acw3-dav`
   realm (must match `AuthName` in `conf/httpd-vuln.conf`). Change the
   password as you like, just keep the three-part format.

4. If the digest file changed after the target container already started,
   recreate it so Apache picks up the new credentials:

   ```
   docker compose up -d --force-recreate target
   ```

5. Open:
   - Site: http://localhost:8080/ (served from `public/` — the Fieldstone Docs portal)
   - WebDAV share (digest auth): http://localhost:8080/dav/ (served from `www/`)
   - Reverse-proxied path: http://localhost:8080/proxy/
   - Team CVE map (internal reference): http://localhost:8080/cve-map.html

6. Check both containers are up: `docker compose ps`
7. Tear down when done: `docker compose down`

## Verified working (2026-10-22)

- `docker compose up -d --build` builds and starts cleanly.
- `GET /` → 200, `GET /dav/` without credentials → 401, `GET /proxy/` → 200 (backend reachable).
- Digest auth: correct credentials → 200, wrong password → 401.
- WebDAV write: `PUT /dav/<file>` → 201, `GET` back → 200, `DELETE` → 204.

## Notes

- Run this only on an isolated lab network or VM, never exposed to the internet.
- No PoC is published for any of these three records (CISA lists exploitation as "none" for
  all of them), so identification/exploitation is on your team to work out from the
  advisory and record above — exactly as the spec asks.
- Remember to keep screenshots for the report appendix, and check with the instructors that
  these three CVEs are approved before you start.
