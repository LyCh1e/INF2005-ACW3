# How and Why We Built the Lab Environment

## Assignment Constraints

The ACW3 spec requires us to demonstrate three vulnerabilities in a live, 30-minute demo
with no setup time and only one attempt. That shaped every decision we made about the
environment:

- It has to come up instantly — no manual installs, no "let me just configure this" on
  demo day.
- It has to be completely isolated — we are running real exploits, so nothing can leak out
  to the university network or the internet.
- It has to be reproducible — if something breaks during rehearsal, we need to tear it
  down and rebuild from scratch in under a minute.

Docker Compose was the answer we landed on. One `docker-compose.yml`, one command
(`docker compose up -d --build`), and the entire lab is running. Tear it down with
`docker compose down`, rebuild, and you are back to a clean state.

### Why Docker Over a Virtual Machine

A traditional pentest lab would use VMs — a vulnerable target VM and a Kali attacker VM,
often managed through something like VirtualBox or VMware. We considered that route and
chose Docker instead for several reasons:

1. **Startup speed.** A VM takes minutes to boot. A Docker container starts in seconds.
   In a demo with no setup time and one attempt, the difference between "it's already
   running" and "please wait while the VM loads" matters.

2. **Portability across the team.** Six team members need to rehearse on their own
   machines. Shipping a VM image means distributing a multi-gigabyte `.ova` file and
   hoping everyone's hypervisor handles it the same way. A Compose file and a few config
   files fit in a Git repo — everyone clones, runs one command, and gets an identical
   environment regardless of whether they are on Windows, macOS, or Linux.

3. **Reproducibility.** With a VM, state drifts: someone installs a package, changes a
   config, forgets to snapshot. With Docker, the container image is built from a
   Dockerfile and a pinned base image (`httpd:2.4.68`). Every `docker compose up --build`
   produces the exact same environment. There is no "it worked on my machine" problem.

4. **Lightweight resource usage.** Our laptops do not need to dedicate 2–4 GB of RAM and
   a virtual disk to a full guest OS. The Apache container runs the server process
   directly on the host kernel with minimal overhead, leaving resources free for the
   tools we run against it (Wireshark, curl, Python scripts).

5. **No hypervisor dependency.** Some team members' machines had issues with
   hardware virtualisation or conflicting hypervisors. Docker Desktop runs on all of
   them without needing to enable VT-x, configure nested virtualisation, or debug
   Hyper-V conflicts.

The one trade-off is that Docker containers share the host kernel, so a kernel-level
exploit could theoretically escape the container. That is not a concern here — all three
of our CVEs are application-level bugs in Apache userspace code, not kernel exploits. The
container boundary is more than sufficient isolation for what we are demonstrating.

---

## Why We Chose a Single Apache Target for All Three CVEs

Early on, the team considered running separate targets for each vulnerability — a
different VM or container per CVE. We dropped that idea for two reasons:

1. **Demo reliability.** Three separate machines means three things that can fail on the
   day. A single container that hosts all three attack surfaces is simpler to start, simpler
   to verify, and simpler to recover if something goes wrong mid-demo.

2. **It is actually realistic.** In the real world, an unpatched Apache server does not
   have just one vulnerability — it has every vulnerability in that version. Our three CVEs
   all affect Apache HTTP Server 2.4.68 and are all fixed in 2.4.69. Running them on the
   same server mirrors what an actual pentest would find: one target, multiple weaknesses,
   and an attack chain that connects them.

We pinned the target to `httpd:2.4.68`, the exact Docker Hub image for the last affected
version. No source patches, no custom builds — stock Apache with the bugs still in it.

---

## Why Two Containers Instead of One

One of the three CVEs (CVE-2026-63686, the mod_xml2enc NULL pointer dereference) requires
Apache to reverse-proxy a response from a backend server. The bug triggers when the
charset declared in the response header does not match the actual byte encoding of the
body — Apache's charset conversion filter crashes trying to convert it.

