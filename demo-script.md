# ACW3 Demo Script — Team P6-6

**Date:** Thursday 12 Nov 2026, 4:00–6:00 PM  
**Venue:** E2-05-05  
**Time budget:** 20 min presentation + 10 min Q&A = 30 min total  
**Rule:** One attempt per vulnerability. No setup time. All members must present.

---

## Pre-demo checklist (before your slot — do this in the corridor)

- [ ] Laptop plugged in + external display tested
- [ ] Docker Desktop running
- [ ] Lab started: `.\run.ps1` or `./run.sh` — both containers show "Up"
- [ ] Verify http://localhost:8080/ loads in browser
- [ ] Terminal windows pre-arranged (3 tabs: one per CVE)
- [ ] Fallback video ready on desktop (in case of catastrophic failure)

---

## Run sheet (20 minutes)

### PART 1 — Environment Setup & Architecture (Chiyung + Jerry + Nicholas, ~7.5 min)

The three support members each take ~2.5 min to explain one aspect of how the
lab was built and why, before the CVE owners demo their exploits.

---

#### 1A — Why Docker, and how the lab starts (Chiyung, ~2.5 min)

**Chiyung** opens, standing at the laptop:

> "Good afternoon, we are Team P6-6. Before we run the exploits, we want to
> walk you through how we built this lab and why we made the choices we did."

> "The ACW3 spec says: no setup time, one attempt, and the environment must be
> on our own laptop. That ruled out anything slow or fragile. We chose Docker
> Compose over traditional VMs for four reasons."

Show `docker-compose.yml` on screen (or the relevant terminal):

> "First — startup speed. A VM takes minutes to boot. Our containers start in
> seconds. On demo day, the lab is already running before we walk in."

> "Second — reproducibility. The target image is pinned to `httpd:2.4.68`, the
> exact last affected version. Every `docker compose up --build` produces the
> same environment. There is no state drift, no 'it worked on my machine'
> problem."

> "Third — portability. Six team members on Windows, macOS, and Linux all
> clone the same Git repo and run one command. No multi-gigabyte VM images to
> pass around."

> "Fourth — safety. We set a 512 MB memory cap on the target container. One
> of our exploits causes the Apache worker to consume gigabytes of RAM — without
> the cap, it would freeze the demo laptop. The cap makes the crash happen
> cleanly in seconds while protecting the host."

Show the containers running:

```
docker compose ps
```

> "Two containers — `acw3-target` running stock Apache 2.4.68, and `acw3-backend`,
> a small Python server behind the reverse proxy. Both are up."

---

#### 1B — How the Apache config enables each CVE (Nicholas, ~2.5 min)

**Jerry** takes over, shows `httpd-vuln.conf` on screen:

> "We didn't modify Apache's source code or replace any modules. We wrote one
> config overlay file — `httpd-vuln.conf` — that gets included on top of the
> default Apache config at startup. Each block maps directly to a CVE's
> precondition."

Point to lines 8–14:

> "First, the module loads. We enable `mod_dav` and `mod_dav_fs` for the WebDAV
> attack surface, `mod_auth_digest` for HTTP Digest authentication, and
> `mod_proxy_html` plus `mod_xml2enc` for the reverse proxy's charset filter.
> These are all stock Apache modules — we didn't add anything custom."

Point to lines 16–46 (the `/dav/` Directory block):

> "The `/dav/` directory block enables WebDAV with write access for the
> digest-authenticated user `labuser`. This is the precondition for
> CVE-2026-93546 — the attacker needs an authenticated WebDAV session
> to send the crafted PROPPATCH."

> "Inside the same block: `AuthDigestNonceLifetime 0`. This is the specific
> misconfiguration that CVE-2026-73636 requires. It means digest auth nonces
> never expire, so a captured Authorization header can be replayed indefinitely
> after a server restart."

Point to lines 48–63 (the `/proxy/` Location block):

> "Finally, `/proxy/` is configured as a reverse proxy to the backend container.
> The output filter `proxy-html` with `ProxyHTMLCharsetOut *` activates
> mod_xml2enc's charset conversion — this is where the NULL-pointer dereference
> in CVE-2026-63686 lives."

> "One config file, three attack surfaces, all traceable to the official CVE
> records."

---

#### 1C — The two-container architecture and why it matters (Jerry, ~2.5 min)

**Nicholas** takes over, shows the browser with http://localhost:8080/:

> "This is what the target looks like — Fieldstone Docs, a fictional internal
> company portal. We built this themed front-end so the demo tells a story
> instead of just showing raw terminal output. The instructors can see what the
> 'company' is and why each endpoint exists."

