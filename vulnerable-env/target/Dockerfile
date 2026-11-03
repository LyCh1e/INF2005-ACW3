# Custom target image for CVE-2026-63686 lab demonstration.
#
# The stock httpd:2.4.68 mod_xml2enc.so contains a defensive null-guard
# on ctx->convset (line 409) that was added as a hardening measure.
# The CVE describes a NULL-pointer dereference when charset conversion
# is attempted on a proxied response with a mismatched declared charset.
# This Dockerfile rebuilds ONLY mod_xml2enc.so with that null-guard
# disabled so the filter proceeds into the conversion path with a NULL
# convset, reproducing the crash (SIGSEGV) described in the CVE record.
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

# Patch: disable the null-guard on ctx->convset at line 409 of
# mod_xml2enc.c. With the guard removed, the filter enters the
# apr_xlate_conv_buffer() loop even when convset is NULL, causing a
# NULL-pointer dereference (SIGSEGV) — the crash path described by CVE.
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
