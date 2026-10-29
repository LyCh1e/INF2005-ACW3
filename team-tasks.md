# INF2005 ACW3 — Team Tasks & Delegation (Team P1-6)

**Status:** lab environment + pen-test guides + report outline are done. We are now in the **run exploits → capture evidence → write report → rehearse** phase.

**Key dates:** Report due **Mon 9 Nov 23:59** (Xsite Dropbox, 5% late penalty) · Demo **Thu 12 Nov, 4:00–6:00pm, E2-05-05** (one attempt, no setup time) · Peer review (optional) Fri 14 Nov.

**Scoring:** Demo 20% + Report 10%. All three CVEs are **High**, so the severity multiplier is 100%. Total CVSS 24.4 (minimum 20).

---

## Who does what

### CVE owners (one each, end-to-end)
Each owner: reproduces the exploit, captures evidence, verifies the CVSS score, writes that CVE's report section, and demos it live.

| Owner | CVE | Component | Severity | Guide |
|---|---|---|---|---|
| **Han** | CVE-2026-93546 | mod_dav_fs | High 8.8 | `vulnerable-env/guides/CVE-2026-93546-mod_dav_fs.md` |
| **Raynard** | CVE-2026-73636 | mod_auth_digest | High 8.1 | `vulnerable-env/guides/CVE-2026-73636-mod_auth_digest.md` |
| **Jolene** | CVE-2026-63686 | mod_xml2enc | High 7.5 | `vulnerable-env/guides/CVE-2026-63686-mod_xml2enc.md` |

### Cross-cutting roles
| Member | Role | Owns |
|---|---|---|
| **Cyube** | Lab & reproducibility lead | Build Kali attacker box, take the **clean snapshots** everyone works from, help the CVE owners get their exploits reproducing, deep technical Q&A backup on the day. |
| **Nicholas** | Report owner | Assemble the 3 CVE sections + intro/methodology/conclusion, formatting (11-pt Calibri, ≤10 pages), Page-1 names/IDs + originality declaration (collect signatures), GenAI declaration, references, lab topology diagram, export & **submit** `Report_P1-6.pdf`. |
| **LyChii / Jerry** | Demo coordinator | Build the 30-min run sheet, run the **timed rehearsal** from a fresh snapshot, record the fallback video, keep time on the day, QA everyone's evidence. |

*(Everyone must be present at the demo and able to explain ≥1 CVE — instructors can ask anyone.)*

---

## What "owning a CVE" means (Han / Raynard / Jolene)

1. **Reproduce the exploit reliably** from the clean snapshot, following your guide.
2. **Screenshot every step** (+ relevant logs) — these go straight into the report appendix.
3. **Verify the CVSS score/vector** against the official CVE record (note v3.1 vs v4.0).
4. **Write your CVE's report section** — exploit technique/tool used + recommended remediation — and send it to Nicholas.
5. Be ready to **demo it live** and answer Q&A.

**Notes per CVE:**
- **Raynard (73636):** ⚠️ a naive replay returned 401 in testing — work out the exact nonce/`nc` handling so a replayed request returns 200. Nail this early.
- **Jolene (63686):** capture the segfault + the Apache error-log lines as evidence of the `/proxy/` crash (DoS).
- **Han (93546):** the crafted `PROPPATCH` crashes httpd; capture before/after and the crash.

---

## How to run the lab
- Windows: `run.ps1` · Mac/Linux: `./run.sh` → open http://localhost:8080/
- Shared-drive login: `labuser` / `labpass123`
- **Don't start exploiting until Cyube shares the clean snapshot** — everyone works/rehearses from the same known-good state.
- Tear down: `./run.sh down` (or `docker compose down` in `vulnerable-env/`).

---

## Sequence (dependencies)
1. **Cyube:** Kali box + clean snapshot — *do this first; everyone depends on it.*
2. **Han / Raynard / Jolene:** exploit working + evidence captured + report section drafted → **by Wed 5 Nov.**
3. **Nicholas:** assemble report once the 3 sections + evidence land → draft **6 Nov**, final **8 Nov**, submit by **9 Nov.**
4. **Demo coordinator:** timed rehearsal ~**11 Nov** → demo **12 Nov, 4–6pm.**

---

## Report checklist (owner: Nicholas)
- [ ] Page 1: full names + student IDs + **originality declaration signed by all**
- [ ] Page 2: summary table — `# | Severity Scale | Vulnerability | Used Exploit | Recommended Remediation`
- [ ] 3 CVE sections (from owners) + intro / methodology / conclusion
- [ ] Appendix: screenshots/evidence + lab topology diagram + full CVSS vectors
- [ ] References (official CVE records + Apache 2.4.69 advisory)
- [ ] **GenAI-use declaration** (state which parts were AI-assisted — allowed under SIT policy)
- [ ] 11-pt Calibri, ≤10 pages (excl. cover/refs/appendix), PDF named `Report_P1-6.pdf`
- [ ] Submit to Xsite Dropbox by **Mon 9 Nov 23:59**

---

## Risks to watch
- **Single demo attempt, no setup time** — rehearse from a snapshot; keep the fallback recording.
- **Exploits must actually reproduce** — the guides are methodology, not canned PoCs. Verify early, especially the digest replay.
- **4.4-point margin** above 20 — if one CVE fails, swap in reserve **CVE-2026-73637** (mod_auth_digest, 7.3) rather than dropping below 20.
