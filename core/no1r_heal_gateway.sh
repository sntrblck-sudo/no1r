#!/bin/bash
# Wrapper script for minimal heal action: restart/openclaw-gateway.service
# Intended to be run via sudo by dedicated user (no1r_heal)

LOG=/var/log/no1r_heal.log
DISABLE_FLAG=/etc/no1r/heal_disabled
RATEFILE=/var/run/no1r_heal_last

# Check disable flag
if [ -f "$DISABLE_FLAG" ]; then
  echo "$(date -u +%FT%TZ) - heal disabled via $DISABLE_FLAG" >> "$LOG"
  exit 2
fi

# Rate limit: no more than one restart per 300 seconds
if [ -f "$RATEFILE" ]; then
  last=$(cat "$RATEFILE")
  now=$(date +%s)
  diff=$((now - last))
  if [ "$diff" -lt 300 ]; then
    echo "$(date -u +%FT%TZ) - rate-limited: only $diff seconds since last heal" >> "$LOG"
    exit 3
  fi
fi

# Log intent
echo "$(date -u +%FT%TZ) - heal requested: restarting openclaw-gateway.service" >> "$LOG"

# Perform restart and capture status
if /bin/systemctl restart openclaw-gateway.service; then
  /bin/systemctl status openclaw-gateway.service --no-pager >> "$LOG" 2>&1
  echo "$(date -u +%FT%TZ) - heal success" >> "$LOG"
  date +%s > "$RATEFILE"
  exit 0
else
  echo "$(date -u +%FT%TZ) - heal failed" >> "$LOG"
  /bin/systemctl status openclaw-gateway.service --no-pager >> "$LOG" 2>&1
  exit 4
fi
