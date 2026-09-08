#!/usr/bin/env python3
"""
STT provider seam (moved from PodcastFetch stt.py, commit 74692de, 2026-09-06).
Originally adapted from RF HotScan & SpeakNoEvil projects.
Supports local (Parakeet-MLX, Whisper-MLX, Voxtral) and cloud (OpenAI, Gladia)
speech-to-text models. Generates time-aligned segments for precise
audio-synchronous rolling transcripts.

Cloud provider seam
-------------------
A provider's transcribe() returns a dict the pipeline consumes as-is:
  text          full transcript string
  segments      [{start, end, text, words?: [{word, start, end}]}]
  timing        'model' (real timestamps) or 'proportional' (fiction; never diarized)
  has_words     bool, word-level timings present
  diarization?  {"turns": [{start, end, speaker:int}], "provider", "model"}
                — only from providers with provides_diarization = True; the
                fetcher writes these turns as the _diar.json and skips the
                local GPU pass. Deepgram/AssemblyAI adapters need only map
                their responses onto this shape.
"""

import json
import os
import sys
import time
import re
import wave

from .config import load_env

load_env()

PARAKEET_MODEL = "mlx-community/parakeet-tdt-0.6b-v2"
DEFAULT_WHISPER_MLX = "mlx-community/whisper-small-mlx"
DEFAULT_VOXTRAL = "mzbac/voxtral-mini-3b-4bit-mixed"
OPENAI_MODEL = "whisper-1"
GLADIA_MODEL = "solaria-1"
TARGET_SR = 16000

_JUNK = {"", "you", "thank you", "thank you.", "thanks for watching", "thanks for watching.", ".", "bye", "bye."}
_np = None

def _lazy_np():
    global _np
    if _np is None:
        import numpy as np
        _np = np
    return _np

def is_junk(text):
    return text.strip().lower() in _JUNK

