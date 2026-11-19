"""Build an episode: synthesize per speaker chunk (cached), join, send to Telegram for review."""
import json
import sys
from pathlib import Path

import tts

TERM_STYLE = "friendly explainer, clear and a little brighter"
ep_dir = Path(sys.argv[1])
ep = json.loads((ep_dir / "script.json").read_text(encoding="utf-8"))
skip_optional = "--skip-optional" in sys.argv

wavs, new_chars, cached = [], 0, 0
for sec in ep["sections"]:
    if sec.get("optional") and skip_optional:
        continue
    chunk, speaker = [], None
    for line in sec["lines"] + [{"sp": None, "text": ""}]:
        if line["sp"] != speaker and chunk:
            text = " ".join(chunk)
            style = TERM_STYLE if speaker == "T" else f"{ep['narrator_style']}; this part: {sec['style']}"
            wav, hit, _ = tts.synth(text, ep["voices"][speaker], style)
            wavs.append(wav)
            cached += hit
            new_chars += 0 if hit else len(text)
            chunk = []
        speaker = line["sp"]
        chunk.append(line["text"])

out = Path("out") / f"{ep['id']}.mp3"
out.parent.mkdir(exist_ok=True)
tts.concat(wavs, out)
secs = tts.duration(out)
print(json.dumps({"event": "episode.built", "id": ep["id"], "chunks": len(wavs), "cached": cached,
                  "new_chars": new_chars, "audio_seconds": round(secs, 1)}))
tts.send_telegram(out, f"[검수용] {ep['title']} · {int(secs // 60)}분 {int(secs % 60)}초 · 승인 전 업로드 안 함")
