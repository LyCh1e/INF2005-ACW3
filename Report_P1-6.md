# Vulnerabilities Assessments and Remediation
## INF2005 Cyber Security Fundamentals — Assessed Coursework 3 (ACW3)

**Team:** P1-6 · **Target build:** Apache HTTP Server 2.4.68 (self-built local Docker lab) · **Date:** 9 November 2026

> *Formatting note for submission:* export this document to PDF in **11-pt Calibri**. The body (§1–§6) is sized to the **10-page limit**; the cover page, references, and appendix are excluded from that count per the brief. Replace every `[PLACEHOLDER: …]` marker before submission.

---

### Team page

| Full name | Student ID | Role |
|---|---|---|
| [PLACEHOLDER: name] | [PLACEHOLDER: ID] | Lead — CVE-2026-93546 (mod_dav_fs) |
| [PLACEHOLDER: name] | [PLACEHOLDER: ID] | CVE-2026-73636 (mod_auth_digest) |
| [PLACEHOLDER: name] | [PLACEHOLDER: ID] | CVE-2026-63686 (mod_xml2enc) |
| [PLACEHOLDER: name] | [PLACEHOLDER: ID] | Environment & reproducibility engineering |
| [PLACEHOLDER: name] | [PLACEHOLDER: ID] | Remediation & reporting |
| [PLACEHOLDER: name] | [PLACEHOLDER: ID] | [role] |

**Module:** INF2005 Cyber Security Fundamentals · **Coursework:** ACW3 — Vulnerabilities Assessments and Remediation · **Lab group / team:** P1-6 · **Submission date:** 9 November 2026.

### Declaration of originality and AI usage

We declare that this report is our own work, that all team members contributed to the pen-testing and its documentation, and that it has not been submitted for any other assessment.

**GenAI-use disclosure (per SIT policy on GenAI use in assessments).** A generative-AI coding assistant (Anthropic Claude, via Claude Code) was used to: **verify** the CVE-2026-93546 exploit against the local lab and identify why the original payload did not work; **author** the reproducibility PoC script (`poc_dav_overflow.py`) and the `mem_limit` safe-demo hardening; **cross-check** the official CVE records; and **draft and structure** this report from the team's outline and verified findings. All exploitation was run by the team against the team's own isolated lab; all results reported as "verified" were observed by the team, and all outstanding items are disclosed as such. The team reviewed, edited, and is responsible for the final content.
[PLACEHOLDER: adjust the GenAI wording above to match exactly what each member used, per module policy.]

By signing below, all team members confirm the declaration and the GenAI disclosure above.

| Full name | Student ID | Signature | Date |
|---|---|---|---|
| [PLACEHOLDER: name] | [PLACEHOLDER: ID] | | |
| [PLACEHOLDER: name] | [PLACEHOLDER: ID] | | |
| [PLACEHOLDER: name] | [PLACEHOLDER: ID] | | |
| [PLACEHOLDER: name] | [PLACEHOLDER: ID] | | |
| [PLACEHOLDER: name] | [PLACEHOLDER: ID] | | |
| [PLACEHOLDER: name] | [PLACEHOLDER: ID] | | |

---

## Summary table (required)

| # | Severity Scale (CVSS) | Vulnerability | Used Exploit | Recommended Remediation |
|---|---|---|---|---|
| 1 | 8.8 (High) | CVE-2026-93546 — Apache `mod_dav_fs` integer overflow (CWE-190) — **✅ verified** | Crafted `PROPPATCH` declaring ~45,000 distinct XML namespaces, delivered by `poc_dav_overflow.py`, overflowing the namespace counter and crashing the worker (DoS). | Upgrade to httpd 2.4.69; tighten `LimitXMLRequestBody` (100 KB) and bound worker memory (`RLimitMEM` / container `mem_limit`). |
| 2 | 8.1 (High) | CVE-2026-73636 — Apache `mod_auth_digest` capture-replay (CWE-294) — *in progress (§3.2)* | *Exploitation to be documented once reproduced — see §3.2.* | Upgrade to httpd 2.4.69; remove `AuthDigestNonceLifetime 0`; move to HTTP Basic/SSO over TLS so the header is never sniffable. |
| 3 | 7.5 (High) | CVE-2026-63686 — Apache `mod_xml2enc` NULL-pointer dereference (CWE-476) — *in progress (§3.2)* | *Exploitation to be documented once reproduced — see §3.2.* | Upgrade to httpd 2.4.69; drop `mod_xml2enc` / `proxy-html` where charset normalisation is not required; validate upstream `Content-Type`. |
| | **Target total: 24.4** (≥ 20 required) — **verified so far: 8.8** | Highest tier: **High → 100 % severity multiplier** | | |

