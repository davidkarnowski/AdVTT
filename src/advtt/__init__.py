"""advtt — time-resolved advertising disclosure for finished media.

Public surface (Research/01 §5):

    from advtt import classify_segments, providers, stt
    from advtt.captions import read_captions
    from advtt.record import build_record
    from advtt.evaluate import evaluate, self_test

Constants: AD_THRESHOLD, UNCERTAIN_THRESHOLD, MAX_AD_FRACTION, STATUS_*,
SCHEMA_VERSION, PROMPT_VERSION.
"""

from .config import load_env as _load_env

_load_env()

from .classify import TaskExtension, classify_segments, effective_prompt_version  # noqa: E402
from .validate import (  # noqa: E402
    AD_KINDS, AD_THRESHOLD, CONTEXT_SEGMENTS, LADDER_VERSION, MAX_AD_FRACTION, MAX_SPAN_SECONDS,
    PROMPT_VERSION, SCHEMA_VERSION, STATUS_FAILED, STATUS_NO_TRANSCRIPT, STATUS_OK,
    STATUS_REJECTED_DEGENERATE, STATUS_REJECTED_OVERLABEL, UNCERTAIN_THRESHOLD,
)

__version__ = "0.1.0.dev0"

__all__ = [
    "classify_segments", "TaskExtension", "effective_prompt_version",
    "AD_KINDS", "AD_THRESHOLD", "UNCERTAIN_THRESHOLD", "CONTEXT_SEGMENTS",
    "MAX_AD_FRACTION", "MAX_SPAN_SECONDS", "PROMPT_VERSION", "LADDER_VERSION", "SCHEMA_VERSION",
    "STATUS_OK", "STATUS_REJECTED_OVERLABEL", "STATUS_REJECTED_DEGENERATE",
    "STATUS_FAILED", "STATUS_NO_TRANSCRIPT", "__version__",
]
