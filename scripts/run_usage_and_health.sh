#!/usr/bin/env bash
set -euo pipefail
cd /home/thera/.openclaw/workspace
/usr/bin/python3 usage-monitor.py
/usr/bin/python3 model-health.py
