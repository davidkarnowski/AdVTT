"""Per-model capability map (Research/08 §5.2 item 2, Research/12 WP2).

Everything model-specific lives here so the adapters stay thin and a model
change is a one-row edit. Verified against the Claude API reference on
2026-09-06:

* Sonnet 5, Opus 5 and the Fable/Mythos 5 family: thinking is adaptive by
  default; `thinking: {type: "enabled", budget_tokens: N}` returns a 400;
  depth is `output_config.effort` in low | medium | high | xhigh | max.
* Haiku 4.5 and older: no `effort`; thinking needs `budget_tokens` (>= 1024,
  < max_tokens). Budget 0 means thinking off, which on this project's fixtures
  falsely marked 77.5 s of journalism as advertising. Leave the default alone.
* Structured outputs (`output_config.format`) are GA on all of them, and are
  incompatible with Citations, so quotes are resolved in code (the ladder).
* Prompt-cache floors: 1,024 tokens on Sonnet 5 / Opus 5; 4,096 on Haiku 4.5.

Prices are USD per million tokens (input / output) and are informational only;
the CLI reports its own `total_cost_usd` per call.
"""

CLAUDE_MODELS = {
    "claude-opus-5":    {"reasoning": "effort", "default_effort": "high", "cache_floor": 1024,
                         "price_in": 5.00, "price_out": 25.00, "context": 1_000_000},
    "claude-sonnet-5":  {"reasoning": "effort", "default_effort": "high", "cache_floor": 1024,
                         "price_in": 2.00, "price_out": 10.00, "context": 1_000_000},
    "claude-haiku-4-5": {"reasoning": "budget", "default_budget": None, "cache_floor": 4096,
                         "price_in": 1.00, "price_out": 5.00, "context": 200_000},
    "claude-opus-4-8":  {"reasoning": "effort", "default_effort": "high", "cache_floor": 1024,
                         "price_in": 5.00, "price_out": 25.00, "context": 1_000_000},
    "claude-sonnet-4-6": {"reasoning": "effort", "default_effort": "high", "cache_floor": 1024,
                          "price_in": 3.00, "price_out": 15.00, "context": 1_000_000},
}

_ALIASES = {"opus": "claude-opus-5", "sonnet": "claude-sonnet-5", "haiku": "claude-haiku-4-5"}

EFFORT_LEVELS = ("low", "medium", "high", "xhigh", "max")


def resolve_model(model):
    m = (model or "").strip()
    return _ALIASES.get(m, m)


def capabilities(model):
    """Capability row for a model id; unknown ids get a conservative default
    (effort-style reasoning, 1,024-token cache floor, no price)."""
    m = resolve_model(model)
    if m in CLAUDE_MODELS:
        return dict(CLAUDE_MODELS[m], model=m, known=True)
    # Heuristic for dated snapshots and future ids: 4.5-and-older need budgets.
    reasoning = "budget" if ("4-5" in m or "haiku" in m) else "effort"
    return {"model": m, "known": False, "reasoning": reasoning, "default_effort": "high",
            "default_budget": None, "cache_floor": 1024, "price_in": None, "price_out": None}


def estimate_cost_usd(model, tokens_in, tokens_out):
    cap = capabilities(model)
    if cap.get("price_in") is None or tokens_in is None or tokens_out is None:
        return None
    return round(tokens_in / 1e6 * cap["price_in"] + tokens_out / 1e6 * cap["price_out"], 6)