Navigate to http://localhost:8080/proxy/ in the browser:

> "This is the News Mirror page — served through the reverse proxy. When you
> visit `/proxy/`, Apache fetches this page from the backend container and
> passes it through the charset transcoding filter. The backend is not
> accessible from outside — it sits on an internal Docker network with no
> published ports. The only way to reach it is through Apache's proxy rule."

Navigate to http://localhost:8080/dav/ (shows 401 or login prompt):

> "And this is the Shared Drive — the WebDAV endpoint behind Digest auth.
> Two of our three CVEs target this path: one exploits the authentication,
> the other exploits the file-property handling."

Show the architecture visually (gesture or point to the browser):

> "So the architecture is: attacker hits localhost:8080 — Apache serves the
> homepage, the WebDAV shared drive, and proxies requests to the backend.
> Three attack surfaces on one server, which mirrors what a real pentest
> would find on an unpatched Apache."

> "Our total CVSS score across the three CVEs is 24.4 — above the required 20.
> All three are High severity, giving us the 100% multiplier."

Show the summary:

> | #   | CVE            | Component       | CVSS | Owner   |
> | --- | -------------- | --------------- | ---- | ------- |
> | 1   | CVE-2026-93546 | mod_dav_fs      | 8.8  | Han     |
> | 2   | CVE-2026-73636 | mod_auth_digest | 8.1  | Raynard |
> | 3   | CVE-2026-63686 | mod_xml2enc     | 7.5  | Jolene  |

> "Now Han will demonstrate the first exploit — the highest severity."

---

### PART 2 — CVE-2026-93546: mod_dav_fs namespace overflow (Han, ~4 min)

**Han** takes the keyboard:

> "CVE-2026-93546 is an integer overflow in mod_dav_fs — the WebDAV file-system
> backend. CVSS 8.8, High. CWE-190: integer overflow."

**Explain (30 sec):**

> "When a PROPPATCH request declares thousands of XML namespace declarations,
> a size counter in the property-database handling overflows. This causes O(n²)
> memory blowup — the worker tries to allocate gigabytes from a small payload
> and gets OOM-killed."

**Run the exploit (2 min):**

```
python cve93546_han_mod_dav_fs.py
```

> "The control PROPPATCH with one namespace returns 207 — normal.
> Now the attack: 45,000 namespaces, about 844 KB of XML."

Wait ~5-6 seconds for the crash:

> "ConnectionError — the worker consumed so much memory it hit the 512 MB cap
> and was killed."

```
docker inspect --format "OOMKilled={{.State.OOMKilled}}" acw3-target
```

> "Docker confirms OOMKilled=true. The service recovers automatically, but
> repeated attacks would cause sustained denial of service."

**Remediation (30 sec):**

> "Upgrade to Apache 2.4.69. Additionally, set LimitXMLRequestBody to cap
> XML payload size, and use container memory limits to protect the host."

---

### PART 3 — CVE-2026-73636: mod_auth_digest nonce replay (Raynard, ~4 min)

**Raynard** takes the keyboard:

> "CVE-2026-73636 is an authentication bypass via nonce replay. CVSS 8.1, High.
> CWE-294: capture-replay."

**Explain (30 sec):**

> "Digest auth uses nonces to prevent replay attacks. With NonceLifetime set
> to 0, nonces never expire. When the server restarts, it loses track of which
> nonce-counts were already used. A captured Authorization header can be replayed."

**Run the exploit (2.5 min):**

Step 1 — Capture the victim's auth header:

```
curl -v --digest -u labuser:labpass123 http://localhost:8080/dav/ 2>&1 | grep "> Authorization:"
```

> "Victim authenticates — I've captured their header. In a real attack, this
> comes from Wireshark or tcpdump."

Step 2 — Naive replay returns 401 with stale=true:

> "Immediate replay fails — the nonce-count was used. But notice: stale=true,
> not 'nonce expired.' The nonce itself is still valid."

Step 3 — Graceful restart + replay:

```
docker exec acw3-target httpd -k graceful
```

_(wait 3 seconds)_

```
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: [header]" http://localhost:8080/dav/
```

> "HTTP 200. Full access to the shared drive without the password."

**Remediation (30 sec):**

> "Upgrade to Apache 2.4.69. Remove NonceLifetime 0 — use the default 300 seconds.
> Better yet, switch to Basic auth over TLS so credentials can't be sniffed."

---

### PART 4 — CVE-2026-63686: mod_xml2enc NULL-pointer dereference (Jolene, ~4 min)

**Jolene** takes the keyboard:

