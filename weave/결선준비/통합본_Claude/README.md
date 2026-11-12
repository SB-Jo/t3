# Weave 통합본 (Claude, 2026-11-13 6차)

인트로, 모션그래픽, 솔루션과 How it Works, 뒷부분, Appendix를 한 덱으로 합친 판이에요. 6차에서는 11월 13일에 받은 수정사항을 넣었어요. 3쪽을 클릭 한 번으로 나누고 기록 조각이 떠다니게 했고, 기대효과 세 장을 한 장(AS-IS → TO-BE)으로 줄였고, 기존 기능과의 비교는 Appendix로 옮겼고, 마무리 사진 세 장과 출처 표기를 바꿨어요. 바꾼 곳은 `대본.md`의 '5차에서 바꾼 곳'에 쪽마다 적었어요.

| 파일 | 내용 |
| --- | --- |
| `Weave_통합본_Claude.pptx` | 통합 덱 152장(본 발표 37장, Appendix 17장, 이전 판 5차 28장, 4차 9장, 3차 10장, 2차 26장, 1차 25장) |
| `Weave_통합본_Claude_미리보기.mp4` | 본 발표 37장을 처음부터 끝까지 말하며 넘긴 영상(낭독, 자막) |
| `대본.md` | 장마다 말할 글과 영상에서 잰 시간, 5차에서 바꾼 곳, 더 줄일 곳, 이전 대본 |
| `한눈에.jpg` | 152장을 한 장에 모은 그림 |
| `마무리사진_후보/` | 마무리 세 장의 사진 후보 195장과 시안. 덱에는 G15, A2, M4를 넣었어요 |
| `기대효과_후보/` | 기대효과 한 장(32쪽, 후보 L을 손본 판)만 따로 본 것: 31~33쪽을 말하며 넘긴 영상, 그 장만 담은 덱, 세 순간을 모은 그림, 고른 기록 |
| `비교장표_후보/` | 기존 기능과의 비교 장 후보 넷. 후보 나에 글을 보태 Appendix 39쪽에 넣었어요 |
| `assets/` | 6쪽의 앱 화면과 그 소스, 3~5쪽의 기록 조각, 마무리 사진 세 장, 아웃트로 덱에서 가져온 그림. 출처는 `assets/CREDITS.md` |

## 덱 차례

| 쪽 | 묶음 | 어디서 왔나 |
| --- | --- | --- |
| 1 | 표지 | 우리 중간본의 표지. 영상은 표지 영상 v9(`../10_표지영상`, 18초)로 바꾸고 제목을 48pt로 줄임 |
| 2~5 | 인트로 | 팀원이 손본 덱(jjun-0824/t3 87bf80b)의 2~5쪽. 6차에서 3쪽의 첫 인물과 말풍선을 클릭으로 미루고(`patch_person_click`), 3~5쪽의 옅은 기록 조각을 세 층으로 나눠 떠다니게 했어요(`patch_floats`). 4·5쪽의 둘째 말풍선은 '정확한 이름이 뭐였지?'(`patch_ask2`) |
| 6 | 수많은 기록 | 새로 그림(`slides_new.py`의 `s_hook`) |
| 7~14 | 설문 두 장, 기록을 남기는 곳, AI에게 묻는데, 흩어진 기록이 이어짐, 물을 순 없을까요, 잇는 장 | 팀원이 손본 덱의 7~14쪽(도형, 그림, 전환, 효과). 6차에서 7쪽 머리글(`patch_heading7`), 9쪽 글자 크기(`patch_hub`), 10쪽 AI 답변(`patch_answer`)을 바꿨어요 |
| 15 | 모션그래픽 | 우리 중간본의 영상 장. 영상은 v24(`../08_인트로영상`)로 바꿔 끼움 |
| 16~31 | 솔루션 3장, How it Works 13장 | `../09_HowItWorks/장표5_claude` 그대로 |
| 32 | 기대효과 (AS-IS → TO-BE) | 새로 그림(`fx_new.py`의 `s_fx`). 5차의 세 장을 한 장으로 |
| 33 | 비즈니스 임팩트 | WIWLEE/t3-2 `Weave_BI_아웃트로_통합_1110_v7.pptx` 4쪽의 내용을 같은 엔진으로 다시 그림. 왼쪽 앱 아이콘은 14개 |
| 34 | Why Now · Why Samsung 연표 | 같은 덱 5쪽의 내용을 두 줄 연표로 다시 그림 |
| 35~37 | 마무리 세 장 | 같은 덱 6~8쪽의 문구를 사진 위에(글은 모두 흰색). 사진은 G15, A2, M4. 끝 로고 없이 말로 맺음 |
| 38~54 | Appendix | 가름 장, 기존 기능과의 비교(39쪽), How it Works Appendix 14장(40~53쪽), 사진과 음악 출처(54쪽) |
| 55~82 | 이전 판 (5차) | 가름 장, 5차 통합본에서 6차에 화면이나 대본이 바뀐 27장(기대효과 세 장, 비교 지도, 마무리 세 장, 제안 장표 포함) |
| 83~91 | 이전 판 (4차) | 가름 장, 4차 통합본의 7~14쪽(팀원이 손본 장으로 바뀌기 전) |
| 92~101 | 이전 판 (3차) | 가름 장, 3차 통합본의 16쪽, 뺀 21쪽(흩어진 단서), 22~26쪽, 30쪽, 비교 표(37쪽) |
| 102~127 | 이전 판 (2차) | 가름 장, 2차 통합본의 인트로 2~14쪽, 빠진 고리(26쪽), 뒷부분 32~41쪽, 두 줄 연표 제안(62쪽) |
| 128~152 | 이전 판 (1차) | 가름 장, 1차 통합본의 인트로 2~13쪽과 뒷부분 32~41쪽, 저장 채널 그림, 인트로 덱의 13쪽 |

