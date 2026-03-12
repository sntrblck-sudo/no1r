#!/bin/bash
# One-shot setup script for enabling OpenAI client for no1r on this host.
# Installs SDK (user), prompts for OPENAI_API_KEY, adds to ~/.profile, and runs a smoke async test.
set -euo pipefail

echo "Installing OpenAI Python SDK (user install)..."
python3 -m pip install --user openai

read -p "Paste your OPENAI_API_KEY (sk-...): " KEY
if [ -z "$KEY" ]; then
  echo "No key provided; aborting."; exit 1
fi

# Persist in ~/.profile if not present
PROFILE=${HOME}/.profile
if ! grep -q OPENAI_API_KEY "$PROFILE" 2>/dev/null; then
  echo "export OPENAI_API_KEY='$KEY'" >> "$PROFILE"
  echo "Added OPENAI_API_KEY to $PROFILE"
else
  echo "OPENAI_API_KEY already present in $PROFILE (not overwriting)."
fi

# Also export for current shell
export OPENAI_API_KEY="$KEY"

echo "Running smoke test..."
python3 - <<'PY'
import asyncio, os
from openai import AsyncOpenAI
async def main():
    client = AsyncOpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    r = await client.chat.completions.create(model='gpt-4.1-nano', messages=[{'role':'user','content':'Hello from no1r smoke test'}], max_tokens=16)
    print('SMOKE OK ->', r.choices[0].message.content)

asyncio.run(main())
PY

if [ $? -eq 0 ]; then
  echo "Smoke test succeeded. To make the router use precheck, add the following lines where you select models:"
  echo
  echo "from core.noir_router_wrapper import call_with_precheck_and_call"
  echo "resp = call_with_precheck_and_call(task_type, messages, budget_cap_usd, primary_model, fallback_model)"
  echo "if not resp['ok']: handle_over_budget(resp['reason']); else: result = resp['result'] # contains content and usage"
  echo
  echo "Done. Restart any user timers or shells to pick up ~/.profile." 
else
  echo "Smoke test failed — check error output above."
fi