All three are fixed in Apache httpd 2.4.69; the target runs 2.4.68. Full CVSS vector strings are in Appendix C.

---

## Executive summary

This report documents a vulnerability assessment and remediation exercise carried out by Team P1-6 against a **self-built, isolated Apache HTTP Server 2.4.68 environment** running under Docker on a team member's laptop. Three vulnerabilities from the approved ACW3 CVE list were selected, all affecting the same unpatched Apache build and together accumulating a CVSS base-score total of **24.4** (above the required 20), with a highest severity tier of **High**.

The three flaws form two attack narratives against one server: an **authenticated denial-of-service / memory-corruption** path in the WebDAV file backend (`mod_dav_fs`, CVE-2026-93546), a **credential capture-replay** path in HTTP Digest authentication (`mod_auth_digest`, CVE-2026-73636), and an **unauthenticated denial-of-service** path in the reverse-proxy charset filter (`mod_xml2enc`, CVE-2026-63686). All three are closed by the single upstream remediation of upgrading to Apache 2.4.69.

The team's principal methodological contribution is **reproducibility engineering**: each flaw is identified from its official CVE record and the 2.4.68→2.4.69 advisory, then reduced to a deterministic, one-command procedure with a control-then-attack structure so that any team member — or the assessing instructor — can re-run it and obtain the same result. For CVE-2026-93546 this process also **corrected a non-working exploit** (the original attempt used the wrong payload shape) and introduced a container memory cap (`mem_limit: 512m`) so the proof-of-concept crashes the worker safely in seconds instead of exhausting the host's RAM.

**Verification status at the time of writing (29 October 2026):** CVE-2026-93546 is fully reproduced with captured evidence. For CVE-2026-73636 and CVE-2026-63686 the vulnerable **preconditions are confirmed present**, but end-to-end exploitation against the current lab build was **not yet reproduced** by the team's automated checks; §3.2 and §3.3 state precisely what remains outstanding. These are flagged honestly so they can be closed before the live demonstration.

---

## 1. Introduction, scope and environment

### 1.1 Purpose
This coursework applies the vulnerability-management lifecycle — **identification, exploitation (pen-testing), and remediation** — to a controlled target. For each selected CVE the report establishes the root cause, demonstrates (or specifies) how the flaw is reached and triggered, and recommends a defence that mitigates or fully remediates it. "Done" for the module means three approved vulnerabilities demonstrated live and documented with evidence and defences.

### 1.2 Scope and ethics
All testing was conducted **exclusively against the team's own local Docker lab** (`vulnerable-env/`), on an isolated host-only network, never deployed to the internet or the SIT network, in line with the ACW3 brief's prohibition on using online or operational targets. No third-party or production systems were touched. The lab is torn down with `docker compose down` when not in use. CVE selection is restricted to the approved ACW3 list.

