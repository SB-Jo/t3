# Weave 통합본 (Claude, 2026-11-12 5차)

인트로, 모션그래픽, 솔루션과 How it Works, 뒷부분, Appendix를 한 덱으로 합친 판이에요. 5차에서 인트로 7~14쪽을 팀원이 손본 덱(jjun-0824/t3 87bf80b)의 장과 노트로 바꿨어요. 바꾼 곳은 `대본.md`의 '4차에서 바꾼 곳'에 쪽마다 적었어요. 5차 뒤(11월 12일 밤)에 덱 전체의 '이름이'를 '정확한 이름이'로 바꾸고 기대효과의 '검색으로 바로 찾지'에서 '바로'를 뺐어요(`대본.md`의 '5차 뒤에 바꾼 곳').

| 파일 | 내용 |
| --- | --- |
| `Weave_통합본_Claude.pptx` | 통합 덱 130장(본 발표 40장, Appendix 16장, 제안 장표 4장, 이전 판 4차 9장, 3차 10장, 2차 26장, 1차 25장) |
| `Weave_통합본_Claude_미리보기.mp4` | 본 발표 40장을 처음부터 끝까지 말하며 넘긴 영상(낭독, 자막) |
| `제안장표_미리보기.mp4` | 제안 장표 세 장을 말하며 넘긴 영상 |
| `대본.md` | 장마다 말할 글과 영상에서 잰 시간, 4차에서 바꾼 곳, 더 줄일 곳, 이전 대본 |
| `한눈에.jpg` | 130장을 한 장에 모은 그림 |
| `마무리사진_후보/` | 마무리 세 장에 바꿔 넣을 사진 후보 186장과 시안(덱에는 아직 넣지 않음) |
| `기대효과_후보/` | 기대효과 세 장(32~34쪽)을 한 장으로 바꾸는 후보(지금 고르는 것은 3차의 J, K, L): 앞뒤 장과 함께 말하며 넘긴 영상, 후보를 모은 덱(덱에는 아직 넣지 않음) |
| `비교장표_후보/` | 35쪽(기존 기능과의 비교)을 바꾸는 후보 넷(가 두 띠, 나 넓이와 깊이, 다 네 칸, 라 계단): 그 장을 말하며 넘긴 영상, 후보를 모은 덱(덱에는 아직 넣지 않음) |
| `assets/` | 6쪽의 앱 화면과 그 소스, 3~5쪽의 기록 조각, 마무리 사진 세 장(CC0), 아웃트로 덱에서 가져온 그림. 출처는 `assets/CREDITS.md` |

## 덱 차례

| 쪽 | 묶음 | 어디서 왔나 |
| --- | --- | --- |
| 1 | 표지 | 우리 중간본의 표지. 영상은 표지 영상 v9(`../10_표지영상`, 18초)로 바꾸고 제목을 48pt로 줄임 |
| 2~5 | 인트로 | 팀원이 손본 덱(jjun-0824/t3 87bf80b)의 2~5쪽. 우리 3차 덱과 같은 장이에요. 4·5쪽의 둘째 말풍선만 '그 이름이 뭐였지?'를 '정확한 이름이 뭐였지?'로 바꿨어요(`make.py`의 `patch_ask2`) |
| 6 | 수많은 기록 | 새로 그림(`slides_new.py`의 `s_hook`) |
| 7~14 | 설문 두 장, 기록을 남기는 곳, AI에게 묻는데, 흩어진 기록이 이어짐, 물을 순 없을까요, 잇는 장 | 팀원이 손본 덱의 7~14쪽을 그대로 옮김(도형, 그림, 전환, 효과, 노트). 클릭이 없어요 |
| 15 | 모션그래픽 | 우리 중간본의 영상 장. 영상은 v24(`../08_인트로영상`, 제목의 색과 자간을 표지와 같게)로 바꿔 끼움 |
| 16~31 | 솔루션 3장, How it Works 13장 | `../09_HowItWorks/장표5_claude` 그대로 |
| 32~34 | 기대효과 세 장 | WIWLEE/t3-2 `Weave_BI_아웃트로_통합_1110_v7.pptx` 1~3쪽의 내용을 같은 엔진으로 다시 그림 |
| 35 | 기존 기능과의 비교 | 새로 그림(두 축의 지도: 찾는 범위 × 찾는 방식) |
| 36 | 비즈니스 임팩트 | 같은 덱 4쪽 |
| 37 | Why Now · Why Samsung 연표 | 같은 덱 5쪽의 내용을 두 줄 연표로 다시 그림 |
| 38~40 | 마무리 세 장 | 같은 덱 6~8쪽의 문구를 사진 위에(글은 모두 흰색). 끝 로고 없이 말로 맺음 |
| 41~56 | Appendix | How it Works Appendix 15장, 사진 출처 1장 |
| 57~60 | 제안 장표 | 가름 장, 기대효과를 고리 그래프의 움직임으로 보여 주는 안 세 장 |
| 61~69 | 이전 판 (4차) | 가름 장, 4차 통합본의 7~14쪽(팀원이 손본 장으로 바뀌기 전) |
| 70~79 | 이전 판 (3차) | 가름 장, 3차 통합본의 16쪽, 뺀 21쪽(흩어진 단서), 22~26쪽, 30쪽, 비교 표(37쪽) |
| 80~105 | 이전 판 (2차) | 가름 장, 2차 통합본의 인트로 2~14쪽, 빠진 고리(26쪽), 뒷부분 32~41쪽, 두 줄 연표 제안(62쪽) |
| 106~130 | 이전 판 (1차) | 가름 장, 1차 통합본의 인트로 2~13쪽과 뒷부분 32~41쪽, 저장 채널 그림, 인트로 덱의 13쪽 |

