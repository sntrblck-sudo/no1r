#!/usr/bin/env python3
"""
Watchdog - Monitors Sentinel and restarts if dead
"""

import os
import sys
import time
import subprocess
import signal
import json
from pathlib import Path

SENTINEL_PID_FILE = Path(__file__).parent / "sentinel_state.json"
SENTINEL_SCRIPT = Path(__file__).parent / "sentinel.py"
LOG_FILE = Path(__file__).parent / "watchdog.log"
CHECK_INTERVAL = 60  # 1 min


def log(msg):
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
            f.flush()
    except:
        pass


def is_sentinel_alive():
    try:
        if not SENTINEL_PID_FILE.exists():
            return False
        
        with open(SENTINEL_PID_FILE) as f:
            state = json.load(f)
        
        pid = state.get("pid")
        if not pid:
            return False
        
        os.kill(pid, 0)
        return True
        
    except:
        return False


def start_sentinel():
    log("Starting Sentinel...")
    try:
        subprocess.Popen(
            ["python3", str(SENTINEL_SCRIPT)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        time.sleep(3)
        
        if is_sentinel_alive():
            log("Sentinel started")
            return True
        return False
    except Exception as e:
        log(f"Start failed: {e}")
        return False


def main():
    log("=== Watchdog v2 Starting ===")
    sys.stdout.flush()
    
    consecutive_failures = 0
    
    while True:
        try:
            alive = is_sentinel_alive()
            
            if alive:
                if consecutive_failures > 0:
                    log(f"Recovered ({consecutive_failures} fails)")
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                log(f"Dead (#{consecutive_failures})")
                
                if consecutive_failures >= 2:
                    start_sentinel()
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("Stopped")
            break
        except Exception as e:
            log(f"Error: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