> "CVE-2026-63686 is a NULL-pointer dereference in mod_xml2enc. CVSS 7.5, High.
> CWE-476. This one is unauthenticated — no login needed."

**Explain (30 sec):**

> "When Apache proxies a response, mod_xml2enc converts the charset. If the
> conversion fails with an incomplete multi-byte sequence, the function returns
> APR_INCOMPLETE — error 70008. But the code checks for APR_EINCOMPLETE — 20022.
> The mismatch causes a fall-through that NULLs a pointer and crashes the worker."

**Run the exploit (2 min):**

Baseline:

```
curl -s http://localhost:8080/proxy/ -o /dev/null -w "baseline: %{http_code}\n"
```

> "Proxy works normally — 200."

Attack:

```
curl -s "http://localhost:8080/proxy/?charset=big5&encode_as=cp500&body=AAAAAAA" -o /dev/null -w "attack: %{http_code}\n"
```

> "HTTP 200 but curl exits with code 18 — transfer closed. The worker crashed
> mid-response."

Evidence:

```
docker compose logs target | grep -E "70008|Segmentation"
```

> "Error 70008 — the mismatched constant — followed by Segmentation fault 11.
> The NULL dereference is confirmed."

**Remediation (30 sec):**

> "Upgrade to 2.4.69. The fix corrects the constant and adds a return after
> the default handler. As a workaround, disable mod_xml2enc where it's not needed."

---

## Q&A preparation (10 min)

### Likely questions and who answers them

| Question                                                 | Primary   | Backup    |
| -------------------------------------------------------- | --------- | --------- |
| "Why did you choose these 3 CVEs?"                       | Nicholas  | Jerry     |
| "How did you build the lab environment?"                 | Chiyung   | Jerry     |
| "Why Docker instead of VMs?"                             | Chiyung   | Nicholas  |
| "What is the CVSS vector for CVE-X?"                     | CVE owner | Nicholas  |
| "Could these be exploited remotely over the internet?"   | CVE owner | Chiyung   |
| "What does APR_INCOMPLETE vs APR_EINCOMPLETE mean?"      | Jolene    | Jerry     |
| "Why does the nonce replay need a server restart?"       | Raynard   | Nicholas  |
| "Why 45,000 namespaces? What happens with fewer?"        | Han       | Chiyung   |
| "What if the attacker doesn't have WebDAV credentials?"  | Han       | Raynard   |
| "How does the memory cap affect the mod_dav_fs exploit?" | Han       | Chiyung   |
| "Is there a way to detect these attacks in production?"  | Nicholas  | Chiyung   |
| "What tools did you use?"                                | Chiyung   | CVE owner |

### Prepared answers for key questions

**"Why these 3 CVEs?"**

> All three target the same Apache 2.4.68 server, which let us build one
> unified Docker lab. They cover three different attack categories — memory
> corruption, authentication bypass, and crash-based DoS — and together
> score 24.4, well above the 20-point minimum. All are High severity for
> the 100% multiplier.

**"Why Docker?"**

> Instant startup (seconds, not minutes), reproducible from a single file,
> portable across 6 team members on different OSes, and safe — the memory
> cap on the container protects the host during the mod_dav_fs exploit.

**"Could these be exploited remotely?"**

> CVE-93546 and 73636 require authentication, so the attacker needs valid
> credentials first. CVE-63686 is unauthenticated — anyone who can reach the
> proxy endpoint can crash workers. All three would work over a network.

**"What AI tools did you use?"**

> We used Claude Code to help verify our exploits against the lab, write
> PoC scripts, cross-check CVE records, and structure the report. All
> exploitation was run by us on our own lab. The GenAI usage is declared
> in the report per SIT policy.

---

## Timing guide

| Segment                     | Duration | Cumulative | Speaker(s) |
| --------------------------- | -------- | ---------- | ---------- |
| 1A — Why Docker             | 2:30     | 2:30       | Chiyung    |
| 1B — Apache config          | 2:30     | 5:00       | Nicholas   |
| 1C — Architecture & portal  | 2:30     | 7:30       | Jerry      |
| CVE-93546 (mod_dav_fs)      | 4:00     | 11:30      | Han        |
| CVE-73636 (mod_auth_digest) | 4:00     | 15:30      | Raynard    |
| CVE-63686 (mod_xml2enc)     | 4:00     | 19:30      | Jolene     |
| Q&A                         | 10:00    | 29:30      | Everyone   |

**Jerry keeps time.** Hold up fingers at 1-min and 30-sec marks for each presenter.
If any segment runs over, cut the current speaker and move on.

---
