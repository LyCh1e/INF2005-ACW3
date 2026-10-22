# ACW3 CVE Suggestions (Group P1-6)

## Key Requirements (from spec)

- **Demo:** exploit **3** vulnerabilities, approved by the instructors.
- **Demo marks:** highest severity Critical/High = 100%, Medium = 95%, Low/None = 90%.
- **Report:** total CVSS across vulnerabilities must be **>= 20 points**.
- **Demo format:** 30 minutes including 10 minutes Q&A. Single attempt, no setup time. **All members must be present** and each gets a chance to demo or answer questions. Absent without valid reason = 0.
- Team size is 6, so 4 vulnerabilities is more than enough; the demo only needs 3.

## Final Selection (3 CVEs, all in one Apache environment)

| # | CVE | Component | CVSS | Severity |
|---|---|---|---|---|
| 1 | CVE-2026-93546 | Apache mod_dav_fs | 8.8 | High |
| 2 | CVE-2026-73636 | Apache mod_auth_digest | 8.1 | High |
| 3 | CVE-2026-63686 | Apache mod_xml2enc | 7.5 | High |

**Total: 24.4** (minimum required: 20). Highest severity is High, so the demo earns 100% of its marks.

## Why Include Each Vulnerability

### 1. CVE-2026-93546 - Apache mod_dav_fs (8.8, High)
- **Why:** highest score on the list that is practical to demo; it single-handedly contributes the largest share of the 20-point minimum.
- **Ease of showcase:** a vulnerable Apache version runs in one Docker container or VM. No special hardware, domain controller or specific kernel is needed.

### 2. CVE-2026-73636 - Apache mod_auth_digest (8.1, High)
- **Why:** second-highest practical score, and an authentication-related flaw is easy for the audience and instructors to understand.
- **Ease of showcase:** same Apache environment as #1. The effect (access or auth behaviour) is visible on screen in a browser or curl, which suits a one-attempt demo.

### 3. CVE-2026-63686 - Apache mod_xml2enc (7.5, High)
- **Why:** keeps all three at High, and covers a different module and attack type from #1 and #2, so the demo shows variety rather than two auth-digest issues.
- **Ease of showcase:** same Apache environment, so no extra setup.

## Why These Over the Alternatives

- **Single shared environment:** all three run on one Apache target. Less setup, fewer things to fail during a single-attempt demo, and one snapshot or container image to rehearse with.
- **Avoided as too hard to demo reliably:**
  - Windows Hello / Kerberos: special hardware or an AD lab.
  - Linux kernel CVEs: exact kernel version needed, and a risk of crashing the VM mid-demo.
  - VirtualBox CVEs: nested virtualisation.
  - Android CVEs: emulator setup.
  - Docker CVEs: all Medium and configuration-heavy.
- **Python CVEs (tarfile 5.7, tempfile 5.9):** easy to run but Medium, and they would not use the shared Apache environment.

## Reserve

- **CVE-2026-73637 - Apache mod_auth_digest (7.3, High):** same environment and setup. Use it if CVE-2026-63686 has no workable PoC or fails on the day.
- **Margin:** the total is only 4.4 points above the 20-point minimum. If one CVE is rejected or fails, the total drops to 15.9-16.9, below the minimum. Keep the reserve prepared.

## Splitting 6 Members Across 3 Vulnerabilities

- Two people per vulnerability: one runs the exploit, one explains the remediation.
- Every member must be able to explain at least one vulnerability end to end, since the instructors can ask anyone.

## Next Steps

1. Email the instructors to get the 3 CVEs approved before starting.
2. Check each CVE record for affected Apache versions and public PoCs, and confirm one container or VM can host all three.
3. Build the target and attacker (Kali) environments and take snapshots.
4. Rehearse the full demo once, time-boxed to the 20 minutes available before Q&A.
5. Draft the report table (severity, vulnerability, exploit used, remediation) and note any GenAI use.

## Caveat

The ease-of-demo ratings come from the component type, not from reading each CVE record. Verify versions and PoC availability before committing.
