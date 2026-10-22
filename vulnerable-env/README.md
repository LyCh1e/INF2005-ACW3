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
   - Site: http://localhost:8080/
   - WebDAV share (digest auth): http://localhost:8080/dav/
   - Reverse-proxied path: http://localhost:8080/proxy/

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
