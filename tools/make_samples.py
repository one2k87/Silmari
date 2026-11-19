"""Voice samples: each voice x each style on the same ~1 minute excerpt."""
import json
import sys
from pathlib import Path

import tts

req = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
out = Path("out/samples")
out.mkdir(parents=True, exist_ok=True)
seconds, n = 0.0, 0
for voice in req["voices"]:
    for style in req["styles"]:
        n += 1
        wav, _, _ = tts.synth(req["text"], voice, style["prompt"])
        mp3 = out / f"sample{n}_{voice}_{style['id']}.mp3"
        tts.concat([wav], mp3, gap=0.0)
        seconds += tts.duration(mp3)
        tts.send_telegram(mp3, f"뉴스 실마리 목소리 견본 {n} — {voice} · {style['label']}")
print(json.dumps({"event": "samples.completed", "count": n, "audio_seconds": round(seconds, 1)}))
