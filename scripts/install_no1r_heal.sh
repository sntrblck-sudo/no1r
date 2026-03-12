#!/bin/bash
# One-shot installer for no1r heal helper (run as root)
set -euo pipefail

echo "Installing no1r heal wrapper and sudoers entry..."

# Paths
SRC="/home/sntrblck/.openclaw/workspace/core/no1r_heal_gateway.sh"
DEST="/usr/local/bin/no1r_heal_gateway.sh"
SUDOERS="/etc/sudoers.d/no1r_heal"
LOGFILE="/var/log/no1r_heal.log"
DISABLE_DIR="/etc/no1r"
USER=no1r_heal

# Create system user if missing
if ! id -u "$USER" >/dev/null 2>&1; then
  useradd --system --no-create-home --shell /usr/sbin/nologin "$USER" || true
  echo "Created system user $USER"
fi

# Install wrapper
cp "$SRC" "$DEST"
chown root:root "$DEST"
chmod 750 "$DEST"

# Prepare dirs and logs
mkdir -p "$DISABLE_DIR"
touch "$LOGFILE" || true
chown root:adm "$LOGFILE" || true
chmod 640 "$LOGFILE"

# Install sudoers
cat > "$SUDOERS" <<'EOF'
no1r_heal ALL=(root) NOPASSWD: /usr/local/bin/no1r_heal_gateway.sh
EOF
chmod 440 "$SUDOERS"

# Validate sudoers
if visudo -c; then
  echo "sudoers syntax OK"
else
  echo "visudo check failed" >&2
  exit 2
fi

# Final notes
echo "Installed wrapper at $DEST"
echo "Sudoers entry written to $SUDOERS"
echo "Log file: $LOGFILE"

echo "To test (manual): sudo $DEST"

echo "If you want me to verify installation remotely, run this script and then tell me to proceed with verification."