## 다시 만들기

```
~/.cache/weave-tools/venv/bin/python tools/hook_assets.py   # 6쪽의 앱 화면과 벽 그림, 카메라 아이콘 (assets/src → assets/hook)
~/.cache/weave-tools/venv/bin/python tools/intro_assets.py  # 3~5쪽의 기록 조각, 연표의 NPU 아이콘 (assets/src → assets/intro, assets/outro)
~/.cache/weave-tools/venv/bin/python make.py --png          # 덱 + out/png (PowerPoint로 렌더)
~/.cache/weave-tools/venv/bin/python talk.py                # 낭독 → 덱 → 녹화 → 낭독, 자막, 모션그래픽 소리를 얹은 영상
~/.cache/weave-tools/venv/bin/python talk.py --proposal
~/.cache/weave-tools/venv/bin/python trim.py                # 더 줄인 대본 안의 시간을 같은 목소리로 잼
~/.cache/weave-tools/venv/bin/python doc.py                 # 대본.md
~/.cache/weave-tools/venv/bin/python tools/overview.py      # 한눈에.jpg
~/.cache/weave-tools/venv/bin/python tools/fx_try.py        # 기대효과 한 장 후보(fx_new.py)의 영상과 덱 → 기대효과_후보/
~/.cache/weave-tools/venv/bin/python tools/cmp_try.py       # 비교 장 후보(cmp_new.py)의 영상과 덱 → 비교장표_후보/
```

- `원본/`에 일곱 덱을 둬야 해요(저장소에는 올리지 않아요).
  - https://github.com/jjun-0824/t3/blob/claude/pull-push-permissions-eacsir/weave/결선준비/02_PPT/Weave_결선_중간본_도입부수정.pptx
  - https://github.com/WIWLEE/t3-2/blob/main/Weave_BI_아웃트로_통합_1110_v7.pptx
  - `통합본_1차.pptx`: `git show ab7ab74:weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx > 원본/통합본_1차.pptx`
  - `통합본_2차.pptx`: `git show 9a8bddb:weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx > 원본/통합본_2차.pptx`
  - `통합본_3차.pptx`: `git show ab0c460:weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx > 원본/통합본_3차.pptx`
  - `통합본_4차.pptx`: `git show 406c351:weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx > 원본/통합본_4차.pptx` (이전 판 묶음을 이 네 덱에서 옮겨요)
  - `통합본_인트로수정_87bf80b.pptx`: https://github.com/jjun-0824/t3/blob/87bf80bdc1ee5e580a44f22fa619558c998bb794/weave/결선준비/통합본_Claude/Weave_통합본_Claude.pptx (인트로 2~5쪽과 7~14쪽을 여기서 옮겨요)
- 바탕 덱은 `../02_PPT/Weave_결선_중간본.pptx`예요. 읽기만 하고, 표지와 모션그래픽 장, 장 틀을 빌려 써요.
- `slides_new.py`에 새로 그린 장과 말할 글이 있어요(인트로 노트는 `INTRO_NOTES`, 새 장은 `NOTES`). 9, 11~12, 14쪽을 그리던 `s_hub2`, `s_scat`, `s_link`, `s_bridge`는 4차까지 쓰던 것이에요. 그리는 엔진과 낭독 도구는 `../09_HowItWorks/장표5_claude` 것을 그대로 써요.
- `make.py`의 `copy_intro`가 팀원이 손본 덱에서 인트로 장을 옮겨 와요(`FOREIGN`에 키와 쪽). `patch_cover`가 표지의 영상과 제목을, `patch_mg`가 모션그래픽 장의 영상을 바꿔요. `patch_intro`(옮겨 온 인트로 장의 노트, 화면 글, 고리 굵기, 말풍선, AI 표시, 흐린 배경, 삼성노트 아이콘을 바꿈)는 4차까지 쓰던 것으로, 이미 손본 장을 옮겨 오는 지금은 부르지 않아요. `foreign.py`는 다른 덱의 장을 도형, 그림, 전환, 효과째로 옮겨요.
- `hook_layout.py`는 6쪽 벽에서 어느 자리에 어느 앱 화면이 놓이고 어디에 불이 켜지는지 적은 표예요.
- 낭독은 이 컴퓨터 안에서만 만들어요(Supertonic 3, 목소리 F2F1_70, 속도 1.15).