### 1.3 Environment
The target is a single **Apache HTTP Server 2.4.68** container (stock `httpd:2.4.68` image, unmodified binaries), configured through a mounted `httpd-vuln.conf` that enables exactly the modules and preconditions each CVE requires: WebDAV (`mod_dav` / `mod_dav_fs`) with a digest-authenticated writable `/dav/` collection, `mod_auth_digest` with `AuthDigestNonceLifetime 0`, and a `mod_proxy` + `mod_proxy_html` + `mod_xml2enc` reverse-proxy at `/proxy/` forwarding to a small purpose-built backend container. The attacker role uses Kali Linux (or a host shell) with `curl`, `python3`/`requests`, Wireshark and Burp Suite. Topology is shown in Appendix A (Fig. A-1).

**Target resource cap.** The target container is pinned to **`mem_limit: 512m` (+ `memswap_limit: 512m`)**. This is a deliberate environment constraint, not incidental: the CVE-2026-93546 proof-of-concept amplifies roughly 1 MB of request XML into multiple gigabytes of worker memory (over 10 GB observed uncapped). The cap stops that from exhausting the host, makes the worker crash within about five seconds, keeps the demonstration repeatable, and realistically models a production server with finite memory. It does not change whether any vulnerability is present.

## 2. Methodology

### 2.1 CVSS scoring
Each vulnerability's severity is taken from its **official CVE record** (CVSS v3.1 base scores), not re-derived: 8.8, 8.1 and 7.5, totalling 24.4. The full vector strings and the per-metric breakdown are reproduced in Appendix C. The team reproduced, rather than invented, the vendor-published scores and tier (all three **High**).

### 2.2 Vulnerability study method
For each flaw the team read the **official CVE record** (cve.org / the MITRE and NVD records) and cross-referenced the **Apache 2.4 security advisory** for the 2.4.68→2.4.69 fix, to establish the precise trigger condition and the affected code path before attempting any exploit. This "record-first" discipline proved decisive — see §3.1, where a plausible-looking but incorrect reading of the trigger produced no crash until the record's exact wording ("many XML namespaces") was taken literally.

### 2.3 Evidence method
Effects are captured as HTTP request/response pairs, `docker stats` resource readings, and Apache `error_log` / container-log excerpts (child-process signal lines), collected into the Appendix and referenced inline as "Fig. A-n".

### 2.4 Reproducibility engineering
So that any team member or the instructor can re-run a flaw deterministically, the team built:
- **Self-contained PoC scripts** under `vulnerable-env/guides/` (e.g. `poc_dav_overflow.py`) that first issue a **control** request to prove the baseline works, then the attack, printing the before/after so the effect is unambiguous — no payloads are hand-crafted live during the demo.
- **Parameterised** scripts (target URL, intensity) that act only on the lab's own writable paths, so runs are deterministic.
- **Dated verified transcripts** inside each guide, so a grader can diff their run against the team's.
- **Demo-safety hardening** via the container memory cap (§1.3), converting a potential host-wide outage into a fast, recoverable worker death.

### 2.5 Honesty of verification status
Where the team's automated checks reproduced a flaw end-to-end, concrete figures are given. Where only the **precondition** is confirmed and full exploitation is still outstanding, this is stated explicitly rather than implied, and the remaining step is named. No exploit result is fabricated.

## 3. Per-flaw analysis

### 3.1 CVE-2026-93546 — mod_dav_fs namespace overflow *(verified)*

**Overview.** Apache `mod_dav_fs` ≤ 2.4.68, CWE-190 integer overflow, **CVSS 8.8 (High)**. Official text: *"Integer overflow in mod_dav_fs … allows an authenticated WebDAV client with write access to crash worker processes and persistently corrupt a directory's property database via PROPPATCH requests declaring many XML namespaces."*

**Root cause.** `mod_dav_fs` is the file-system backend for Apache WebDAV. When it parses the XML body of a `PROPPATCH`, a counter tracking the number of declared XML namespaces overflows (CWE-190). The namespaces are also written into the resource's on-disk `.DAV` property database, so the damage persists across worker restarts.

**Precondition (wired in `httpd-vuln.conf`).** WebDAV is enabled on `/dav/`, which is digest-protected and writable by `labuser`. Confirmed by a `PUT`/`GET`/`DELETE` round-trip returning `201/200/204` (Fig. A-2).

