Noir Router Integration — cost precheck wrapper (short README)

Purpose
- Provide a simple drop‑in that prevents model calls from exceeding a per‑call budget and logs routing decisions for audit.

Files
- core/model_cost_precheck.py — utilities to estimate tokens and cost; should_call(model, messages, budget_cap_usd)
- core/noir_router_wrapper.py — call_with_precheck(task_type, messages, budget_cap_usd, primary, fallback, out_tokens)
  - Returns (chosen_model_or_None, reason, estimated_cost_usd) and writes a decision record to experiments/metrics.

How to integrate (minimal)
1) Import wrapper at the top of your router code:
   from core.noir_router_wrapper import call_with_precheck

2) Replace direct model selection logic with a precheck step:
   chosen, reason, est = call_with_precheck(task_type, messages, budget_cap_usd, primary_model, fallback_model)
   if chosen is None:
       # handle over-budget: raise, queue, or return safe fallback
   else:
       # proceed to call the chosen model with your existing client
       result = call_model(chosen, messages, max_tokens=out_tokens)
       # after call, append actual cost to the decision log (for reconciliation)

3) Post-call reconciliation (recommended)
   - Write actual_cost_usd, cached_flag, and model_used into experiments/metrics record (match by timestamp or correlation id).

Notes & tips
- The cost estimate is intentionally coarse (chars→tokens heuristic). For production, integrate a token counter library (tiktoken or similar) to get accurate token counts.
- Keep PRICING table in core/model_cost_precheck.py up to date with provider pricing; consider sourcing from a central config.
- Ensure experiments/metrics is rotated and archived; do not store sensitive inputs.

Example
- See scripts/noir_call_stub.py for a quick demo of fallback logic.

Contact
- no1r-1 (ops) — ping if you want the wrapper adapted to a specific router implementation.
