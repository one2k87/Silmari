"""Gemini TTS helper with per-chunk caching (Interactions API, checked 2026-11-19)."""
import base64
import hashlib
import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
MODEL = os.environ.get("TTS_MODEL", "gemini-3.8-flash-tts")
CACHE = Path(os.environ.get("TTS_CACHE", ".tts_cache"))


def _keys():
    keys = [(n, os.environ.get(n)) for n in ("LLM_API_KEY", "LLM_API_KEY_PAID")]
    keys = [(n, k) for n, k in keys if k]
    if not keys:
        raise RuntimeError("LLM_API_KEY or LLM_API_KEY_PAID required")
    return keys


def _call(key, text, voice, style):
    body = {
        "model": MODEL,
        "input": [{"type": "user_input", "content": [{
            "type": "text", "text": text,
            "annotations": [{"type": "speech_metadata", "style": style}],
        }]}],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": voice}]},
    }
    req = urllib.request.Request(
        API_URL, data=json.dumps(body).encode(),
        headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as res:
        data = json.load(res)
    audio = [c for s in data.get("steps", []) if s.get("type") == "model_output"
             for c in s.get("content", []) if c.get("type") == "audio"]
    if not audio:
        raise RuntimeError(f"no audio in response, keys={list(data)}")
    return base64.b64decode(audio[-1]["data"]), data.get("usage")


def synth(text, voice, style):
    """Return (wav_path, cached, key_name). One chunk = one cache file."""
    CACHE.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(f"{MODEL}|{voice}|{style}|{text}".encode()).hexdigest()[:20]
    path = CACHE / f"{digest}.wav"
    if path.exists():
        return path, True, "cache"
    last = None
    for name, key in _keys():
        try:
            wav, usage = _call(key, text, voice, style)
        except urllib.error.HTTPError as err:
            last = f"{name}: HTTP {err.code} {err.read()[:300].decode(errors='replace')}"
            print(json.dumps({"event": "tts.failed", "key": name, "status": err.code}))
            continue
        path.write_bytes(wav)
        print(json.dumps({"event": "tts.completed", "key": name, "voice": voice,
                          "chars": len(text), "usage": usage}, ensure_ascii=False))
        return path, False, name
    raise RuntimeError(f"all keys failed: {last}")


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def concat(wavs, out_mp3, gap=0.45):
    """Join wavs with short silences, normalize loudness, write mp3."""
    args, parts = ["ffmpeg", "-y", "-loglevel", "error"], []
    for i, wav in enumerate(wavs):
        args += ["-i", str(wav)]
        parts.append(f"[{i}:a]apad=pad_dur={gap}[a{i}]")
    joined = "".join(f"[a{i}]" for i in range(len(wavs)))
    graph = ";".join(parts) + f";{joined}concat=n={len(wavs)}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11[out]"
    args += ["-filter_complex", graph, "-map", "[out]", "-ar", "44100", "-b:a", "128k", str(out_mp3)]
    subprocess.run(args, check=True)


def send_telegram(path, caption):
    token, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        raise RuntimeError("TELEGRAM_TOKEN and TELEGRAM_CHAT_ID required")
    subprocess.run(
        ["curl", "-sS", "--fail", f"https://api.telegram.org/bot{token}/sendAudio",
         "--form-string", f"chat_id={chat}", "--form-string", f"caption={caption}",
         "--form-string", f"title={caption[:60]}", "-F", f"audio=@{path}", "-o", "/dev/null"],
        check=True)
