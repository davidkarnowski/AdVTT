"""Content hashing and atomic JSON writes. Caches key on a hash of the segments,
never on file bytes or mtimes.
"""
# Moved verbatim from PodcastFetch adclass.py (commit 74692de, 2026-09-06),
# lines 2553-2565, 2599-2625. Do not edit the moved bodies without bumping PROMPT_VERSION
# where the prompt or ladder behaviour changes; see Research/01 and 12.
import hashlib
import json
import os
import tempfile


def source_sha256(segments):
    """Hash the STT *content*, not the file bytes and not mtime.

    Rewriting an identical _stt.json must not invalidate the cache, but a
    different STT model (different segmentation or text) must.
    """
    payload = json.dumps(
        [[round(float(s.get("start") or 0.0), 2), round(float(s.get("end") or 0.0), 2), s.get("text") or ""]
         for s in segments],
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_atomic(path, obj):
    """temp + os.replace. Nothing in this codebase ever deletes content."""
    d = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".adclass-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        # mkstemp gives 0600; the other sidecars are 0644 and server.py serves them.
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
