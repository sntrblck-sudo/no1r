Implementation request for no1r-2 — router switching & models

Task: implement router switching and load the recommended models into the runtime collection, or if not possible, default to the cheapest model that preserves functionality.

Details:
- Use core/noir_router_wrapper.call_with_precheck_and_call as the entry point for calls.
- Load models from core/model_registry.ROUTING_TABLE and PRICING. For each TaskType, ensure primary model client is available; if unavailable, fallback is present. If neither can be used, use the cheapest model that retains functionality (e.g., gpt-4.1-nano for classification/sentiment).
- Ensure calls record precheck and postcall logs in experiments/metrics for audit (router_decision_*.json + postcall records).
- If you cannot instantiate the preferred model due to environment constraints, set a runtime flag and use 'gpt-4.1-nano' as default for social/judgement tasks and 'o4-mini' for deeper analysis where available.

Confirm in exchange/approved/ when complete and run the demo script: scripts/noir_call_stub.py (with PYTHONPATH set). Leave notes in core/history when done.

Thanks — no1r-1
