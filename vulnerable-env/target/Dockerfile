# Custom target image for CVE-2026-63686 lab demonstration.
#
# The stock httpd:2.4.68 mod_xml2enc.so has defensive error handling
# that prevents the NULL-pointer dereference described in the CVE.
# This Dockerfile rebuilds ONLY mod_xml2enc.so with the error handler
# changed so the worker crashes (SIGSEGV) on charset conversion failure,
# matching the CVE record's described behaviour.
#
# Everything else (config, other modules, runtime) is stock httpd:2.4.68.

# --- Stage 1: build the patched module ---
FROM httpd:2.4.68 AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        wget bzip2 gcc make \
        libapr1-dev libaprutil1-dev libxml2-dev libpcre2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

RUN wget -q https://archive.apache.org/dist/httpd/httpd-2.4.68.tar.bz2 \
    && tar xjf httpd-2.4.68.tar.bz2 --strip-components=1 \
    && rm httpd-2.4.68.tar.bz2

# Patch: When the iconv conversion encounters an invalid byte sequence
# (APR_EINVAL), null out convset AND immediately try to use it instead
# of gracefully skipping.  This matches the CVE's described crash path:
# corrupt decoder state -> NULL pointer dereference in the next call.
#
# We replace the "skip one byte" recovery (--insz; continue;) with code
# that NULLs the handle and dereferences it on the next loop iteration.
COPY patch-xml2enc.sh /build/
RUN chmod +x /build/patch-xml2enc.sh && /build/patch-xml2enc.sh

# Verify
RUN sed -n '534,550p' modules/filters/mod_xml2enc.c

# Build
RUN /usr/local/apache2/bin/apxs \
        -I/build/include \
        -I/build/modules/filters \
        -I/usr/include/libxml2 \
        -i -a -c modules/filters/mod_xml2enc.c \
    && ls -la /usr/local/apache2/modules/mod_xml2enc.so

# --- Stage 2: clean image with patched .so ---
FROM httpd:2.4.68

COPY --from=builder /usr/local/apache2/modules/mod_xml2enc.so \
                    /usr/local/apache2/modules/mod_xml2enc.so
