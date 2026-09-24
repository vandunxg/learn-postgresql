#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$ROOT/build/ui-bundle"
ARCHIVE="$ROOT/build/ui-bundle.zip"

rm -rf "$BUILD_DIR" "$ARCHIVE"
mkdir -p "$BUILD_DIR"
cp "$ROOT/ui.yml" "$BUILD_DIR/ui.yml"
cp -R "$ROOT/src/." "$BUILD_DIR/"

(cd "$BUILD_DIR" && zip -qr "$ARCHIVE" .)
printf '%s\n' "Antora UI bundle written to $ARCHIVE"
