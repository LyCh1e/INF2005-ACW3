# INF2005 ACW3 — Project Timeline Checklist (Team P1-6)

**Today:** Sun 22 Oct 2026 · **Report due:** Mon 9 Nov 23:59 (Xsite Dropbox, 5% late penalty) · **Demo:** Tue 10 Nov or Thu 12 Nov (30 min slot, incl. 10 min Q&A, one attempt) · **Peer review:** Fri 14 Nov (email instructors, CC all members)

That leaves ~2.5 weeks. Work backwards from the demo, not the report — the demo is 20% and single-attempt.

---

## Current progress snapshot (as of 22 Oct 2026, commit d825f22)

**Done:**
- [x] Target server fully configured — `httpd:2.4.68` in `docker-compose.yml`, all three CVE preconditions wired in `conf/httpd-vuln.conf` (WebDAV + digest on `/dav/`, `AuthDigestNonceLifetime 0`, `/proxy/` → backend with proxy-html/xml2enc).
- [x] Decoy "Fieldstone Docs" portal built under `public/` (index/about/login/cve-map + styling) so the target looks like a real internal site.
- [x] WebDAV share `www/` populated with fake sensitive docs (Q3 financials, vendor contract, client brief, onboarding metrics) as demo loot.
- [x] Proxy backend `backend/server.py` built as a test harness (query params `charset` / `encode_as` / `truncate` / `chunked`) to shape proxied responses.
- [x] Smoke test logged in README (GET / → 200, `/dav/` unauth → 401, WebDAV PUT/GET/DELETE cycle works).

**Still open:** CVE approval email, the actual trigger/exploitation research for all three CVEs, Kali attacker + snapshots, the report, and the timed demo rehearsal.

---

## Phase 0 — Approval & setup (by Fri 24 Oct)
- [ ] **Email instructors to approve the 3 CVEs** (93546, 73636, 63686) + reserve 73637. *Blocking — do first.*
- [ ] Confirm CVSS version and exact base scores against each official record; recompute the ≥20 total.
- [ ] Assign 2 members per CVE (one studies the trigger, one studies the remediation); every member owns ≥1 CVE end to end.
- [ ] Agree where report/evidence live (this repo) and the file-naming convention.

## Phase 1 — Build the lab (by Wed 29 Oct)
- [x] Stand up the Apache 2.4.68 target from `vulnerable-env/` and confirm it starts clean. *(done, commit d825f22)*
- [x] Backend service for `/proxy/` built as a test harness (`backend/server.py`). *(done — note: this is the harness, not a working CVE-2026-63686 trigger; see Phase 2)*
- [x] Verify each CVE's config precondition is actually wired (WebDAV writable, `AuthDigestNonceLifetime 0`, proxy route live). *(wired in `httpd-vuln.conf`; confirm live on next `docker compose up`)*
- [ ] Stand up the Kali attacker on an isolated / host-only network.
- [ ] **Take clean VM/container snapshots** of a known-good state.

## Phase 2 — Study & reproduce each flaw (by Wed 5 Nov)
For each CVE (work from vendor advisory + 2.4.68→2.4.69 diff):
- [ ] Establish the trigger condition and capture the observed behaviour as evidence (screenshots, request/response, logs).
- [ ] Record the CVSS vector breakdown for the appendix.
- [ ] Write the remediation: upstream fix + config hardening + detection signal.
- [ ] Confirm the reserve CVE (73637) is reproducible as a fallback.
- [ ] Re-snapshot once each flaw is reliably reproducible.

## Phase 3 — Report (draft by Fri 6 Nov, final by Sun 8 Nov)
- [ ] Fill the outline (`report-outline.md`) into prose; keep body ≤10 pages, evidence in appendix.
- [ ] Complete the Page 2 summary table with real vector strings and scores.
- [ ] Write the GenAI-use declaration.
- [ ] Format: PDF, 11-pt Calibri; export as `Report_P1-6.pdf`.
- [ ] Proofread + page-count check (cover/refs/appendix excluded).
- [ ] **Submit by Mon 9 Nov 23:59** — aim for the 8th to absorb any Dropbox issues.

## Phase 4 — Demo prep (by Mon 9 Nov)
- [ ] Build the 30-min run sheet: ~20 min content, leave 10 min for Q&A.
- [ ] Assign speaking parts so every member presents or answers.
- [ ] **Full timed rehearsal from a fresh snapshot** (single-attempt = no live debugging).
- [ ] Prep a fallback: pre-recorded clip / screenshots in case a live step fails.
- [ ] Confirm which day your slot is (10th or 12th) and the room/link.

## Phase 5 — Demo & close-out
- [ ] **Demo day (10 or 12 Nov):** all members present; absent-without-reason = 0.
- [ ] **Peer review by Fri 14 Nov:** email instructors, CC every member.

---

## Critical-path risks
- **CVE approval is blocking** — nothing else is safe to finalise until the 3 are approved.
- **4.4-point margin** above the 20 minimum: if one CVE is rejected/fails, swap in the reserve immediately, don't drop below 20.
- **Single demo attempt, no setup time:** rehearse from snapshot, have a recorded fallback.
- **mod_xml2enc backend is unbuilt** — highest-uncertainty task; start it in Phase 1.
