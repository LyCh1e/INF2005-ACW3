#!/usr/bin/env bash
# ACW3 lab runner — macOS / Linux.
# Rebuilds the images from the current source and (re)starts the target +
# backend containers defined in vulnerable-env/docker-compose.yml.
#
# Usage:
#   ./run.sh              build (using cache) and start/recreate the lab
#   ./run.sh --no-cache   force a full rebuild with no Docker layer cache
#   ./run.sh down         stop and remove the containers

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
ENV_DIR="$SCRIPT_DIR/vulnerable-env"
DIGEST_FILE="$ENV_DIR/conf/digest.passwd"
DIGEST_USER="labuser"
DIGEST_REALM="acw3-dav"
DIGEST_PASS="labpass123"

cd "$ENV_DIR"

compose() {
  if docker compose version >/dev/null 2>&1; then
    docker compose "$@"
  else
    docker-compose "$@"
  fi
}

if [[ "${1:-}" == "down" ]]; then
  echo "==> Stopping ACW3 lab"
  compose down
  exit 0
fi

NO_CACHE=()
if [[ "${1:-}" == "--no-cache" ]]; then
  NO_CACHE=(--no-cache)
fi

echo "==> Checking Docker is running"
if ! docker info >/dev/null 2>&1; then
  echo "Docker does not appear to be running. Start Docker Desktop (or the"
  echo "Docker daemon) and re-run this script." >&2
  exit 1
fi

if [[ ! -f "$DIGEST_FILE" ]]; then
  echo "==> No digest.passwd found, creating default lab credentials ($DIGEST_USER/$DIGEST_PASS)"
  mkdir -p "$ENV_DIR/conf"
  if command -v md5sum >/dev/null 2>&1; then
    HASH="$(printf '%s' "$DIGEST_USER:$DIGEST_REALM:$DIGEST_PASS" | md5sum | awk '{print $1}')"
  else
    # macOS/BSD
    HASH="$(printf '%s' "$DIGEST_USER:$DIGEST_REALM:$DIGEST_PASS" | md5 -q)"
  fi
  printf '%s:%s:%s\n' "$DIGEST_USER" "$DIGEST_REALM" "$HASH" > "$DIGEST_FILE"
fi

echo "==> Building images from the latest source"
compose build "${NO_CACHE[@]}"

echo "==> Starting the lab (recreating containers with the new images)"
compose up -d --force-recreate

echo "==> Containers:"
compose ps

cat <<'EOF'

ACW3 lab is up:
  Site:           http://localhost:8080/
  WebDAV (dav):   http://localhost:8080/dav/   (digest auth, see README for creds)
  Reverse proxy:  http://localhost:8080/proxy/
  CVE map:        http://localhost:8080/cve-map.html

Tear down with:  ./run.sh down
EOF
