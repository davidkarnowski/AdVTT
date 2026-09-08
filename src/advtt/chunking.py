"""Chunk planner. Chunking is an ACCURACY mechanism, not a context-window workaround:
on a 3919-segment episode a whole-transcript call found the right sponsor text at
segment 1245 instead of 445. 6000-token tiled windows matched ground truth exactly.
"""
# Moved verbatim from PodcastFetch adclass.py (commit 74692de, 2026-09-06),
# lines 1587-1635. Do not edit the moved bodies without bumping PROMPT_VERSION
# where the prompt or ladder behaviour changes; see Research/01 and 12.
from .validate import CONTEXT_SEGMENTS


def estimate_tokens(text):
    """Tokenizer-free estimate: ~4 chars per token, plus per-line overhead."""
    return len(text or "") // 4 + 8


def plan_chunks(segments, max_chunk_tokens, context=CONTEXT_SEGMENTS):
    """Tile the episode into non-overlapping labelling windows [a, b).

    Windows do NOT overlap, so every segment gets exactly one authoritative vote
    and there are no contradictory labels to reconcile. An ad straddling a seam is
    still visible inside the neighbour's read-only context, so it can be extended
    up to the seam from both sides and merged afterwards.

    Invariant: window size W >= 3*context (so the window always dominates the
    context it carries), unless the whole episode is shorter than that.
    """
    n = len(segments)
    if n == 0:
        return []
    min_w = max(1, 3 * context)
    costs = [estimate_tokens(s.get("text") or "") for s in segments]
    # Reserve budget for the two context blocks and the prompt scaffolding.
    ctx_reserve = 2 * context * (sum(costs) // max(1, n) + 1)
    budget = max(min_w * 8, max_chunk_tokens - ctx_reserve)

    chunks = []
    a = 0
    while a < n:
        used = 0
        b = a
        while b < n:
            if b - a >= min_w and used + costs[b] > budget:
                break
            used += costs[b]
            b += 1
        if b <= a:
            b = min(n, a + min_w)
        # Don't leave a runt tail smaller than the context width.
        if 0 < n - b < context:
            b = n
        chunks.append({"start": a, "end": b, "est_tokens": used})
        a = b
    return chunks


# --------------------------------------------------------------------------
# Validation ladder
# --------------------------------------------------------------------------
