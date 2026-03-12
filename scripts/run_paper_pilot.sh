#!/bin/bash
# Run the paper trading pilot in real time for a given duration
# Usage: nohup bash run_paper_pilot.sh &
DURATION_HOURS=${DURATION_HOURS:-72}
INTERVAL_MIN=${INTERVAL_MIN:-15}
ITER=$(( (DURATION_HOURS*60) / INTERVAL_MIN ))
for i in $(seq 1 $ITER); do
  echo "[$(date -Is)] step $i/$ITER"
  python3 /home/sntrblck/.openclaw/workspace/scripts/paper_trading_step.py
  sleep ${INTERVAL_MIN}m
done
echo "pilot complete"
