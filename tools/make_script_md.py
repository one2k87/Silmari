"""Readable script (markdown) from script.json."""
import json
import re
import sys
from pathlib import Path

ACTS = {0: "여는 말", 1: "1막 — 먼저, 나에게 달라지는 것", 2: "2막 — 여기까지 온 과정", 3: "3막 — 같은 일, 다른 시각", 4: "4막 — 무엇을 보면 되나"}
ep_dir = Path(sys.argv[1])
d = json.loads((ep_dir / "script.json").read_text(encoding="utf-8"))
out = [f"# {d['title']}", "",
       f"> 기준일 {d['as_of']} · 해설자 N / 제2화자 T · 대괄호는 근거 번호(검수표 참조)", ""]
cur = None
for s in d["sections"]:
    if s["act"] != cur:
        cur = s["act"]
        out += [f"## {ACTS[cur]}", ""]
    tag = f" · 용어: {s['term']}" if s.get("term") else (" · 선택 구간" if s.get("optional") else "")
    out.append(f"**{s['id']}**{tag} _(연출: {s['style']})_")
    for l in s["lines"]:
        t = re.sub(r"<(short|long) pause>", "(쉼)", l["text"])
        out.append(f"- {l['sp']}: {t}" + (f" [{', '.join(l['src'])}]" if l["src"] else ""))
    out.append("")
(ep_dir / "script.md").write_text("\n".join(out), encoding="utf-8")