클릭은 3쪽에 한 번, 6쪽에 여섯 번, 16~31쪽에 22번, 32쪽에 세 번, 33쪽에 두 번, 34쪽에 세 번이에요. 나머지 장은 넘기기만 해요.

## 다시 만들기

```
~/.cache/weave-tools/venv/bin/python tools/hook_assets.py   # 6쪽의 앱 화면과 벽 그림, 카메라 아이콘 (assets/src → assets/hook)
~/.cache/weave-tools/venv/bin/python tools/intro_assets.py  # 3~5쪽의 기록 조각(한 장과 세 층), 연표의 NPU 아이콘 (assets/src → assets/intro, assets/outro)
~/.cache/weave-tools/venv/bin/python make.py --png          # 덱 + out/png (PowerPoint로 렌더)
~/.cache/weave-tools/venv/bin/python talk.py                # 낭독 → 덱 → 녹화 → 낭독, 자막, 모션그래픽 소리를 얹은 영상
~/.cache/weave-tools/venv/bin/python trim.py                # 더 줄인 대본 안의 시간을 같은 목소리로 잼
~/.cache/weave-tools/venv/bin/python doc.py                 # 대본.md
~/.cache/weave-tools/venv/bin/python tools/overview.py      # 한눈에.jpg
~/.cache/weave-tools/venv/bin/python tools/fx_try.py        # 기대효과 한 장(fx_new.py의 s_fx)을 앞뒤 장과 함께 찍은 영상, 그 장만 담은 덱, 한눈에.jpg → 기대효과_후보/
~/.cache/weave-tools/venv/bin/python tools/cmp_try.py       # 비교 장 후보(cmp_new.py)의 영상과 덱 → 비교장표_후보/
```

- `원본/`에 여덟 덱을 둬야 해요(저장소에는 올리지 않아요).
  - https://github.com/jjun-0824/t3/blob/claude/pull-push-permissions-eacsir/weave/결선준비/02_PPT/Weave_결선_중간본_도입부수정.pptx
  - https://github.com/WIWLEE/t3-2/blob/main/Weave_BI_아웃트로_통합_1110_v7.pptx
  - `통합본_1차.pptx`: `git show ab7ab74:weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx > 원본/통합본_1차.pptx`
  - `통합본_2차.pptx`: `git show 9a8bddb:weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx > 원본/통합본_2차.pptx`
  - `통합본_3차.pptx`: `git show ab0c460:weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx > 원본/통합본_3차.pptx`
  - `통합본_4차.pptx`: `git show 406c351:weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx > 원본/통합본_4차.pptx`
  - `통합본_5차.pptx`: `git show fcf8346:weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx > 원본/통합본_5차.pptx` (이전 판 묶음을 이 다섯 덱에서 옮겨요)
  - `통합본_인트로수정_87bf80b.pptx`: https://github.com/jjun-0824/t3/blob/87bf80bdc1ee5e580a44f22fa619558c998bb794/weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx (인트로 2~5쪽과 7~14쪽을 여기서 옮겨요)
- 바탕 덱은 `../02_PPT/Weave_결선_중간본.pptx`예요. 읽기만 하고, 표지와 모션그래픽 장, 장 틀을 빌려 써요.
- `slides_new.py`에 새로 그린 장과 말할 글이 있어요(인트로 노트는 `INTRO_NOTES`, 새 장은 `NOTES`). 기대효과 한 장은 `fx_new.py`의 `s_fx`, Appendix의 비교 장은 `cmp_new.py`의 `s_cmp_apx`예요. `slides_new.py`의 `s_hub2`, `s_scat`, `s_link`, `s_bridge`(9, 11~12, 14쪽), `s_fx`(기대효과 세 장), `s_cmp`(비교 지도)는 앞선 차수에 쓰던 것이에요. 그리는 엔진과 낭독 도구는 `../09_HowItWorks/장표5_claude` 것을 그대로 써요.
- `make.py`의 `copy_intro`가 팀원이 손본 덱에서 인트로 장을 옮겨 와요(`FOREIGN`에 키와 쪽). 옮긴 뒤에 손보는 곳은 `INTRO_PATCH`에 장마다 적었고, 노트를 우리 글로 바꾼 장은 `NOTE_OURS`예요. `patch_cover`가 표지의 영상과 제목을, `patch_mg`가 모션그래픽 장의 영상을 바꿔요. `foreign.py`는 다른 덱의 장을 도형, 그림, 전환, 효과째로 옮겨요.
- 3~5쪽의 기록 조각은 끝없이 되풀이하는 이동 효과로 떠다녀요(`FLOAT_LAYERS`에 층마다 방향과 빠르기). 세 장이 Morph로 이어져서 넘어갈 때 조각이 튀지 않아요.
- 옮겨 온 장에 클릭이 있으면(3쪽) 노트의 `(클릭)`으로 말을 나누고, 녹화용 사본에서는 `foreign.auto_play`가 클릭 묶음을 앞말이 끝나는 때에 저절로 나오게 바꿔요.
- PowerPoint는 영상으로 내보낼 때 끝없이 되풀이하는 효과가 한 번 다 돌 때까지 그 장에 머물러요. 그래서 녹화용 사본에서는 `foreign.cap_repeats`가 되풀이 수를 그 장에 머무는 시간만큼으로 줄여요.
- `hook_layout.py`는 6쪽 벽에서 어느 자리에 어느 앱 화면이 놓이고 어디에 불이 켜지는지 적은 표예요.
- 낭독은 이 컴퓨터 안에서만 만들어요(Supertonic 3, 목소리 F2F1_70, 속도 1.15).
