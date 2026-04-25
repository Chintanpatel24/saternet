# saternet install.sh
# Installs saternet on any Linux distribution.
# Usage: sudo bash install.sh   OR   bash install.sh (installs to ~/.local)

set -e

REPO_URL="https://github.com/yourusername/saternet"
VERSION="1.0.0"
TOOL_NAME="saternet"
SRC="src/saternet.py"
ICON_SRC="assets/saternet.png"
DESKTOP_SRC="assets/saternet.desktop"

# ──────────────────────────────────────────────
# DETECT INSTALL MODE
# ──────────────────────────────────────────────

if [ "$EUID" -eq 0 ]; then
    INSTALL_MODE="system"
    BIN_DIR="/usr/local/bin"
    LIB_DIR="/usr/local/lib/saternet"
    ICON_DIR="/usr/share/pixmaps"
    DESKTOP_DIR="/usr/share/applications"
else
    INSTALL_MODE="user"
    BIN_DIR="$HOME/.local/bin"
    LIB_DIR="$HOME/.local/lib/saternet"
    ICON_DIR="$HOME/.local/share/pixmaps"
    DESKTOP_DIR="$HOME/.local/share/applications"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_banner() {
cat << 'EOF'

────────────────────────────────────────────────────────────────────
███████╗ █████╗ ████████╗███████╗██████╗ ███╗   ██╗███████╗████████╗
██╔════╝██╔══██╗╚══██╔══╝██╔════╝██╔══██╗████╗  ██║██╔════╝╚══██╔══╝
███████╗███████║   ██║   █████╗  ██████╔╝██╔██╗ ██║█████╗     ██║   
╚════██║██╔══██║   ██║   ██╔══╝  ██╔══██╗██║╚██╗██║██╔══╝     ██║   
███████║██║  ██║   ██║   ███████╗██║  ██║██║ ╚████║███████╗   ██║   
╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   
────────────────────────────────────────────────────────────────────

  installer

EOF
}

log() { printf "  %s\n" "$1"; }
ok()  { printf "  ok   %s\n" "$1"; }
err() { printf "  err  %s\n" "$1" >&2; exit 1; }

# ──────────────────────────────────────────────
# CHECK PYTHON
# ──────────────────────────────────────────────

check_python() {
    if command -v python3 &>/dev/null; then
        PY_VERSION=$(python3 --version 2>&1)
        ok "python3 found  $PY_VERSION"
    else
        err "python3 is required but not installed"
    fi
}

# ──────────────────────────────────────────────
# INSTALL
# ──────────────────────────────────────────────

do_install() {
    print_banner
    log "install mode   $INSTALL_MODE"
    log "bin target     $BIN_DIR"
    log "lib target     $LIB_DIR"
    echo

    check_python

    # Create directories
    mkdir -p "$BIN_DIR" "$LIB_DIR" "$ICON_DIR" "$DESKTOP_DIR"

    # Copy main script
    cp "$SCRIPT_DIR/$SRC" "$LIB_DIR/saternet.py"
    chmod 644 "$LIB_DIR/saternet.py"

    # Write launcher
    cat > "$BIN_DIR/saternet" << LAUNCHER
#!/usr/bin/env bash
exec python3 "$LIB_DIR/saternet.py" "\$@"
LAUNCHER
    chmod 755 "$BIN_DIR/saternet"

    ok "installed binary   $BIN_DIR/saternet"
    ok "installed library  $LIB_DIR/saternet.py"

    # Install icon if present
    if [ -f "$SCRIPT_DIR/$ICON_SRC" ]; then
        cp "$SCRIPT_DIR/$ICON_SRC" "$ICON_DIR/saternet.png"
        ok "installed icon     $ICON_DIR/saternet.png"
    fi

    # Install desktop entry
    if [ -f "$SCRIPT_DIR/$DESKTOP_SRC" ]; then
        cp "$SCRIPT_DIR/$DESKTOP_SRC" "$DESKTOP_DIR/saternet.desktop"
        if command -v update-desktop-database &>/dev/null; then
            update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
        fi
        ok "installed desktop  $DESKTOP_DIR/saternet.desktop"
    fi

    # PATH check for user mode
    if [ "$INSTALL_MODE" = "user" ]; then
        if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
            echo
            log "add this to your .bashrc or .zshrc:"
            echo
            echo '    export PATH="$HOME/.local/bin:$PATH"'
            echo
        fi
    fi

    echo
    ok "saternet $VERSION installed successfully"
    echo
    log "run:  saternet"
    log "run:  saternet help"
    echo
}

do_install
