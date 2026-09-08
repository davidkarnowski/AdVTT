"""Environment and key loading.

Keys come from the process environment first, then from the first `.env` found
in: `$ADVTT_ENV`, `./.env`, `~/.config/advtt/.env`. Values already set in the
environment are never overwritten. No key ever lands in an output artefact.
"""

import os

ENV_CANDIDATES = (
    os.environ.get("ADVTT_ENV", ""),
    os.path.join(os.getcwd(), ".env"),
    os.path.join(os.path.expanduser("~"), ".config", "advtt", ".env"),
)

_loaded = []


def load_env(paths=ENV_CANDIDATES):
    """Load KEY=VALUE lines from the first readable .env in `paths`."""
    for path in paths:
        if not path or not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        except OSError:
            continue
        _loaded.append(path)
        return path
    return None


def loaded_env_files():
    return list(_loaded)


def offline_mode():
    return os.environ.get("ADVTT_OFFLINE", "").strip().lower() in ("1", "true", "yes")
