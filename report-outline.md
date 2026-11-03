# INF2005 ACW3 — Report Outline Skeleton (Team P1-6)

**Target file:** `Report_P1-6.pdf` · **Format:** PDF, 11-pt Calibri · **Limit:** 10 pages (cover, references, appendix excluded)

> **Scoring math this outline is built to satisfy**
> - Documented items must total **≥ 20 CVSS points**. Current selection: 8.8 + 8.1 + 7.5 = **24.4** (headroom 4.4).
> - Highest tier = **High** → 100% severity multiplier.
> - **Reserve:** CVE-2026-73637 (7.3, High). If one primary CVE is dropped, swap it in to stay above 20 (e.g. 8.8 + 8.1 + 7.3 = 24.2; 8.1 + 7.5 + 7.3 = 22.9). Verify every score against the official record before locking it in.

---

## Page budget (10 pages max, body only)

| Page(s) | Section | Approx. words |
|---|---|---|
| 1 | Cover-style team page (names + student IDs) | — |
| 2 | Summary table (flaw / severity / mitigation) | table only |
| 3 | §1 Introduction, scope & environment | ~500 |
| 3–4 | §2 Methodology (CVSS, lab, evidence approach) | ~500 |
| 4–6 | §3.1 CVE-2026-93546 (mod_dav_fs) | ~700 |
| 6–7 | §3.2 CVE-2026-73636 (mod_auth_digest) | ~700 |
| 7–9 | §3.3 CVE-2026-63686 (mod_xml2enc) | ~700 |
| 9 | §4 Cross-cutting defensive engineering | ~400 |
| 10 | §5 Conclusion + §6 GenAI-use declaration | ~300 |

Keep diagrams, screenshots, config listings and PoC steps in the **Appendix** (not counted), and reference them inline as "Fig. A-1", etc.

---

## Page 1 — Team page
- Module, coursework number, lab group / team (P1-6), submission date.
- Table: **Full name · Student ID · Role** (one row per member).
- **Declaration of originality, signed by all team members** (required by the spec).

## Page 2 — Summary table (required)
Columns exactly as the spec's template. "Severity Scale" is the CVSS base score (the spec's example uses the number, e.g. 6, 5).

| # | Severity Scale | Vulnerability | Used Exploit | Recommended Remediation |
|---|---|---|---|---|
| 1 | 8.8 (High) | CVE-2026-93546 — mod_dav_fs | Crafted `PROPPATCH` declaring ~45,000 distinct XML namespaces (CWE-190 count overflow) via `poc_dav_overflow.py` → Apache worker crash / DoS | Upgrade to httpd 2.4.69; cap `LimitXMLRequestBody` (100 KB) + bound worker memory (`RLimitMEM` / container `mem_limit`) |
| 2 | 8.1 (High) | CVE-2026-73636 — mod_auth_digest | *(technique/tool used)* | *(defence)* |
| 3 | 7.5 (High) | CVE-2026-63686 — mod_xml2enc | *(technique/tool used)* | *(defence)* |
|   | **Total 24.4** (≥ 20) | | | |

Footnote: all three fixed in Apache httpd 2.4.69; target runs 2.4.68. (The full CVSS vector strings go in the appendix / §2, not this table.)

## §1 — Introduction, scope & environment (p.3)
- Objective and what "done" means for the module.
- **Scope / ethics statement:** isolated local lab only, no online or operational testing, no public deployment.
- Environment summary: single Apache 2.4.68 target (Docker), Kali attacker, host-only / internal network, snapshots taken. Reference the lab topology diagram (Fig. A-1).
- **Target resource cap:** the Docker target is pinned to **`mem_limit: 512m` (+ `memswap_limit: 512m`)**. State this up front as a deliberate environment constraint: it stops the mod_dav_fs PoC's memory blow-up (observed >10 GB uncapped) from exhausting the host, makes the worker crash fast (~5 s) and repeatable, and models a realistic production server with finite RAM.

