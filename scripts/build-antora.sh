#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLAYBOOK="$ROOT/playbook/antora-playbook.yml"

rm -rf "$ROOT/build/site"

if command -v antora >/dev/null 2>&1; then
  (cd "$ROOT/playbook" && antora antora-playbook.yml)
elif command -v npx >/dev/null 2>&1; then
  (cd "$ROOT/playbook" && npx --yes antora@3.2.0 antora-playbook.yml)
else
  printf '%s\n' 'Antora is not installed and npx is unavailable.' >&2
  exit 127
fi

test -d "$ROOT/build/site"
INDEX_DIR="$ROOT/build/site/learn-postgresql/main"
test -f "$INDEX_DIR/front-matter.html"
cp "$ROOT/scripts/site-index.html" "$INDEX_DIR/index.html"
test -f "$INDEX_DIR/index.html"
printf '%s\n' "Antora site written to $ROOT/build/site"
