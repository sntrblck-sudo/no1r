HEAL_SUDO_PROPOSAL — minimal sudo policy for sentinel heal helper

Purpose
- Allow the sentinel heal helper to restart the openclaw-gateway service only, without granting broader sudo privileges.

Proposal
1. Create a dedicated user group and a wrapper script that performs only the required actions:
   - Script: /usr/local/bin/no1r_heal_gateway.sh
     - Allowed actions: systemctl restart openclaw-gateway.service; systemctl status openclaw-gateway.service
     - Script must log actions to /var/log/no1r_heal.log and enforce a rate limit (e.g., no more than 1 restart per 5 minutes).
2. Sudoers entry (visudo):
   - Add (restrictive) line:
     no1r_heal ALL=(root) NOPASSWD: /usr/local/bin/no1r_heal_gateway.sh
   - Alternatively, bind to the specific service control commands via systemctl with full path if script is not acceptable:
     no1r_heal ALL=(root) NOPASSWD: /bin/systemctl restart openclaw-gateway.service, /bin/systemctl status openclaw-gateway.service

Security controls
- Limit who can write the wrapper script (root only). Use checksum verification in sentinel before calling.
- Log every heal attempt; alert operator on automated heals with details and backtrace if restart fails.
- Add an enable/disable flag in sentinel_state.json so operator can toggle automated heals without editing sudoers.
- Rate-limit restarts and implement exponential backoff in wrapper script.

Approval path
- Operator (Sen) to authorize applying the sudoers change. After approval, I can:
  1. Create the wrapper script (owner=root, mode=750) and push it to /usr/local/bin (require manual placement or sudo to write).  
  2. Provide the exact visudo line for the operator to paste (or apply with sudo if operator grants me temporary elevation).

Rollback
- Remove the sudoers line and disable the wrapper script. The wrapper script should refuse to run if a global disable file exists (/etc/no1r/heal_disabled).

Notes
- This proposal minimizes scope: only service restart/status for the openclaw-gateway. It avoids granting broad systemctl or shell access.
- I will not apply the sudoers change without explicit operator credentials or an explicit command to apply it.
