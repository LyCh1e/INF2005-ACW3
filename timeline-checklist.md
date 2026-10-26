# INF2005 ACW3 — Project Timeline Checklist (Team P1-6)

**Today:** Mon 26 Oct 2026 · **Report due:** Mon 9 Nov 23:59 (Xsite Dropbox, 5% late penalty) · **Demo (fixed):** Thu 12 Nov 2026, 4:00–6:00pm, venue E2-05-05 (Group P1) · **Peer review (optional):** Fri 14 Nov

Work backwards from the demo, not the report — the demo is worth 20% and is **single-attempt with no setup/debug time**.

> **Marks:** Pen-test demo 20 + Report 10 = 30% of the module. Highest severity across the documented CVEs sets the multiplier: Critical/High = 100%, Medium = 95%, Low/None = 90%. All three chosen CVEs are **High**, so 100%.

---

## Current progress snapshot (as of 26 Oct 2026)

**Done:**
- [x] Target server fully configured — `httpd:2.4.68`, all three CVE preconditions wired in `conf/httpd-vuln.conf` (WebDAV + digest on `/dav/`, `AuthDigestNonceLifetime 0`, `/proxy/` → backend with proxy-html/xml2enc).
- [x] Proxy backend `backend/server.py` built as a response-shaping test harness (`charset` / `encode_as` / `truncate` / `chunked`).
- [x] Demo site built and fully styled (Home, News Mirror, About, Sign in, CVE map, WebDAV listing) with decoy "sensitive" docs as loot.
- [x] **Per-CVE pen-test guides** written (`vulnerable-env/guides/`): setup, identification, exploitation methodology, evidence-to-capture, remediation.
- [x] Report **outline** + this timeline drafted.

**Still open:** run the exploits and capture evidence, verify CVSS vectors, write the report, Kali box + snapshots, timed demo rehearsal.

---

## Phase 0 — Setup (this week)
- [ ] Confirm CVSS version (v3.1 / v4.0) and exact base scores against each **official CVE record**; recompute the ≥20 total (currently 24.4).
- [ ] Assign members: one CVE each is fine for the demo (guides are written per CVE); **every member must be able to explain ≥1 CVE end to end** (instructors can ask anyone).
- [ ] Agree where the report/evidence live (this repo) and the file-naming convention.
- [ ] *(No CVE-approval email needed — all three CVEs are from the provided INF2005-ACW3-CVE-List. An email is only required if a team proposes its own CVE that is not on the list.)*

## Phase 1 — Attacker box + snapshots (by ~Wed 29 Oct)
- [x] Target + backend stand up cleanly (`docker compose up -d --build`).
- [x] CVE config preconditions wired and verified.
- [ ] Stand up the Kali (or equivalent) attacker on an isolated / host-only network.
- [ ] **Take clean VM/container snapshots** of a known-good state to rehearse and demo from.

## Phase 2 — Run & reproduce each exploit (by ~Wed 5 Nov)
Follow each guide in `vulnerable-env/guides/` end to end:
- [ ] Reproduce each exploit and **confirm it triggers reliably from a fresh snapshot** (the one-attempt rule is strict).
- [ ] **Screenshot every step** for the report appendix.
- [ ] Record the CVSS vector breakdown per CVE.
- [ ] Note: the mod_auth_digest replay needs the exact `nc`/nonce handling worked out — verify a replayed request actually returns 200 before relying on it live.
- [ ] Keep the reserve CVE (73637) reproducible as a fallback in case one fails.
- [ ] Re-snapshot once everything reproduces cleanly.

## Phase 3 — Report (draft by Fri 6 Nov, final by Sun 8 Nov)
- [ ] Fill `report-outline.md` into prose; body ≤10 pages (cover/refs/appendix excluded), 11-pt Calibri.
- [ ] Page 1: team members' **full names + student IDs**.
- [ ] Page 2: summary table — columns per spec: **# | Severity Scale | Vulnerability | Used Exploit | Recommended Remediation**.
- [ ] Per CVE: exploit technique/tool used, screenshots in the appendix, suitable defence mechanism(s).
- [ ] **Declaration of originality signed by all team members.**
- [ ] **GenAI-use declaration** — state which parts were (partially) AI-generated (SIT policy; AI use is allowed).
- [ ] Export as `Report_P1-6.pdf`; proofread + page-count check.
- [ ] **One representative submits to Xsite Dropbox by Mon 9 Nov 23:59** — aim for the 8th to absorb any issues.

## Phase 4 — Demo prep (by Wed 11 Nov)
- [ ] 30-min run sheet: ~20 min demo + 10 min Q&A. Remediation is **optional** to demo — focus stage time on identification + exploitation.
- [ ] Assign speaking parts so **every member presents or answers**.
- [ ] **Full timed rehearsal from a fresh snapshot** (no live debugging on the day).
- [ ] Fallback: pre-recorded clip / screenshots in case a live step fails.

## Phase 5 — Demo & close-out
- [ ] **Demo: Thu 12 Nov, 4:00–6:00pm, E2-05-05.** All members present — absent without valid reason = 0 for the demo component.
- [ ] *(Optional)* **Peer review** by Fri 14 Nov — only if there's a contribution imbalance. Email the 4 instructors, **CC all members**. No submission = everyone assumed equal.

---

## Critical-path risks
- **Single demo attempt, no setup time** (slot is strictly demo + Q&A). Rehearse from a snapshot; have a recorded fallback.
- **Exploits must actually reproduce.** The CVEs are instructor-provided; the guides give methodology, not canned PoCs. Verify each triggers before demo day — especially the digest nonce-replay (the exact replay mechanics need nailing down).
- **4.4-point margin** above the 20 minimum: if one CVE fails, swap in the reserve (73637) rather than dropping below 20.
