"""Review sheet: every sentence with a number, date or named body next to its source."""
import json
import re
import sys
from pathlib import Path

ep_dir = Path(sys.argv[1])
ep = json.loads((ep_dir / "script.json").read_text(encoding="utf-8"))
src = ep["sources"]
clean = lambda t: re.sub(r"<[^>]+>\s*", "", t)
lines = [(s, l) for s in ep["sections"] for l in s["lines"]]
facts = [(s, l) for s, l in lines if l["src"]]


def bucket(keys):
    kinds = {src[k]["kind"] for k in keys}
    if kinds == {"public"}:
        return "공공"
    if "public" in kinds:
        return "공공+언론"
    return "일반 지식" if kinds == {"general"} else "언론"


count = {}
for _, l in facts:
    count[bucket(l["src"])] = count.get(bucket(l["src"]), 0) + 1
chars = sum(len(clean(l["text"])) for _, l in lines)
out = [f"# 검수표 — {ep['title']}", "",
       f"- 기준일: {ep['as_of']} · 글자 수 {chars:,}자 · 예상 길이 약 {chars / 330:.0f}분(실제 길이는 음성 합성 뒤 확정)",
       f"- 근거가 붙은 문장 {len(facts)}개: " + " · ".join(f"{k} {v}개({v / len(facts):.0%})" for k, v in count.items()),
       "", "## 숫자·날짜가 들어간 문장", "", "| 구간 | 문장 | 근거 |", "|---|---|---|"]
for s, l in facts:
    if re.search(r"\d|다섯|여덟|네 명|사흘|한 시간", l["text"]):
        out.append(f"| {s['id']} | {clean(l['text'])} | {', '.join(l['src'])} |")
out += ["", "## 언론 보도에만 기대는 문장", "", "| 구간 | 문장 | 근거 |", "|---|---|---|"]
for s, l in facts:
    if bucket(l["src"]) in ("언론", "일반 지식"):
        out.append(f"| {s['id']}{' (선택)' if s.get('optional') else ''} | {clean(l['text'])} | {', '.join(l['src'])} |")
out += ["", "## 출처", ""]
out += [f"- **{k}** [{v['kind']}] {v['name']}" + (f" — {v['url']}" if v["url"] else "") for k, v in src.items()]
(ep_dir / "factsheet.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(out[2]); print(out[3])
