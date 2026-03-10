# no1r Cold Start / Replanting Guide

Version: 2026-03-10

This document describes how to bring **no1r** online on a new machine or after a clean install, using this workspace and a minimal OpenClaw setup.

> Assumption: You have access to this Git repo (workspace) and can install OpenClaw.

---

## 1. Host Requirements

- OS: Modern 64-bit Linux recommended.
- Network: Outbound HTTPS (for OpenClaw gateway + any external APIs you explicitly use).
- Disk: Enough for logs, state, and this repo (a few GB is plenty to start).
- CPU/RAM: modest; no heavy local models assumed.

---

## 2. Install OpenClaw

1. Install Node and npm.
2. Install OpenClaw (example):

   ```bash
   npm install -g openclaw@latest
   openclaw onboard
   ```

3. Confirm it runs:

   ```bash
   openclaw status
   ```

   You should see a gateway and dashboard.

(If using a managed app / different install method, follow the official OpenClaw docs for that environment.)

---

## 3. Clone the no1r Workspace

On the new host:

```bash
cd ~
# Replace with your actual repo URL
git clone https://github.com/your-user/your-no1r-repo.git no1r
cd no1r
```

If OpenClaw expects a specific workspace path (e.g., `~/.openclaw/workspace`), either:

- point OpenClaw at this repo directory in its config, or
- move/symlink this repo to `~/.openclaw/workspace`.

Example (destructive if workspace exists):

```bash
rm -rf ~/.openclaw/workspace
mv ~/no1r ~/.openclaw/workspace
```

Adjust paths to match your environment.

---

## 4. Core Services to Enable

From the workspace (`~/.openclaw/workspace`):

- **Sentinel** – the ops monitor:
  - Ensure `sentinel.service` is installed under systemd (or equivalent) and enabled.
  - Start/restart:
    ```bash
    sudo systemctl enable sentinel.service
    sudo systemctl start sentinel.service
    ```

- **Autocommit** – optional but recommended:
  - Ensure `autocommit.service` is installed and enabled to keep Git history flowing.
  - Start/restart similarly.

Check that Sentinel is responding:

```bash
curl -s http://localhost:18799/health
```

You should see a small JSON blob with `"status": "ok"` when healthy.

---

## 5. Identity & Guardrails

The portable identity core lives in:

- `no1r_identity.md` – who no1r is; values, guardrails, focus areas.
- `DISPOSITION.md` – operational stance and hard NOs.
- `ARCHITECTURE_ROADMAP.md` – high-level system overview.

If you ever need to verify or explain no1r's behavior on a new host, start with these files.

---

## 6. Nervous System (Tasks)

The main entry point is `no1r.py`.

From the workspace:

```bash
python3 no1r.py --task <name>
```

See `NO1R_TASKS.md` for a description of each task.

Typical first runs on a new host:

```bash
python3 no1r.py --task ops-inbox
python3 no1r.py --task inclawbate-analytics
python3 no1r.py --task patterns-mirror
```

These will:

- confirm OpenClaw/Sentinel/cron are visible,
- fetch Inclawbate analytics (read-only) and align attention,
- generate `patterns.md` with a quick view of current patterns.

---

## 7. Channels (Optional)

If you want no1r to talk to you over Telegram (or other channels):

- Configure the channel in your OpenClaw config (bot token, chat ID, etc.).
- Ensure the relevant OpenClaw channel integrations are enabled.

no1r itself doesn't need special wiring here; OpenClaw routes messages into the workspace.

---

## 8. Safety Check on a New Host

After a cold start, verify:

1. Identity/guardrails:
   - Read `no1r_identity.md` and `DISPOSITION.md` – confirm they match your expectations.

2. Ops health:
   - Run `python3 no1r.py --task ops-inbox` and confirm OPS/CRON/DFI look reasonable.

3. Logs & state:
   - Check `sentinel.log`, `ops_state.json`, `attention_items.jsonl` for obvious errors.

If anything looks wrong, pause and fix that before adding new tasks or freedoms.

---

## 9. Notes

- This guide intentionally avoids stack-specific tricks; it should work across most Linux + OpenClaw setups.
- If a future environment uses a different orchestrator, the key ideas remain:
  - clone this workspace,
  - respect `no1r_identity.md` and DISPOSITION,
  - rewire the few core services (Sentinel equivalent, cron/automation, task registry),
  - and keep the core state files (`working_context.json`, `attention_items.jsonl`, `ops_state.json`) intact.
