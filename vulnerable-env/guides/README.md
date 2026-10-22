# ACW3 pentest guides — Group P1-6

One guide per CVE wired up in `vulnerable-env/`. Each guide is written
as a standalone demo + report walkthrough: setup, identification,
exploitation, evidence to capture, and recommended remediation.

| # | CVE | Component | Severity | Guide |
|---|---|---|---|---|
| 1 | CVE-2026-93546 | `mod_dav_fs`        | High 8.8 | [CVE-2026-93546-mod_dav_fs.md](CVE-2026-93546-mod_dav_fs.md) |
| 2 | CVE-2026-73636 | `mod_auth_digest`   | High 8.1 | [CVE-2026-73636-mod_auth_digest.md](CVE-2026-73636-mod_auth_digest.md) |
| 3 | CVE-2026-63686 | `mod_xml2enc`       | High 7.5 | [CVE-2026-63686-mod_xml2enc.md](CVE-2026-63686-mod_xml2enc.md) |

**Total CVSS: 24.4** (report minimum is 20).

## How to use the guides on demo day

Each team member can take one CVE and run through its guide front-to-
back as their 5–7 minute slot in the 30-minute demo window. The guides
are deliberately paired with evidence screenshots at each step so your
report appendix writes itself.

For every guide:

1. Stand the lab up first — `docker compose up -d --build` from
   `vulnerable-env/`.
2. Open the Fieldstone portal (`http://localhost:8080/`) to confirm the
   target is live.
3. Follow the guide's steps in order; screenshot each numbered step for
   the appendix.
4. Tear down with `docker compose down` when you're done.

## Notes

* All exact exploit lengths, nonce values, and byte offsets come from
  the **official CVE records** linked at the top of each guide; the
  guides give you the methodology and the scaffolding, not a
  pre-canned PoC (per the assignment spec: "identification and
  exploitation steps are worked out by the team from each official
  CVE record").
* The three CVEs chain in the obvious way — CVE-2026-73636 gets you
  `labuser`'s session without a password; CVE-2026-93546 then lets
  that session crash httpd via a crafted `PROPPATCH`; CVE-2026-63686
  is an independent, unauth DoS of `/proxy/`. The report can mention
  the chain in the executive summary.