We needed something behind the reverse proxy for this to work. Rather than pointing Apache
at a random external site (which would break isolation and make the trigger
uncontrollable), we built a small Python HTTP server as a second container. It serves a
normal-looking HTML page by default, but accepts query parameters like `charset=`,
`encode_as=`, and `truncate=` that let us shape the response to trigger the crash.

This second container (`acw3-backend`) has no published ports — it sits on the internal
Docker network (`labnet`) and is reachable only through Apache's `/proxy/` path. That
matches the CVE's attack path exactly: the attacker hits the Apache proxy endpoint, not
the backend directly.

---

## How the Apache Config Was Wired Up

We did not modify Apache's source code or replace any modules. Instead, we wrote a single
overlay config file (`conf/httpd-vuln.conf`) that gets included on top of the default
`httpd.conf` at startup. This file does three things, each one matching a precondition
from a CVE record:

**For CVE-2026-93546 (mod_dav_fs integer overflow):** We enabled WebDAV on the `/dav/`
directory and gave the digest-authenticated user write access. The CVE requires an
authenticated WebDAV client that can send `PROPPATCH` requests — without WebDAV turned on
and a writable directory, the vulnerable code path never executes.

**For CVE-2026-73636 (mod_auth_digest nonce replay):** Inside the same `/dav/` directory
block, we set `AuthDigestNonceLifetime 0`. This is the specific misconfiguration the CVE
record calls out. Normally, digest auth nonces expire after a few minutes, so a captured
`Authorization` header stops working quickly. Setting the lifetime to zero means nonces
never expire — a single captured header can be replayed indefinitely.

**For CVE-2026-63686 (mod_xml2enc NULL pointer dereference):** We configured `/proxy/` as
a reverse proxy to the backend container, with the `proxy-html` output filter and
`ProxyHTMLCharsetOut *` enabled. This activates mod_xml2enc's charset conversion on every
proxied response, which is where the NULL dereference lives.

The reason we kept everything in one config file rather than scattering directives across
multiple files is traceability: anyone on the team can open `httpd-vuln.conf`, see exactly
what was changed from the default Apache setup, and map each block to the CVE it supports.

---

## Why We Added a Themed Portal

A bare Apache "It works!" page would have been functional, but it makes the demo harder to
follow. The instructors would see curl output and raw HTTP responses without any context
for what the "company" is or why the endpoints exist.

So we built **Fieldstone Docs**, a fictional internal company portal. It has a homepage, a
styled shared-drive directory listing behind the digest login, and a news mirror page
served through the reverse proxy. All the sample documents on the shared drive
(financial summaries, meeting notes, client briefs) are fake but plausible — they give
the demo a narrative: "this is a company's internal site, here is what an attacker can
reach, here is what they can steal or break."

This took extra effort, but it means the demo tells a story instead of just showing
terminal output.

---

## Safety Decisions

### Memory Cap on the Target Container

During early testing of CVE-2026-93546, we found that the crafted `PROPPATCH` payload
amplifies roughly 1 MB of XML into multiple gigabytes of memory inside the Apache worker.
On one test run, the host machine's RAM usage climbed past 10 GB before the process
finally crashed. That would be disastrous on a demo laptop.

We solved this by setting `mem_limit: 512m` and `memswap_limit: 512m` in the Compose
file. The Apache worker now hits the container's memory ceiling and dies within seconds.
The denial-of-service effect is clearly visible, the laptop stays safe, and the behaviour
actually models a real server with finite resources — it does not change whether the bug
is present, only how fast the crash happens.

### Network Isolation

The Docker bridge network `labnet` is internal to the host. The backend container has no
port mappings at all. The target container exposes only port 8080 on localhost. Nothing is
reachable from outside the machine unless you deliberately change the configuration.

### No Real Data

Every document, name, company, and news article in the environment is fabricated sample
data. If the environment were accidentally left running or someone browsed to it, there is
nothing sensitive to leak.

---