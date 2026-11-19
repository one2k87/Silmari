"""Commute bundle: join several episodes (reusing their cached audio) with a short opening, bridges and a close."""
import json
import sys
from pathlib import Path

import build_episode
import tts

bundle_dir = Path(sys.argv[1])
b = json.loads((bundle_dir / "bundle.json").read_text(encoding="utf-8"))
say = lambda text: tts.synth(text, b["voice"], b["style"])[0]

wavs, cached, new_chars = [say(b["opening"])], 0, 0
for n, item in enumerate(b["episodes"]):
    ep = build_episode.load(Path("episodes") / item["id"])
    wavs.append(say(item["bridge"]))
    ep_wavs, hit, new = build_episode.chunk_wavs(ep, skip_optional=item.get("skip_optional", False), in_bundle=True)
    wavs += ep_wavs
    cached += hit
    new_chars += new
wavs.append(say(b["closing"]))

out = Path("out") / f"{b['id']}.mp3"
out.parent.mkdir(exist_ok=True)
tts.concat(wavs, out)
secs = tts.duration(out)
print(json.dumps({"event": "bundle.built", "id": b["id"], "episodes": len(b["episodes"]), "chunks": len(wavs),
                  "cached": cached, "new_chars": new_chars, "audio_seconds": round(secs, 1)}))
tts.send_telegram(out, f"[검수용 묶음] {b['title']} · {int(secs // 60)}분 {int(secs % 60)}초 · 승인 전 업로드 안 함")
