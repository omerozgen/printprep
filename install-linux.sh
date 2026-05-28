#!/usr/bin/env bash
# Two roles:
#   - With no args: install the PrintPrep.desktop launcher into the user's
#     applications dir (substituting absolute paths from this checkout).
#   - With "run" as the first arg (used by the .desktop Exec line): just start
#     the desktop app (`printprep app`, falling back to `serve` + xdg-open).
set -e

PROJECT="$(cd "$(dirname "$0")" && pwd)"
VENV_PP="$PROJECT/venv/bin/printprep"
VENV_PY="$PROJECT/venv/bin/python"

if [ "$1" = "run" ]; then
    if [ ! -x "$VENV_PP" ] || [ ! -x "$VENV_PY" ]; then
        echo "PrintPrep venv missing — run: pip install -e \".[web,desktop]\"" >&2
        exit 1
    fi
    if "$VENV_PY" -c "import webview" 2>/dev/null; then
        exec "$VENV_PP" app
    fi
    # Fallback: serve + xdg-open
    (sleep 1.5 && xdg-open http://127.0.0.1:8000) &
    exec "$VENV_PP" serve --host 127.0.0.1 --port 8000
fi

# Install mode.
DEST_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$DEST_DIR"
DEST="$DEST_DIR/printprep.desktop"

TEMPLATE="$PROJECT/PrintPrep.desktop"
if [ ! -f "$TEMPLATE" ]; then
    echo "Template not found: $TEMPLATE" >&2
    exit 1
fi

# Substitute the project path; the Exec line becomes "<project>/install-linux.sh run".
sed -e "s|__PROJECT__|$PROJECT|g" \
    -e "s|install-linux.sh %u|install-linux.sh run|" \
    "$TEMPLATE" > "$DEST"

# Update GNOME/KDE's launcher database if the tool is available.
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DEST_DIR" >/dev/null 2>&1 || true
fi

echo "Installed: $DEST"
echo "Now search for 'PrintPrep' in your application launcher, or pin it to the dock."
