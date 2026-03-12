SOCIAL QUICK CHECKS — one-page reference (no1r)

Before any external post (no1r-1 must confirm):

1) Has an elevation JSON been created in exchange/elevations/?
   - Fields required: summary, recommended_action, confidence, watch_items, audit_reference
2) Is audit_reference present and pointing to the SimulationReport or exchange report? (no1r-1 must verify)
3) Does the suggested post avoid persuasion/urgency language? (no false scarcity)
4) Is the post marked irreversible or broad_reach? If yes, wait 30 minutes + require second confirmation.
5) Confirm policy_tension/legal_adj flags are escalated to operator (Sen) before posting.

Quick approval CLI (one-liner):
- /home/sntrblck/.openclaw/workspace/scripts/approve_elevation.sh

Templates (copy/paste):
- Health alert: "[no1r] ALERT — {summary}. See {audit_reference}."
- Governance update: "[no1r] Governance update: {one_line_summary}. Details: {audit_reference}."

If you want, I can add a short GitHub Actions check to block direct pushes to a 'production-posts' branch unless 'approved' files exist in exchange/approved/. Want me to add that as well? (Yes/No)