def _ffmpeg_decode_mono16k(path):
    """Decode anything ffmpeg understands -> float32 mono at TARGET_SR.

    Returns None when ffmpeg is not on PATH, so the caller falls through to the
    next backend. Raises when ffmpeg is present but the file is genuinely bad.
    """
    import shutil
    import subprocess
    exe = shutil.which("ffmpeg")
    if not exe:
        return None
    proc = subprocess.run(
        [exe, "-v", "error", "-nostdin", "-i", path,
         "-f", "f32le", "-acodec", "pcm_f32le", "-ac", "1", "-ar", str(TARGET_SR), "-"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0 or not proc.stdout:
        raise RuntimeError("ffmpeg could not decode %s: %s"
                           % (path, (proc.stderr or b"").decode("utf-8", "replace")[:200]))
    np = _lazy_np()
    # frombuffer is a read-only view over the pipe's bytes; copy so callers that
    # normalise or slice in place (diarization, VAD) are not handed a locked array.
    return np.frombuffer(proc.stdout, dtype=np.float32).copy()


def read_audio_mono16k(path):
    """Read MP3 / M4A / WAV audio file -> float32 mono array at 16 kHz.

    Three backends, in cost order: soundfile (in-process, no subprocess), then
    ffmpeg, then librosa. ffmpeg sits in the middle deliberately -- libsndfile
    rejects plenty of real podcast MP3s (observed 2026-09-01 on a PDB episode
    with a large ID3v2 tag), librosa is an optional dependency that is usually
    absent, and ffmpeg is already required by the Whisper engines, so it is the
    backend most likely to be installed and least likely to refuse the file.
    Without it this helper raised ModuleNotFoundError and took diarization and
    any audio-input path down with it.
    """
    np = _lazy_np()
    try:
        import soundfile as sf
        data, sr = sf.read(path, dtype='float32')
        if data.ndim > 1:
            data = data.mean(axis=1)
        if sr != TARGET_SR:
            from math import gcd
            from scipy.signal import resample_poly
            g = gcd(int(sr), TARGET_SR)
            data = resample_poly(data, TARGET_SR // g, int(sr) // g)
        return data.astype(np.float32)
    except Exception:
        pass

    decoded = _ffmpeg_decode_mono16k(path)
    if decoded is not None:
        return decoded

    import librosa
    data, _ = librosa.load(path, sr=TARGET_SR, mono=True)
    return data.astype(np.float32)

def get_audio_duration_seconds(path):
    """Get exact audio duration in seconds; 0.0 only if every backend fails.

    The 0.0 is not cosmetic: it feeds progress estimates and, worse,
    build_proportional_segments(), where a zero duration turns every timestamp
    into nonsense. ffprobe is tried before giving up for the same reason ffmpeg
    is in read_audio_mono16k -- it reads files libsndfile will not.
    """
    try:
        import soundfile as sf
        return sf.info(path).duration
    except Exception:
        pass

    try:
        import shutil
        import subprocess
        exe = shutil.which("ffprobe")
        if exe:
            out = subprocess.run(
                [exe, "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=nw=1:nk=1", path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            if out.returncode == 0:
                return float((out.stdout or b"").decode("utf-8", "replace").strip())
    except Exception:
        pass

    try:
        import librosa
        return librosa.get_duration(path=path)
    except Exception:
        return 0.0

def build_proportional_segments(full_text, duration_sec):
    """Split transcript text into sentences and compute time-proportional start/end timestamps."""
    if not full_text or duration_sec <= 0:
        return []

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', full_text) if s.strip()]
    if not sentences:
        sentences = [full_text.strip()]

    total_chars = sum(len(s) for s in sentences)
    if total_chars == 0:
        return []

    segments = []
    curr_time = 0.0
    for s in sentences:
        ratio = len(s) / total_chars
        seg_dur = ratio * duration_sec
        start_time = curr_time
        end_time = curr_time + seg_dur
        segments.append({
            'start': round(start_time, 2),
            'end': round(end_time, 2),
            'text': s
        })
        curr_time = end_time

    return segments

class SttProvider:
    name = "base"
    wants_audio = True
    cloud = False
    provides_diarization = False   # True: transcribe() may return {"diarization": ...}

    def available(self):
        return False

    def ensure_ready(self):
        return False, "not implemented"

    def warm_up(self):
        pass

    def transcribe(self, audio, sample_rate=TARGET_SR, wav_path=None):
        raise NotImplementedError

class MLXWhisperProvider(SttProvider):
    """OpenAI Whisper running locally on Apple Silicon (mlx-whisper).
    Generates rich segment-level timestamps locally without cloud dependencies."""

    name = "whisper-mlx"
    wants_audio = True

    def __init__(self, model_id=DEFAULT_WHISPER_MLX, word_timestamps=False):
        self.model_id = model_id
        self.word_timestamps = bool(word_timestamps)
        self._warmed = False

    def available(self):
        import importlib.util
        return importlib.util.find_spec("mlx_whisper") is not None

    def ensure_ready(self):
        import importlib.util
        if importlib.util.find_spec("mlx_whisper") is None:
            return False, "mlx_whisper package not installed"
        return True, "ok"

    def warm_up(self):
        if self._warmed:
            return
        np = _lazy_np()
        import mlx_whisper
        try:
            mlx_whisper.transcribe(np.zeros(TARGET_SR, dtype=np.float32), path_or_hf_repo=self.model_id)
        except Exception:
            pass
        self._warmed = True

    def transcribe(self, audio=None, sample_rate=TARGET_SR, wav_path=None):
        np = _lazy_np()
        import mlx_whisper
        if audio is None and wav_path:
            audio = read_audio_mono16k(wav_path)
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        kwargs = {"path_or_hf_repo": self.model_id}
        if self.word_timestamps:
            # Adds a DTW alignment pass, so it is opt-in: slower and a much larger
            # sidecar, in exchange for being able to place a boundary inside an
            # utterance instead of surrendering the whole segment.
            kwargs["word_timestamps"] = True
        res = mlx_whisper.transcribe(audio, **kwargs)
        text = res.get("text", "") if isinstance(res, dict) else str(res)

        segments = []
        if isinstance(res, dict) and "segments" in res:
            for seg in res["segments"]:
                seg_text = seg.get("text", "").strip()
                if seg_text and not is_junk(seg_text):
                    entry = {
                        'start': round(seg.get('start', 0.0), 2),
                        'end': round(seg.get('end', 0.0), 2),
                        'text': seg_text
                    }
                    if self.word_timestamps and seg.get('words'):
                        entry['words'] = [
                            {'w': (w.get('word') or '').strip(),
                             's': round(float(w.get('start', 0.0)), 2),
                             'e': round(float(w.get('end', 0.0)), 2)}
                            for w in seg['words'] if (w.get('word') or '').strip()
                        ]
                    segments.append(entry)

        timing = 'model'
        if not segments and text and wav_path:
            total_dur = get_audio_duration_seconds(wav_path)
            segments = build_proportional_segments(text, total_dur)
            timing = 'proportional'   # character-proportional estimates, not real
                                      # timestamps -- downstream alignment (ad
                                      # edges, diarization) must not trust them

        return {
            'text': text.strip(),
            'segments': segments,
            'has_words': bool(self.word_timestamps) and timing == 'model',
            'timing': timing,
        }

class ParakeetMLXProvider(SttProvider):
    """Parakeet-TDT via MLX (Apple Silicon) with 30-second timestamped segment chunking."""
    name = "parakeet-mlx"

    def __init__(self, model_id=PARAKEET_MODEL):
        self.model_id = model_id
        self._model = None
        self._warmed = False

    def available(self):
        import importlib.util
        if importlib.util.find_spec("parakeet_mlx") is None:
            return False
        ok, _ = self.ensure_ready()
        return ok

    def ensure_ready(self):
        try:
            from huggingface_hub import scan_cache_dir
            repos = {r.repo_id for r in scan_cache_dir().repos}
            if self.model_id in repos:
                return True, "ok"
            return False, f"model '{self.model_id}' not in HuggingFace cache"
        except Exception as e:
            return False, f"hf cache scan failed: {e}"

    def _load(self):
        if self._model is None:
            from parakeet_mlx import from_pretrained
            self._model = from_pretrained(self.model_id)
        return self._model

    def warm_up(self):
        if self._warmed:
            return
        np = _lazy_np()
        import mlx.core as mx
        from parakeet_mlx.audio import get_logmel
        model = self._load()
        mel = get_logmel(mx.array(np.zeros(TARGET_SR, dtype=np.float32)), model.preprocessor_config)
        res = model.generate(mel)
        self._warmed = True

    def transcribe(self, audio=None, sample_rate=TARGET_SR, wav_path=None):
        np = _lazy_np()
        import mlx.core as mx
        from parakeet_mlx.audio import get_logmel
        model = self._load()
        if audio is None and wav_path:
            audio = read_audio_mono16k(wav_path)
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # 30-second chunking for precise timestamp alignment and Metal memory bounds
        CHUNK_SEC = 30
        chunk_len = CHUNK_SEC * TARGET_SR
        
        segments = []
        texts = []
        
        for i in range(0, len(audio), chunk_len):
            chunk = audio[i:i + chunk_len]
            start_sec = (i / TARGET_SR)
            end_sec = min((i + chunk_len) / TARGET_SR, len(audio) / TARGET_SR)
            
            mel = get_logmel(mx.array(chunk), model.preprocessor_config)
            res = model.generate(mel)
            if isinstance(res, list) and res and res[0].text:
                txt = res[0].text.strip()
                if txt and not is_junk(txt):
                    texts.append(txt)
                    segments.append({
                        'start': round(start_sec, 2),
                        'end': round(end_sec, 2),
                        'text': txt
                    })

        full_text = " ".join(texts)
        return {
            'text': full_text,
            'segments': segments,
            'timing': 'model',    # chunk-granular but real audio positions
        }

class OpenAIProvider(SttProvider):
    """Cloud STT via OpenAI's Audio API with segment timestamps."""
    name = "openai"
    wants_audio = False
    cloud = True

    def __init__(self, model=OPENAI_MODEL):
        self.model = model
        self.model_id = model
        self._client = None

    def available(self):
        import importlib.util
        import os
        return (importlib.util.find_spec("openai") is not None and bool(os.environ.get("OPENAI_API_KEY")))

    def ensure_ready(self):
        import importlib.util
        import os
        if importlib.util.find_spec("openai") is None:
            return False, "openai package not installed (pip install openai)"
        if not os.environ.get("OPENAI_API_KEY"):
            return False, "OPENAI_API_KEY not set in environment"
        return True, "ok"

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI()
        return self._client

    def warm_up(self):
        self._get_client()

    def transcribe(self, audio=None, sample_rate=TARGET_SR, wav_path=None):
        if not wav_path:
            raise ValueError("OpenAIProvider needs a wav_path to upload")
        
        # OpenAI API has a 25 MB file upload limit
        file_size = os.path.getsize(wav_path) if os.path.exists(wav_path) else 0
        if file_size > 25 * 1024 * 1024:
            print(f"  [OpenAI] Audio file exceeds 25 MB limit ({file_size / (1024*1024):.1f} MB). Routing to local Parakeet-MLX...")
            local_prov = ParakeetMLXProvider()
            if local_prov.available():
                return local_prov.transcribe(wav_path=wav_path)

        client = self._get_client()
        fmt = "verbose_json" if "whisper" in self.model else "json"
        
        try:
            with open(wav_path, "rb") as f:
                resp = client.audio.transcriptions.create(
                    model=self.model, file=f, response_format=fmt
                )
        except Exception as e:
            if "413" in str(e) or "content size limit" in str(e).lower():
                print(f"  [OpenAI] Upload size limit reached. Falling back to local Parakeet-MLX...")
                local_prov = ParakeetMLXProvider()
                if local_prov.available():
                    return local_prov.transcribe(wav_path=wav_path)
            raise e
        
        text = getattr(resp, "text", str(resp))
        segments = []
        if hasattr(resp, "segments") and resp.segments:
            for seg in resp.segments:
                seg_text = getattr(seg, 'text', '').strip()
                if seg_text and not is_junk(seg_text):
                    segments.append({
                        'start': round(getattr(seg, 'start', 0.0), 2),
                        'end': round(getattr(seg, 'end', 0.0), 2),
                        'text': seg_text
                    })

        # Fallback to character-proportional segment timestamps if API returns plain text
        timing = 'model'
        if not segments and text:
            total_duration = get_audio_duration_seconds(wav_path)
            segments = build_proportional_segments(text, total_duration)
            timing = 'proportional'

        return {
            'text': (text or "").strip(),
            'segments': segments,
            'timing': timing,
        }

class GladiaProvider(SttProvider):
    """Cloud STT via Gladia's async pre-recorded API (upload -> init -> poll).

    Returns the normalized cloud-provider shape (see module docstring note on
    the provider seam): text, segments with word-level timings, and — because
    Gladia diarizes server-side — a `diarization` key carrying speaker turns
    in the same {start, end, speaker:int} form the local pyannote layer emits.
    The fetcher uses that to skip the local GPU diarization pass entirely.

    Any future cloud engine (Deepgram, AssemblyAI, ...) only needs to map its
    response to this same return shape to inherit the whole pipeline,
    including cloud diarization adoption.
    """
    name = "gladia"
    wants_audio = False
    cloud = True
    provides_diarization = True

    BASE = "https://api.gladia.io/v2"
    POLL_INTERVAL = 5.0
    POLL_TIMEOUT = 1800.0
    # Standard-plan ceilings: 135 min per request. Chunk at 120 to keep margin,
    # using the fewest equal chunks that fit. Uploads are transcoded to 16 kHz
    # mono first when ffmpeg is present — a 320 kbps stereo mp3 is ~10x more
    # bytes than STT needs, and oversized single-shot uploads get the
    # connection dropped mid-stream.
    MAX_CHUNK_SEC = 120 * 60.0
    TRANSCODE_OVER_BYTES = 80 * 1024 * 1024

    def __init__(self, model=None):
        self.model = model or GLADIA_MODEL
        self.model_id = self.model

    @staticmethod
    def _key():
        return os.environ.get("GLADIA_API_KEY", "").strip()

    def available(self):
        return bool(self._key())

    def ensure_ready(self):
        if not self._key():
            return False, "GLADIA_API_KEY not set (.env or environment)"
        return True, "GLADIA_API_KEY present (model %s)" % self.model

    def _request(self, url, data=None, headers=None, timeout=60):
        import urllib.request
        import urllib.error
        hdrs = {"x-gladia-key": self._key()}
        hdrs.update(headers or {})
        req = urllib.request.Request(url, data=data, headers=hdrs)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")[:400]
            except Exception:
                pass
            raise RuntimeError("gladia HTTP %s on %s: %s" % (e.code, url, body))

    def _upload(self, path):
        boundary = "----podcastfetch%d" % int(time.time() * 1000)
        fname = os.path.basename(path)
        with open(path, "rb") as fh:
            payload = fh.read()
        body = b"".join([
            ("--%s\r\n" % boundary).encode(),
            ('Content-Disposition: form-data; name="audio"; filename="%s"\r\n'
             % fname).encode(),
            b"Content-Type: application/octet-stream\r\n\r\n",
            payload,
            ("\r\n--%s--\r\n" % boundary).encode(),
        ])
        _code, parsed = self._request(
            self.BASE + "/upload", data=body,
            headers={"Content-Type": "multipart/form-data; boundary=%s" % boundary},
            timeout=600)
        url = (parsed or {}).get("audio_url")
        if not url:
            raise RuntimeError("gladia upload returned no audio_url")
        return url

    @staticmethod
    def _ffmpeg():
        for cand in ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
            if os.path.exists(cand):
                return cand
        import shutil as _sh
        return _sh.which("ffmpeg")

    def _prep_chunks(self, wav_path):
        """Yield (tmp_or_source_path, offset_sec) upload units.

        One unit for anything under the duration cap; equal-length chunks
        otherwise. When ffmpeg is available, units are 16 kHz mono 64k mp3 —
        both far smaller on the wire and how chunk boundaries are cut. Without
        ffmpeg, oversized/overlong audio is uploaded as-is and left to fail
        loudly rather than silently truncated.
        """
        import math
        import tempfile
        dur = get_audio_duration_seconds(wav_path) or 0.0
        size = os.path.getsize(wav_path)
        ffmpeg = self._ffmpeg()
        needs_chunks = dur > self.MAX_CHUNK_SEC
        needs_transcode = size > self.TRANSCODE_OVER_BYTES
        if not ffmpeg:
            if needs_chunks or needs_transcode:
                print(f"  [Gladia] WARNING: {dur/60:.0f} min / {size>>20} MB "
                      f"exceeds request limits and ffmpeg is unavailable to "
                      f"chunk/transcode; uploading raw.")
            yield wav_path, 0.0, None
            return
        n = max(1, math.ceil(dur / self.MAX_CHUNK_SEC)) if needs_chunks else 1
        if n == 1 and not needs_transcode:
            yield wav_path, 0.0, None
            return
        chunk_len = dur / n if n > 1 else dur
        for i in range(n):
            off = i * chunk_len
            tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            tmp.close()
            import subprocess as sp
            cmd = [ffmpeg, "-y", "-loglevel", "error", "-ss", "%.3f" % off]
            if n > 1:
                cmd += ["-t", "%.3f" % chunk_len]
            cmd += ["-i", wav_path, "-ac", "1", "-ar", "16000",
                    "-b:a", "64k", tmp.name]
            sp.run(cmd, check=True)
            yield tmp.name, off, tmp.name   # third item: path to delete after

    def _transcribe_one(self, path):
        """Upload one file, start a job, poll to completion; return result doc."""
        audio_url = self._upload(path)
        _code, job = self._request(
            self.BASE + "/pre-recorded",
            data=json.dumps({
                "audio_url": audio_url,
                "model": self.model,
                "diarization": True,
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"})
        result_url = (job or {}).get("result_url") or (
            self.BASE + "/pre-recorded/" + str((job or {}).get("id", "")))
        deadline = time.time() + self.POLL_TIMEOUT
        while True:
            _code, doc = self._request(result_url, timeout=30)
            status = (doc or {}).get("status")
            if status == "done":
                return doc
            if status == "error":
                raise RuntimeError("gladia job failed: %s"
                                   % str((doc or {}).get("error_code"))[:200])
            if time.time() > deadline:
                raise RuntimeError("gladia job timed out after %.0fs" % self.POLL_TIMEOUT)
            time.sleep(self.POLL_INTERVAL)

    def transcribe(self, audio=None, sample_rate=TARGET_SR, wav_path=None):
        if not wav_path:
            raise ValueError("GladiaProvider needs a wav_path to upload")
        texts, segments, turns = [], [], []
        has_words = False
        spk_base = 0        # renumber speakers per chunk so labels never collide
        n_chunks = 0
        for path, offset, cleanup in self._prep_chunks(wav_path):
            n_chunks += 1
            try:
                doc = self._transcribe_one(path)
            finally:
                if cleanup:
                    try:
                        os.unlink(cleanup)
                    except OSError:
                        pass
            tx = ((doc.get("result") or {}).get("transcription")) or {}
            texts.append((tx.get("full_transcript") or "").strip())
            chunk_speakers = set()
            for utt in tx.get("utterances") or []:
                text = (utt.get("text") or "").strip()
                if not text or is_junk(text):
                    continue
                words = [{"word": w.get("word"),
                          "start": round((w.get("start") or 0.0) + offset, 3),
                          "end": round((w.get("end") or 0.0) + offset, 3)}
                         for w in (utt.get("words") or []) if w.get("word")]
                has_words = has_words or bool(words)
                seg = {"start": round((utt.get("start") or 0.0) + offset, 2),
                       "end": round((utt.get("end") or 0.0) + offset, 2),
                       "text": text}
                if words:
                    seg["words"] = words
                segments.append(seg)
                spk = utt.get("speaker")
                if isinstance(spk, int):
                    chunk_speakers.add(spk)
                    tag = spk_base + spk
                    # Merge back-to-back same-speaker utterances into one turn,
                    # mirroring the local layer's turn granularity.
                    if turns and turns[-1]["speaker"] == tag \
                            and seg["start"] - turns[-1]["end"] <= 1.0:
                        turns[-1]["end"] = seg["end"]
                    else:
                        turns.append({"start": seg["start"], "end": seg["end"],
                                      "speaker": tag})
            spk_base += (max(chunk_speakers) + 1) if chunk_speakers else 0

        out = {
            "text": " ".join(t for t in texts if t),
            "segments": segments,
            "timing": "model",
            "has_words": has_words,
        }
        if turns:
            out["diarization"] = {"turns": turns, "provider": self.name,
                                  "model": self.model}
            if n_chunks > 1:
                # Speaker identity does not carry across chunk seams: the same
                # voice gets a fresh label in each chunk. Downstream name
                # attribution (adclass) resolves identity from context anyway.
                out["diarization"]["chunked"] = n_chunks
        return out


_PROVIDERS = {
    "whisper-mlx": lambda model=None, word_timestamps=False: MLXWhisperProvider(
        model or DEFAULT_WHISPER_MLX, word_timestamps=word_timestamps),
    "parakeet-mlx": lambda model=None: ParakeetMLXProvider(model or PARAKEET_MODEL),
    "openai": lambda model=None: OpenAIProvider(model or OPENAI_MODEL),
    "gladia": lambda model=None: GladiaProvider(model or GLADIA_MODEL),
}
_AUTO_ORDER = ["whisper-mlx", "parakeet-mlx", "gladia", "openai"]

def make_provider(prefer="auto", model=None, word_timestamps=False):
    """Return an STT provider instance by name or best available.

    `word_timestamps` is offered to every factory but only honoured by engines
    that support it; the others ignore the keyword, so callers do not have to
    know which is which.
    """
    def _build(name, factory):
        try:
            return factory(model, word_timestamps=word_timestamps)
        except TypeError:
            return factory(model)

    if prefer and prefer != "auto":
        factory = _PROVIDERS.get(prefer)
        if factory is None:
            return None
        p = _build(prefer, factory)
        return p if p.available() else None
    for name in _AUTO_ORDER:
        p = _build(name, _PROVIDERS[name])
        if p.available():
            return p
    return None

def available_providers():
    return [name for name in _AUTO_ORDER if _PROVIDERS[name]().available()]
