# Weave 통합본 (Claude, 2026-11-11 2차)

인트로, 모션그래픽, 솔루션과 How it Works, 뒷부분, Appendix를 한 덱으로 합친 판이에요. 2차에서 인트로 대본과 6쪽, 9쪽, 14쪽을 손보고 10분 안으로 줄였어요.

| 파일 | 내용 |
| --- | --- |
| `Weave_통합본_Claude.pptx` | 통합 덱 87장(본 발표 41장, Appendix 16장, 제안 장표 5장, 이전 판 25장) |
| `Weave_통합본_Claude_미리보기.mp4` | 본 발표 41장을 처음부터 끝까지 말하며 넘긴 영상(낭독, 자막) |
| `제안장표_미리보기.mp4` | 제안 장표 네 장을 말하며 넘긴 영상 |
| `대본.md` | 장마다 말할 글과 영상에서 잰 시간, 1차에서 바꾼 곳, 더 줄일 곳, 이전 대본 |
| `한눈에.jpg` | 87장을 한 장에 모은 그림 |
| `assets/` | 6쪽의 앱 화면과 그 소스, 마무리 사진 세 장(CC0), 아웃트로 덱에서 가져온 그림. 출처는 `assets/CREDITS.md` |

## 덱 차례

| 쪽 | 묶음 | 어디서 왔나 |
| --- | --- | --- |
| 1 | 표지 | 우리 중간본의 표지(표지 영상 v8) |
| 2~5 | 인트로 | jjun-0824/t3 `Weave_결선_중간본_도입부수정.pptx` 2~5쪽. 화면과 효과는 그대로, 노트는 새 대본 |
| 6 | 수많은 기록 | 새로 그림(인트로 덱 6쪽 자리) |
| 7~8 | 설문 두 장 | 인트로 덱 7~8쪽. 7쪽 문구 한 줄과 고리 굵기를 바꿈 |
| 9 | 기록을 남기는 곳 | 새로 그림(설문 4번) |
| 10~13 | 인트로 | 인트로 덱 9~12쪽. 13쪽 문구 한 곳을 바꿈 |
| 14 | 잇는 장 | 새로 그림(인트로 덱 13쪽 자리) |
| 15 | 모션그래픽 | 우리 중간본의 영상 장(v23) |
| 16~32 | 솔루션 3장, How it Works 14장 | `../09_HowItWorks/장표5_claude` 그대로 |
| 33~35 | 기대효과 세 장 | WIWLEE/t3-2 `Weave_BI_아웃트로_통합_1110_v7.pptx` 1~3쪽의 내용을 같은 엔진으로 다시 그림 |
| 36 | 비즈니스 임팩트 | 같은 덱 4쪽 |
| 37 | 기존 기능과의 비교 | 새로 그림 |
| 38 | Why Now · Why Samsung 연표 | 같은 덱 5쪽의 연표 내용 그대로 |
| 39~41 | 마무리 세 장 | 같은 덱 6~8쪽의 문구를 사진 위에. 끝 로고는 41쪽 안에서 뜸 |
| 42~57 | Appendix | How it Works Appendix 15장, 사진 출처 1장 |
| 58~62 | 제안 장표 | 가름 장, 기대효과를 고리 그래프의 움직임으로 보여 주는 안 세 장, 두 줄 연표 |
| 63~87 | 이전 판 | 가름 장, 1차 통합본의 인트로 2~13쪽과 뒷부분 32~41쪽, 저장 채널 그림, 인트로 덱의 13쪽 |

## 다시 만들기

```
~/.cache/weave-tools/venv/bin/python tools/hook_assets.py   # 6쪽의 앱 화면과 벽 그림, 카메라 아이콘 (assets/src → assets/hook)
~/.cache/weave-tools/venv/bin/python make.py --png          # 덱 + out/png (PowerPoint로 렌더)
~/.cache/weave-tools/venv/bin/python talk.py                # 낭독 → 덱 → 녹화 → 낭독, 자막, 모션그래픽 소리를 얹은 영상
~/.cache/weave-tools/venv/bin/python talk.py --proposal
~/.cache/weave-tools/venv/bin/python trim.py                # 더 줄인 대본 안의 시간을 같은 목소리로 잼
~/.cache/weave-tools/venv/bin/python doc.py                 # 대본.md
~/.cache/weave-tools/venv/bin/python tools/overview.py      # 한눈에.jpg
```

- `원본/`에 세 덱을 둬야 해요(저장소에는 올리지 않아요).
  - https://github.com/jjun-0824/t3/blob/claude/pull-push-permissions-eacsir/weave/결선준비/02_PPT/Weave_결선_중간본_도입부수정.pptx
  - https://github.com/WIWLEE/t3-2/blob/main/Weave_BI_아웃트로_통합_1110_v7.pptx
  - `통합본_1차.pptx`: `git show ab7ab74:weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx > 원본/통합본_1차.pptx` (이전 판 묶음을 여기서 옮겨요)
- 바탕 덱은 `../02_PPT/Weave_결선_중간본.pptx`예요. 읽기만 하고, 표지와 모션그래픽 장, 장 틀을 빌려 써요.
- `slides_new.py`에 새로 그린 장과 말할 글이 있어요(인트로 노트는 `INTRO_NOTES`, 새 장은 `NOTES`). 그리는 엔진과 낭독 도구는 `../09_HowItWorks/장표5_claude` 것을 그대로 써요.
- `make.py`의 `patch_intro`가 옮겨 온 인트로 장의 노트, 화면 글 두 곳, 고리 굵기를 바꿔요. `foreign.py`는 다른 덱의 장을 도형, 그림, 전환, 효과째로 옮겨요.
- `hook_layout.py`는 6쪽 벽에서 어느 자리에 어느 앱 화면이 놓이는지 적은 표예요.
- 낭독은 이 컴퓨터 안에서만 만들어요(Supertonic 3, 목소리 F2F1_70, 속도 1.15).
