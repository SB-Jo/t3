# Weave 통합본 (Claude, 2026-11-12 3차)

인트로, 모션그래픽, 솔루션과 How it Works, 뒷부분, Appendix를 한 덱으로 합친 판이에요. 3차에서 표지 영상, 인트로 2~14쪽, 솔루션과 How it Works의 대본 네 곳, 뒷부분 33~41쪽을 손봤어요. 바꾼 곳은 `대본.md`의 '2차에서 바꾼 곳'에 쪽마다 적었어요.

| 파일 | 내용 |
| --- | --- |
| `Weave_통합본_Claude.pptx` | 통합 덱 112장(본 발표 41장, Appendix 16장, 제안 장표 4장, 이전 판 2차 26장, 이전 판 1차 25장) |
| `Weave_통합본_Claude_미리보기.mp4` | 본 발표 41장을 처음부터 끝까지 말하며 넘긴 영상(낭독, 자막) |
| `제안장표_미리보기.mp4` | 제안 장표 세 장을 말하며 넘긴 영상 |
| `대본.md` | 장마다 말할 글과 영상에서 잰 시간, 2차에서 바꾼 곳, 더 줄일 곳, 이전 대본 |
| `한눈에.jpg` | 112장을 한 장에 모은 그림 |
| `assets/` | 6쪽의 앱 화면과 그 소스, 3~5쪽의 기록 조각, 13쪽의 흐린 배경, 마무리 사진 세 장(CC0), 아웃트로 덱에서 가져온 그림. 출처는 `assets/CREDITS.md` |

## 덱 차례

| 쪽 | 묶음 | 어디서 왔나 |
| --- | --- | --- |
| 1 | 표지 | 우리 중간본의 표지. 영상은 표지 영상 v9(`../10_표지영상`, 18초)로 바꾸고 제목을 48pt로 줄임 |
| 2~5 | 인트로 | jjun-0824/t3 `Weave_결선_중간본_도입부수정.pptx` 2~5쪽. 노트는 새 대본. 3~5쪽은 제목을 빼고 그 자리까지 옅은 기록 조각을 흩어 두었고, 첫 말풍선의 글, 말풍선 자리와 꼬리를 바꿈 |
| 6 | 수많은 기록 | 새로 그림(인트로 덱 6쪽 자리) |
| 7~8 | 설문 두 장 | 인트로 덱 7~8쪽. 7쪽 문구 한 줄, 고리 굵기, 각주를 바꿈 |
| 9 | 기록을 남기는 곳 | 새로 그림(설문 4번) |
| 10 | 세상의 모든 지식은 AI에게 | 인트로 덱 9쪽. AI 표시를 벡터 도형으로 바꿈 |
| 11~12 | 흩어진 기록이 이어짐 | 인트로 덱 10~11쪽의 차례를 뒤집어 새로 그림(11쪽 흩어져 있음 → 12쪽 반듯해지고 이어짐) |
| 13 | 내 휴대폰에게 물을 순 없을까요 | 인트로 덱 12쪽. 문구 한 곳과 흐린 배경을 바꿈 |
| 14 | 잇는 장 | 새로 그림(인트로 덱 13쪽 자리) |
| 15 | 모션그래픽 | 우리 중간본의 영상 장(v23) |
| 16~32 | 솔루션 3장, How it Works 14장 | `../09_HowItWorks/장표5_claude` 그대로 |
| 33~35 | 기대효과 세 장 | WIWLEE/t3-2 `Weave_BI_아웃트로_통합_1110_v7.pptx` 1~3쪽의 내용을 같은 엔진으로 다시 그림 |
| 36 | 비즈니스 임팩트 | 같은 덱 4쪽 |
| 37 | 기존 기능과의 비교 | 새로 그림 |
| 38 | Why Now · Why Samsung 연표 | 같은 덱 5쪽의 내용을 두 줄 연표로 다시 그림 |
| 39~41 | 마무리 세 장 | 같은 덱 6~8쪽의 문구를 사진 위에(글은 모두 흰색). 끝 로고 없이 말로 맺음 |
| 42~57 | Appendix | How it Works Appendix 15장, 사진 출처 1장 |
| 58~61 | 제안 장표 | 가름 장, 기대효과를 고리 그래프의 움직임으로 보여 주는 안 세 장 |
| 62~87 | 이전 판 (2차) | 가름 장, 2차 통합본의 인트로 2~14쪽, 빠진 고리(26쪽), 뒷부분 32~41쪽, 두 줄 연표 제안(62쪽) |
| 88~112 | 이전 판 (1차) | 가름 장, 1차 통합본의 인트로 2~13쪽과 뒷부분 32~41쪽, 저장 채널 그림, 인트로 덱의 13쪽 |

