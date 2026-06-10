#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

VERSION="0.1.0.dev1"
RELEASE_DIR="$ROOT/packaging/release"
ARTIFACT_DIR="$RELEASE_DIR/artifacts/macos-developer-preview"
METADATA="$RELEASE_DIR/developer-preview-macos.json"
SHA_FILE="$RELEASE_DIR/SHA256SUMS.txt"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    return 1
  fi
}

require_command python3
require_command shasum
require_command /usr/bin/iconutil

if command -v uv >/dev/null 2>&1; then
  PYTHON_RUN=(uv run --no-project --python 3.12 --with 'briefcase>=0.3.26,<0.4' python)
else
  PYTHON_RUN=(python3)
  if ! "${PYTHON_RUN[@]}" -m briefcase --version >/dev/null 2>&1; then
    cat >&2 <<'EOF'
Briefcase is not available and uv is not installed.
Install uv or install Briefcase for release builds:
  python3 -m pip install 'briefcase>=0.3.26,<0.4'
EOF
    exit 1
  fi
fi

"${PYTHON_RUN[@]}" -m briefcase --version >/dev/null

"${PYTHON_RUN[@]}" scripts/release/build_app_icon.py
"${PYTHON_RUN[@]}" scripts/release/fetch_wezterm.py
"${PYTHON_RUN[@]}" scripts/release/verify_public_source.py --manifest-only
"${PYTHON_RUN[@]}" scripts/release/export_public_source.py --no-zip
"${PYTHON_RUN[@]}" scripts/release/verify_public_source.py

if [[ -d build ]] && find build -path '*Exegesis.app' -type d | grep -q .; then
  "${PYTHON_RUN[@]}" -m briefcase update macOS --no-input --update-resources
else
  "${PYTHON_RUN[@]}" -m briefcase create macOS --no-input
fi
"${PYTHON_RUN[@]}" -m briefcase build macOS --no-input

APP_BUNDLE="$(find build -path '*Exegesis.app' -type d | sort | tail -1)"
if [[ -z "$APP_BUNDLE" ]]; then
  echo "Briefcase did not produce Exegesis.app under build/." >&2
  exit 1
fi

"${PYTHON_RUN[@]}" scripts/release/patch_macos_app_identity.py --copy-wezterm "$APP_BUNDLE"

"${PYTHON_RUN[@]}" -m briefcase package macOS --no-input --adhoc-sign --no-notarize --packaging-format zip

rm -rf "$ARTIFACT_DIR"
mkdir -p "$ARTIFACT_DIR"
APP_ZIP="$ARTIFACT_DIR/Exegesis-${VERSION}-macos-arm64-developer-preview.app.zip"

/usr/bin/ditto -c -k --keepParent "$APP_BUNDLE" "$APP_ZIP"
"${PYTHON_RUN[@]}" scripts/release/export_public_source.py --output "$RELEASE_DIR/public-source/exegesis-developer-preview-source" >/dev/null

{
  shasum -a 256 "$APP_ZIP"
} | sed "s#$ROOT/##" > "$SHA_FILE"

cat > "$METADATA" <<EOF
{
  "name": "Exegesis Developer Preview",
  "version": "$VERSION",
  "bundle_id": "studio.exegesis.developer",
  "platform": "macOS Apple Silicon",
  "wezterm_version": "20240203-110809-5046fc22",
  "app_zip": "${APP_ZIP#$ROOT/}",
  "sha256sums": "${SHA_FILE#$ROOT/}"
}
EOF

echo "Built Exegesis Developer preview artifacts:"
echo "  ${APP_ZIP#$ROOT/}"
echo "  ${SHA_FILE#$ROOT/}"
