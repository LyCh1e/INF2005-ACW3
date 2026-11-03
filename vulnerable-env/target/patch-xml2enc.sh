#!/bin/sh
# Patch mod_xml2enc.c for CVE-2026-63686 lab: remove the null-guard on
# ctx->convset so the filter dereferences it when charset conversion
# is attempted on a response with a declared charset.

set -e
SRC=modules/filters/mod_xml2enc.c

# Disable the null-guard early-return at line 409.
# This causes any response that enters the charset-conversion path to
# proceed into the conversion loop where ctx->convset may be NULL.
sed -i 's/if (!ctx->convset) {/if (0) { \/\* CVE-2026-63686 lab: guard disabled \*\//' "$SRC"

echo "Patch applied:"
grep -n "guard disabled" "$SRC"
