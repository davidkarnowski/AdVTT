"""Provider registry. `make_provider` NEVER falls back from a local provider to
a cloud one: that would ship transcripts off-box without the user asking. An
unavailable provider is returned as-is and the caller reports the reason.
"""

from ..config import offline_mode
from .base import ProviderError
from .claude_api import ClaudeProvider
from .claude_cli import ClaudeCLIProvider
from .gemini import GeminiProvider
from .ollama import OllamaProvider
from .omlx import OMLXProvider
from .openai import OpenAIProvider
from .replay import ReplayProvider

PROVIDERS = {
    "claude-cli": ClaudeCLIProvider,
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "ollama": OllamaProvider,
    "omlx": OMLXProvider,
    "replay": ReplayProvider,
}

DEFAULT_PROVIDER = "claude-cli"


def make_provider(prefer=DEFAULT_PROVIDER, model=None, endpoint=None):
    key = (prefer or DEFAULT_PROVIDER).strip().lower()
    if key not in PROVIDERS:
        raise ValueError("unknown provider %r (choose from %s)" % (prefer, ", ".join(sorted(PROVIDERS))))
    prov = PROVIDERS[key](model=model, endpoint=endpoint)
    if offline_mode() and getattr(prov, "cloud", False):
        raise ProviderError("--offline: provider %r would contact %s"
                            % (key, getattr(prov, "endpoint", None) or "a network host"))
    return prov


def available_providers():
    """Describe every adapter without raising."""
    out = []
    for key in PROVIDERS:
        try:
            out.append(PROVIDERS[key]().describe())
        except Exception as e:
            out.append({"name": key, "available": False, "detail": "constructor failed: %s" % e})
    return out
