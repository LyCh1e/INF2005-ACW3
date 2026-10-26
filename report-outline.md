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
| 1 | 8.8 (High) | CVE-2026-93546 — mod_dav_fs | *(technique/tool used)* | *(defence)* |
| 2 | 8.1 (High) | CVE-2026-73636 — mod_auth_digest | *(technique/tool used)* | *(defence)* |
| 3 | 7.5 (High) | CVE-2026-63686 — mod_xml2enc | *(technique/tool used)* | *(defence)* |
|   | **Total 24.4** (≥ 20) | | | |

Footnote: all three fixed in Apache httpd 2.4.69; target runs 2.4.68. (The full CVSS vector strings go in the appendix / §2, not this table.)

## §1 — Introduction, scope & environment (p.3)
- Objective and what "done" means for the module.
- **Scope / ethics statement:** isolated local lab only, no online or operational testing, no public deployment.
- Environment summary: single Apache 2.4.68 target (Docker), Kali attacker, host-only / internal network, snapshots taken. Reference the lab topology diagram (Fig. A-1).

## §2 — Methodology (p.3–4)
- **CVSS scoring:** state version (v3.1 / v4.0 — match the record), show how each vector string maps to the base score; note you reproduced, not invented, the vendor score.
- **Vulnerability study method:** vendor advisory + 2.4.68→2.4.69 changelog/diff to establish the trigger condition for each module.
- **Evidence method:** how each flaw's effect is captured (screenshot, request/response, log) for the appendix.

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

## References (not counted)
- Each official CVE record URL, the Apache security advisory, and the 2.4.69 changelog.