## §2 — Methodology (p.3–4)
- **CVSS scoring:** state version (v3.1 / v4.0 — match the record), show how each vector string maps to the base score; note you reproduced, not invented, the vendor score.
- **Vulnerability study method:** vendor advisory + 2.4.68→2.4.69 changelog/diff to establish the trigger condition for each module.
- **Evidence method:** how each flaw's effect is captured (screenshot, request/response, log) for the appendix.
- **Reproducibility engineering (what the team did so any member / the instructor can re-run a flaw in one command):**
  - Each flaw ships a **self-contained PoC script** in `vulnerable-env/guides/` (e.g. `poc_dav_overflow.py`) that runs a *control* request first (to prove the baseline works) and then the attack, printing the before/after so the effect is unambiguous — no hand-crafting payloads live during the demo.
  - PoCs are **parameterised** (target URL, intensity) and target only the local lab's writable paths, so they are deterministic and re-runnable.
  - Each guide in `vulnerable-env/guides/` records a **verified transcript** (dated) of the exact output seen against the lab, so a grader can diff their run against ours.
  - **Demo-safety hardening:** the mod_dav_fs PoC amplifies ~1 MB of XML into multiple GB of worker memory; left uncapped this can exhaust the host (observed >10 GB). The target container is therefore pinned with `mem_limit: 512m` (+ `memswap_limit`) in `docker-compose.yml` so the worker dies within ~5 s, the DoS is clearly visible, and the host stays safe — this also realistically models a production server with finite RAM.
  - **Correct trigger documented:** for CVE-2026-93546 the record's phrase "many XML namespaces" means a large *number of distinct namespace declarations*, **not** one oversized namespace token — getting this wrong produces only `413`/`207` and no crash (a dead end we hit and corrected). Noting the trap in the report demonstrates genuine root-cause understanding.

## §3 — Per-flaw analysis (p.4–9)
Repeat this sub-structure for each of the three CVEs:
1. **Overview** — component, affected versions, severity, CVSS vector + base score.
2. **Technical description of the root cause** — what the code/config actually does wrong (cite the advisory and the fix diff).
3. **Preconditions** — config required for the flaw to be reachable (maps to your `httpd-vuln.conf`).
4. **Observed behaviour / evidence** — what the demo shows; point to appendix figures. *(Description and results, not a weaponised, copy-paste exploit in the body.)*
5. **Defensive engineering & remediation** — the core-content requirement:
   - The upstream fix (what 2.4.69 changed and why it closes the root cause).
   - Configuration hardening that reduces exposure before patching.
   - Detection / monitoring signal (what a defender would see in logs).

## §4 — Cross-cutting defensive engineering (p.9)
- Patch management & version pinning (2.4.68 → 2.4.69).
- Least-privilege / module minimisation (disable mod_dav, digest auth, proxy if unused).
- Defence-in-depth: WAF rules, reverse-proxy input validation, auth hardening.

## §5 — Conclusion (p.10)
- Recap severity total (24.4 ≥ 20), highest tier High.
- Residual risk and what a production team should prioritise.

## §6 — GenAI-use declaration (p.10)
- State which tools were used and for what (e.g. drafting, outline, explanation), per module policy.

## Appendix (not counted toward 10 pages)
- Fig. A-1 Lab topology diagram.
- Per CVE: config snippet, request/response evidence, log excerpts, remediation diff/screenshot.
- Full CVSS vector strings and the calculator breakdown for each.
- **Reproducibility artifacts (so each flaw is one-command repeatable):**
  - Per-CVE PoC scripts under `vulnerable-env/guides/` (e.g. `poc_dav_overflow.py`) and the matching step-by-step guide `vulnerable-env/guides/CVE-2026-93546-mod_dav_fs.md`.
  - **CVE-2026-93546 verified transcript (2026-10-29):** control PROPPATCH → `207`; attack (45,000 namespaces, ~0.8 MB) → worker died (connection reset) in ~5 s; service auto-recovered → `207`; captured `AH00052 … child pid N exit signal Segmentation fault (11)`; `.DAV` property DB bloated to ~4.2 MB (persistent corruption).
  - **"Why it looks like nothing crashed" note (Fig.):** Apache's parent respawns the killed child in ~1 s, so `docker ps` stays *Up* and container `RestartCount` stays `0`; evidence is at the *worker* level (connection reset, `docker stats` memory spike to the 512 MiB cap, log signal), and a short parallel flood makes the whole service briefly unreachable then recover.
  - Lab-safety change: `mem_limit: 512m` / `memswap_limit: 512m` on the target in `docker-compose.yml` (keep as an appendix config diff).

## References (not counted)
- Each official CVE record URL, the Apache security advisory, and the 2.4.69 changelog.
