#!/bin/bash
# Simple monitor: count heal requests in the last 30 minutes and alert if above threshold
LOG=/var/log/no1r_heal.log
THRESHOLD=3
WINDOW_MIN=30
STATE_JSON=/home/sntrblck/.openclaw/workspace/finance_state.json
SPEND_DISABLE=/etc/no1r/spend_disabled

if [ ! -f "$LOG" ]; then
  echo "no1r_heal log missing: $LOG"
else
  COUNT=$(awk -v d="$(date -d"-${WINDOW_MIN} minutes" +%Y-%m-%dT%H:%M)" '$0 > d && /heal requested/ {c++} END{print c+0}' "$LOG")

  if [ "$COUNT" -ge "$THRESHOLD" ]; then
    echo "ALERT: $COUNT heal requests in last $WINDOW_MIN minutes (threshold $THRESHOLD)"
    # Append a pending alert for operator review
    jq -n --arg ts "$(date -u +%FT%TZ)" --arg msg "Heal attempts high: $COUNT in last ${WINDOW_MIN}m" '{type: "health", timestamp: $ts, message: $msg}' >> .pending_alerts.json
  else
    echo "OK: $COUNT heal requests in last $WINDOW_MIN minutes"
  fi
fi

# Finance check: if simulated balance is negative, create spend disable and alert
if [ -f "$STATE_JSON" ]; then
  BAL=$(jq -r '.balance_sim // 0' "$STATE_JSON")
  if (( $(echo "$BAL < 0" | bc -l) )); then
    echo "Balance negative ($BAL) — creating spend disable"
    sudo mkdir -p /etc/no1r || true
    sudo touch "$SPEND_DISABLE" || true
    jq -n --arg ts "$(date -u +%FT%TZ)" --arg msg "Spend disabled: negative simulated balance ($BAL)" '{type: "finance", timestamp: $ts, message: $msg}' >> .pending_alerts.json
  fi
else
  echo "Finance state missing: $STATE_JSON"
fi