**Exploitation — identification.** `OPTIONS /dav/` (authenticated) returns `DAV: 1,2` and the full `Allow:` method list including `PROPPATCH`; the `WWW-Authenticate: Digest realm="acw3-dav"` challenge confirms the auth scheme (Fig. A-3).

**Exploitation — the correct trigger.** The decisive finding is that the trigger is a large **number of distinct namespace *declarations*** (`<p xmlns="u0"/><p xmlns="u1"/>…` tens of thousands of times), **not** one namespace with an oversized URI. A single giant token merely returns `207` or trips `LimitXMLRequestBody` and returns `413` — it never crashes the server, which is why an earlier attempt appeared to fail. The working proof-of-concept (`poc_dav_overflow.py`) sends ~45,000 distinct namespaces (~0.8 MB, within the default 1 MB body limit).

**Observed behaviour / evidence (verified 29 Oct 2026).** Against the lab:
- Control (a well-formed `PROPPATCH`) → `207 Multi-Status`.
- Attack (45,000 namespaces) → the Apache worker **died within ~5.6 s**; the connection reset before any HTTP status returned.
- The service **auto-recovered** (subsequent `PROPFIND` → `207`).
- The error log recorded `AH00052: child pid N exit signal Segmentation fault (11)` (captured when RAM was unconstrained).
- The resource's `.DAV` property database **bloated to ~4.2 MB**, evidencing the "persistent corruption" clause.

A correct mental model matters for the demo: killing one worker is **not** a whole-container outage — Apache's parent respawns the child in about a second, so `docker ps` stays *Up* and the container `RestartCount` stays `0`. The evidence therefore lives at the **worker** level (connection reset, `docker stats` memory spike toward the 512 MiB cap, the log signal), and a short parallel flood makes the service briefly unreachable before recovering. See Appendix B for the full transcript.

**Defensive engineering & remediation.**
- *Upstream fix:* upgrade to **2.4.69+**, which removes the overflow (the only complete remediation).
- *Configuration hardening:* set `LimitXMLRequestBody 102400` (the 1 MB default is **not** low enough to stop the memory blow-up); bound worker memory with `RLimitMEM`, a container `mem_limit`, or systemd `MemoryMax`; set `Dav Off` on collections that do not need writes; keep `AuthType Digest` + `Require valid-user`.
- *Detection:* alert on `error_log` child-signal lines and sudden per-worker memory spikes.

### 3.2 Remaining vulnerabilities — exploitation in progress *(not yet written up)*

The other two selected CVEs have **confirmed vulnerable preconditions** but are **not yet reproduced end-to-end**, so their full analysis is deliberately deferred until the exploitation evidence exists. They are summarised here only so the plan and the ≥ 20-point target remain visible; full §3.x write-ups will be added once each is reproduced.

| CVE (CVSS) | Precondition status | What blocks reproduction today | Outstanding step |
|---|---|---|---|
| **CVE-2026-73636** — mod_auth_digest capture-replay, CWE-294 (8.1) | ✅ present — `AuthDigestNonceLifetime 0` set on `/dav/`, digest challenge live | A **naïve** header replay returns **`401`**; Apache's shared-memory nonce-count tracking rejects the duplicate. | Per the official record, replay works only "via crafted requests that trigger **garbage collection of the client's shared-memory entry**". Implement that GC-trigger, then replay the captured header → expect `200`. |
| **CVE-2026-63686** — mod_xml2enc NULL deref, CWE-476 (7.5) | ✅ present — `/proxy/` live through `proxy-html` + `mod_xml2enc`, backend reachable | The documented charset/truncate sweep returns **`200` across every case** — no `502`/segfault against the current backend. | The record requires the **backend to emit a response whose charset conversion partially succeeds then fails**. Adjust the backend to produce that shape, then capture the `502` + `Segmentation fault (11)` child-exit. |

