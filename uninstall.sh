# saternet uninstall.sh
# Removes saternet from the system.

set -e

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
  uninstaller

EOF
}

log() { printf "  %s\n" "$1"; }
ok()  { printf "  ok   %s\n" "$1"; }
warn(){ printf "  warn %s\n" "$1"; }

print_banner

# Determine install mode
if [ "$EUID" -eq 0 ]; then
    BIN_PATHS=("/usr/local/bin/saternet" "/usr/bin/saternet")
    LIB_PATHS=("/usr/local/lib/saternet")
    ICON_PATHS=("/usr/share/pixmaps/saternet.png")
    DESKTOP_PATHS=("/usr/share/applications/saternet.desktop")
else
    BIN_PATHS=("$HOME/.local/bin/saternet")
    LIB_PATHS=("$HOME/.local/lib/saternet")
    ICON_PATHS=("$HOME/.local/share/pixmaps/saternet.png")
    DESKTOP_PATHS=("$HOME/.local/share/applications/saternet.desktop")
fi

CONFIG_DIR="$HOME/.config/saternet"

log "removing saternet ..."
echo

# Remove binary
for f in "${BIN_PATHS[@]}"; do
    if [ -f "$f" ]; then
        rm -f "$f"
        ok "removed binary     $f"
    fi
done

# Remove library
for d in "${LIB_PATHS[@]}"; do
    if [ -d "$d" ]; then
        rm -rf "$d"
        ok "removed library    $d"
    fi
done

# Remove icon
for f in "${ICON_PATHS[@]}"; do
    if [ -f "$f" ]; then
        rm -f "$f"
        ok "removed icon       $f"
    fi
done

# Remove desktop entry
for f in "${DESKTOP_PATHS[@]}"; do
    if [ -f "$f" ]; then
        rm -f "$f"
        ok "removed desktop    $f"
        if command -v update-desktop-database &>/dev/null; then
            update-desktop-database "$(dirname "$f")" 2>/dev/null || true
        fi
    fi
done

# Ask about config
echo
log "config directory found at  $CONFIG_DIR"
printf "  remove config and logs? [yes/no]: "
read -r answer

if [ "$answer" = "yes" ]; then
    rm -rf "$CONFIG_DIR"
    ok "removed config     $CONFIG_DIR"
else
    log "keeping config at  $CONFIG_DIR"
fi

echo
ok "saternet uninstalled"
echo