## 다시 만들기

```
~/.cache/weave-tools/venv/bin/python tools/hook_assets.py   # 6쪽의 앱 화면과 벽 그림, 카메라 아이콘 (assets/src → assets/hook)
~/.cache/weave-tools/venv/bin/python tools/intro_assets.py  # 3~5쪽의 기록 조각, 연표의 NPU 아이콘 (assets/src → assets/intro, assets/outro)
~/.cache/weave-tools/venv/bin/python make.py --png          # 덱 + out/png (PowerPoint로 렌더)
~/.cache/weave-tools/venv/bin/python tools/intro_assets.py --blur   # 12쪽을 고쳤을 때만: out/png의 12쪽을 흐리게 → 13쪽 배경. 그 뒤 make.py를 한 번 더
~/.cache/weave-tools/venv/bin/python talk.py                # 낭독 → 덱 → 녹화 → 낭독, 자막, 모션그래픽 소리를 얹은 영상
~/.cache/weave-tools/venv/bin/python talk.py --proposal
~/.cache/weave-tools/venv/bin/python trim.py                # 더 줄인 대본 안의 시간을 같은 목소리로 잼
~/.cache/weave-tools/venv/bin/python doc.py                 # 대본.md
~/.cache/weave-tools/venv/bin/python tools/overview.py      # 한눈에.jpg
```

- `원본/`에 네 덱을 둬야 해요(저장소에는 올리지 않아요).
  - https://github.com/jjun-0824/t3/blob/claude/pull-push-permissions-eacsir/weave/결선준비/02_PPT/Weave_결선_중간본_도입부수정.pptx
  - https://github.com/WIWLEE/t3-2/blob/main/Weave_BI_아웃트로_통합_1110_v7.pptx
  - `통합본_1차.pptx`: `git show ab7ab74:weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx > 원본/통합본_1차.pptx`
  - `통합본_2차.pptx`: `git show 9a8bddb:weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx > 원본/통합본_2차.pptx` (이전 판 묶음을 이 두 덱에서 옮겨요)
- 바탕 덱은 `../02_PPT/Weave_결선_중간본.pptx`예요. 읽기만 하고, 표지와 모션그래픽 장, 장 틀을 빌려 써요.
- `slides_new.py`에 새로 그린 장과 말할 글이 있어요(인트로 노트는 `INTRO_NOTES`, 새 장은 `NOTES`). 그리는 엔진과 낭독 도구는 `../09_HowItWorks/장표5_claude` 것을 그대로 써요.
- `make.py`의 `patch_cover`가 표지의 영상과 제목을, `patch_intro`가 옮겨 온 인트로 장의 노트, 화면 글, 고리 굵기, 말풍선, AI 표시, 흐린 배경, 삼성노트 아이콘을 바꿔요. `foreign.py`는 다른 덱의 장을 도형, 그림, 전환, 효과째로 옮겨요.
- `hook_layout.py`는 6쪽 벽에서 어느 자리에 어느 앱 화면이 놓이고 어디에 불이 켜지는지 적은 표예요.
- 낭독은 이 컴퓨터 안에서만 만들어요(Supertonic 3, 목소리 F2F1_70, 속도 1.15).
