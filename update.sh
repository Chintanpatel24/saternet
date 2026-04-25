#!/usr/bin/env bash

# saternet update.sh
# Fetches the latest version from the repository and reinstalls.

set -e

REPO_URL="https://github.com/yourusername/saternet"
INSTALL_SCRIPT="install.sh"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_banner() {
cat << 'EOF'

 ___  _   _____ ___ ___ _  _ ___ _____
/ __|| | |_   _| __| _ \ \| | __|_   _|
\__ \| |__ | | | _||   / .` | _|  | |
|___/|____||_| |___|_|_\_|\_|___| |_|

  updater

EOF
}

log() { printf "  %s\n" "$1"; }
ok()  { printf "  ok   %s\n" "$1"; }
err() { printf "  err  %s\n" "$1" >&2; exit 1; }

print_banner

# Check if this is a git repo
if [ -d "$SCRIPT_DIR/.git" ]; then
    log "fetching latest changes from remote ..."
    cd "$SCRIPT_DIR"

    if ! command -v git &>/dev/null; then
        err "git is not installed. install git to use the updater."
    fi

    git fetch origin
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main 2>/dev/null || git rev-parse origin/master 2>/dev/null)

    if [ "$LOCAL" = "$REMOTE" ]; then
        ok "already up to date"
        echo
        exit 0
    fi

    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null
    ok "pulled latest changes"
else
    log "not a git repository, downloading from $REPO_URL ..."

    if command -v curl &>/dev/null; then
        TMPDIR=$(mktemp -d)
        curl -fsSL "$REPO_URL/archive/refs/heads/main.tar.gz" -o "$TMPDIR/saternet.tar.gz"
        tar -xzf "$TMPDIR/saternet.tar.gz" -C "$TMPDIR"
        EXTRACTED=$(ls "$TMPDIR" | grep saternet | head -1)
        cp -r "$TMPDIR/$EXTRACTED/." "$SCRIPT_DIR/"
        rm -rf "$TMPDIR"
        ok "downloaded latest release"
    elif command -v wget &>/dev/null; then
        TMPDIR=$(mktemp -d)
        wget -q "$REPO_URL/archive/refs/heads/main.tar.gz" -O "$TMPDIR/saternet.tar.gz"
        tar -xzf "$TMPDIR/saternet.tar.gz" -C "$TMPDIR"
        EXTRACTED=$(ls "$TMPDIR" | grep saternet | head -1)
        cp -r "$TMPDIR/$EXTRACTED/." "$SCRIPT_DIR/"
        rm -rf "$TMPDIR"
        ok "downloaded latest release"
    else
        err "curl or wget is required to download updates"
    fi
fi

# Reinstall
log "reinstalling ..."
echo

if [ "$EUID" -eq 0 ]; then
    bash "$SCRIPT_DIR/$INSTALL_SCRIPT"
else
    bash "$SCRIPT_DIR/$INSTALL_SCRIPT"
fi

ok "saternet updated successfully"
echo
