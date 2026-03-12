#!/bin/bash
# Summarize recent paper trading steps and write a short report to exchange/
DIR=/home/sntrblck/.openclaw/workspace/experiments/simulations/paper_trading
OUT=/home/sntrblck/.openclaw/workspace/exchange/paper_trading_summary_$(date -u +%Y%m%dT%H%M%SZ).md

if [ ! -d "$DIR" ]; then
  echo "No paper trading data yet" > "$OUT"
  exit 0
fi

# Simple summary: count reports, final balance
LAST=$(ls -1 "$DIR" | tail -n 1)
FINAL_BAL=$(jq -r '(.days|last).balance' "$DIR/$LAST" 2>/dev/null || echo 'unknown')
COUNT=$(ls -1 "$DIR" | wc -l)

cat > "$OUT" <<EOF
# Paper trading pilot summary — $(date -u +%Y-%m-%dT%H:%M:%SZ)

- Reports collected: $COUNT
- Latest report: $LAST
- Latest end balance (approx): $FINAL_BAL

Please review experiments/simulations/paper_trading for details.
EOF

echo "Wrote $OUT"
