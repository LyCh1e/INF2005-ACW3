Fieldstone Docs — Shared Drive (WebDAV)
=======================================

This folder is the team's shared drive. It is mounted read/write over
WebDAV at /dav/ on the portal, protected by HTTP Digest auth.

Any file you drop in here (via Explorer / Finder / cadaver / `curl -T`)
appears in the directory listing above and is editable by anyone else in
the team.

House rules
-----------
- Keep client-sensitive material inside a per-client subfolder.
- Lock a document while editing (your WebDAV client has a lock command;
  Apache enforces it via DavLockDB).
- Large binaries (> 50 MB) go on the object store instead.
- Please don't commit anything with real customer PII — this box is on
  the lab network and intentionally runs an old Apache build.

Contact IT (Arjun K.) if you need access.