**Severity-math note.** CVE-2026-93546 alone contributes 8.8, which is below the required 20. The two CVEs above (8.1 + 7.5) are needed to reach 24.4; until they are reproduced the report does not yet meet the threshold. Reserve option if one proves infeasible: CVE-2026-73637 (mod_auth_digest, 7.3, High).

## 4. Cross-cutting defensive engineering

The three flaws share one root remediation and several defence-in-depth themes:
- **Patch management & version pinning.** All three are closed by upgrading **2.4.68 → 2.4.69**. The single highest-value action is disciplined patching against the vendor advisory index, with pinned, reproducible builds.
- **Module minimisation / least privilege.** Each flaw is reachable only because its module is enabled. Disabling `mod_dav`, `mod_auth_digest`, or `mod_xml2enc`/`proxy-html` where unused removes the attack surface entirely.
- **Resource bounding.** Both DoS paths are blunted by capping request sizes (`LimitXMLRequestBody`) and process/container memory, converting host-wide outages into recoverable worker deaths — a lesson the lab itself encodes with `mem_limit: 512m`.
- **Transport security.** Running everything over **TLS** removes the sniffing precondition for the digest-replay chain.
- **Monitoring.** Apache child-process signal lines are a common tripwire across all three; alerting on them detects every one of these attacks in progress.

## 5. Conclusion

Team P1-6 assessed three High-severity vulnerabilities in an unpatched Apache 2.4.68 build, accumulating a CVSS total of **24.4 (≥ 20)** at a highest tier of **High**. CVE-2026-93546 is fully reproduced, including the correction of a non-working exploit and a safe, repeatable proof-of-concept; CVE-2026-73636 and CVE-2026-63686 have **confirmed preconditions** with specific, named exploitation steps remaining (§3.2, §3.3) to be closed before the live demonstration. A production team should prioritise the single remediation that closes all three — upgrading to 2.4.69 — followed by module minimisation, resource bounding, and TLS. Residual risk after patching is low, dominated by configuration drift (e.g. re-enabling Digest without TLS), which monitoring and config management address.

*(The GenAI-use declaration required by the brief is stated on the team page, combined with the Declaration of originality.)*

---

## References
1. CVE-2026-93546 — Apache HTTP Server mod_dav_fs. https://www.cve.org/CVERecord?id=CVE-2026-93546
2. CVE-2026-73636 — Apache HTTP Server mod_auth_digest. https://www.cve.org/CVERecord?id=CVE-2026-73636
3. CVE-2026-63686 — Apache HTTP Server mod_xml2enc. https://www.cve.org/CVERecord?id=CVE-2026-63686
4. Apache HTTP Server 2.4 vulnerabilities / security advisory index. https://httpd.apache.org/security/vulnerabilities_24.html
5. NVD records for the three CVEs (CVSS v3.1 vectors). https://nvd.nist.gov/
[PLACEHOLDER: add the Apache 2.4.69 changelog entry and any CWE references used.]

## Appendices (excluded from the 10-page count)

- **Appendix A — Figures.** Fig. A-1 lab topology; A-2 DAV write round-trip; A-3 `OPTIONS`/digest challenge; A-4 digest precondition grep; A-5 digest replay evidence *(pending, §3.2)*; A-6 `/proxy/` filter chain; A-7 xml2enc crash evidence *(pending, §3.3)*.
- **Appendix B — CVE-2026-93546 verified transcript (29 Oct 2026):** control `PROPPATCH` → `207`; attack (45,000 namespaces, ~0.8 MB) → worker died (connection reset) in ~5.6 s; recovery → `207`; `AH00052 … exit signal Segmentation fault (11)`; `.DAV` propdb ~4.2 MB.
- **Appendix C — CVSS vector strings** for all three CVEs (from the official records) with per-metric breakdown. [PLACEHOLDER: paste vectors.]
- **Appendix D — Reproducibility artifacts:** `vulnerable-env/guides/*.md`, `poc_dav_overflow.py`, and the `docker-compose.yml` `mem_limit: 512m` diff.
