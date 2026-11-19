# Silmari — 뉴스 실마리 (SolvUp 코드 R)

뉴스를 안 보던 사람을 위한 시사 오디오 채널 제작 레포.
규칙·상태는 `SolvUp_Workspace/_Master_Context/silmari_context.md`가 기준이다.

| 경로 | 내용 |
|---|---|
| `episodes/<id>/script.json` | 대본(구간·화자·연출·문장별 근거) |
| `episodes/<id>/factsheet.md` | 검수표 — `python3 tools/make_factsheet.py episodes/<id>` |
| `samples/request.json` | 목소리 견본 요청. 고쳐서 푸시하면 견본이 텔레그램으로 온다 |
| `tools/tts.py` | Gemini TTS 호출 + 구간 캐시 + 이어 붙이기 + 텔레그램 전송 |
| `.github/workflows/` | `voice-samples`, `episode-review-audio` |
| `audio/` | 만든 음성 보관(로컬 전용, git 제외) — `audio/samples/`, `audio/episodes/`. 워크플로 산출물을 실마리 세션이 내려받아 넣는다 |

검수용 음성 만들기: `episodes/<id>/build.request` 파일을 만들거나 고쳐서 푸시한다(내용에 `skip-optional`이 있으면 선택 구간 제외).
업로드는 하지 않는다. 키·토큰은 이 레포에 적지 않는다(금고 → GitHub Secrets).
