# 09_HowItWorks — 9쪽 HOW IT WORKS 새 장표 + 논문 스터디

결선 덱 9쪽(HOW IT WORKS)을 클릭 10번으로 넘기는 한 장으로 다시 만들었어요. `02_PPT/Weave_결선.pptx`는 건드리지 않았고, 검토용 사본만 만들었어요.

저장소에는 `장표5/`(지금 쓰는 판), `리서치/`, `논문스터디/`만 둬요. `장표/` ~ `장표4/`와 `장표5/out/`은 작업 컴퓨터에만 있어요.

## 지금 쓰는 판 (2026-11-09부터)

- **`HowItWorks_Argon.pptx`**를 기준으로 고쳐요. Argon이 만든 판이고, 빌더는 `장표5/build.py`(본문 16장)와 `장표5/appendix.py`(Appendix 13장)예요.
  - 다시 만들기: `cd 장표5 && ~/.cache/weave-tools/venv/bin/python build.py --png`(흐린 그림을 그대로 쓰려면 `--skip-blur`). PowerPoint 잠금은 `render_c.py`가 스스로 잡으니 `flock`으로 감싸지 않아요.
  - 1쪽 솔루션 장은 `02_PPT/Weave_결선_중간본.pptx`의 5쪽을 가져와요. 중간본 솔루션 장을 고쳤으면 흐린 그림(2쪽)까지 다시 만들도록 `--skip-blur` 없이 빌드해요.
- 중간본 덱(`02_PPT/Weave_결선_중간본.pptx`, `11_중간본/build_deck.py`)의 How it Works(6~20쪽)와 Appendix(28~40쪽)도 같은 장이에요(15차부터). `build.py`의 `add_slides`와 `fix_solution`을 중간본 빌더가 불러서 그려요. 그래서 `장표5`를 고친 뒤에는 두 파일을 모두 다시 만들어요.
- `HowItWorks_Claude.pptx`(`Claude/`)는 비교용으로만 남겨 둬요.
- **`HowItWorks_Argon_claude.pptx`**(`장표5_claude/`)는 Argon판을 복사해 사용자 검토를 넣어 가는 판이에요(10차, 2026-11-12: 본문 16장 클릭 21번 + Appendix 15장, 노트 1,040음절, 낭독 영상 3분 35초). 낭독을 넣은 미리보기 영상은 **`HowItWorks_Argon_claude_미리보기.mp4`**예요. 바뀐 것, 발표 시간(`build.py --time`), 영상 만드는 법(`build.py --video --tts`)은 `장표5_claude/README.md`에 있어요. 중간본 덱에는 아직 들어가지 않았고, 통합본(`../통합본_Claude`)의 16~32쪽과 Appendix가 이 장들이에요.
- 메모 방식(AgentIR)은 본문에 넣지 않고, Appendix 22쪽에 Reasoning Embedding 파이프라인 후보로 로직과 원논문만 실었어요.

## 폴더

| 경로 | 내용 |
|---|---|
| `장표/build_hiw.py` | 장표 빌더(python-pptx + 손으로 쓴 애니메이션 XML). 시나리오·좌표·문구·클릭 순서·발표자 노트가 모두 여기 있음 |
| `장표/hiw_lib.py` | 도형·글자(Inter/Noto Sans KR 조각 나눔)·실(곡선)·묶음·애니메이션(p:timing) 도우미 |
| `장표/render.py` | Windows PowerPoint(COM)로 클릭 상태별 PNG와 미리보기 영상 만들기 (열린 PowerPoint 창은 건드리지 않음) |
| `장표/assets/` | 앱 아이콘, 와인 사진 2장(`photo-white.jpg`는 덱의 BABICH 사진, `photo-red.jpg`는 Codex로 같은 저녁 톤에 맞춰 만든 레드 와인 사진 — 원본 `red-wine-codex.png`) |
| `장표/out/HowItWorks.pptx` | **완성본 한 장**(클릭 애니메이션 + 클릭별 발표자 노트) |
| `장표/out/Weave_결선_HIW검토.pptx` | 작업 덱 사본에서 9쪽만 새 장표로 바꾼 검토용(나머지 18장은 그대로) |
| `장표/out/HowItWorks_미리보기.mp4` | 클릭 없이 저절로 넘어가는 판을 PowerPoint로 녹화한 50초 영상(애니메이션 확인용) |
| `장표/out/단계/s01–s11.png`, `단계_한눈에.png` | 클릭 0~10 상태를 PowerPoint로 렌더한 그림 |
| `장표/out/기존9쪽_발표자노트.txt` | 바꾸기 전 9쪽 발표자 노트(원문 그대로 보관) |
| `리서치/삼성_현재기술_조사.md` | Finder·PDE·Now Nudge·Gemini·Siri 등 공개 자료 검증(장표 문구 근거, "쓰면 안 되는 말" 목록) |
| `리서치/모션_레퍼런스.md` | 애니메이션 레퍼런스 10개와 클릭 빌드 규칙(인트로 수치와 맞춤) |
| `논문스터디/index.html` | 논문 9편 전문 + 한국어 번역 토글 공부 페이지(파일로 바로 열림) |

## 시나리오 (고도화한 와인)

"지은이네 집들이 때 마신 화이트 와인" — 캘린더엔 일정이 없고, 3/12(목) 지은의 카톡 "이번 일요일 6시, 이사 기념으로 우리 집에서 저녁 먹자!"만 남아 있어요('집들이'라는 말이 없음). 그날(3/15 일) 저녁 사진은 레드(19:52)와 화이트(20:14) 두 장이고, 라벨 어디에도 '화이트'라는 글자는 없어요.

| 클릭 | 화면 | 보여 주는 것 |
|---|---|---|
| 0 | 질문 카드 + 내 폰 속 기록 | 답은 이 안에 있음 |
| 1 | 단어로 찾기 · 예: 키워드 검색 | 글자만 같은 기록(BEST 5 캡처·와인 메모)이 걸림. 초대엔 '집들이', 라벨엔 '화이트'가 없음 |
| 2 | 관계로 찾기 · 예: PDE 방식¹ | 저장된 사실(일정)만 이음. 이 약속은 카톡에만 있어 이어진 일정 없음 |
| 3 | 비슷한 것 찾기 · 예: 일반 임베딩 | BEST 5 캡처 1위, 지은 카톡 2위 — 한 번 찾고 끝. 답이 담긴 사진은 질문과 안 닮아 순위 밖 |
| 4 | Weave · 탐색 메모 | 찾을 것(와인 이름·화이트) / 아는 단서(지은·집들이) / 먼저 볼 곳(카톡·캘린더) / 멈출 때 |
| 5 | ① 추론 검색 | '집들이' = '이사 기념으로 우리 집에서 저녁' → 지은의 카톡 |
| 6 | 새 단서 | '이번 일요일 6시' → 3/15 (일) 18:00 토큰이 메모로 들어가 다음 검색 조건이 됨 |
| 7 | ② 시간 필터 | 그날 저녁 사진 2장(날짜는 추론하지 않고 필터) |
| 8 | ③ 사진 속 글자 + 추론 검색 | CABERNET SAUVIGNON(레드) / BABICH SAUVIGNON BLANC(블랑 = 화이트) → 찾을 것이 채워져 멈춤 |
| 9 | 전달 | 배비치 소비뇽 블랑 + 출처(카톡 3/12, 갤러리 3/15 20:14) + 입력하기 |
| 10 | 핵심 엔진 | 온디바이스 Reasoning Embedding — 지금 단서로부터 '이어지는' 기록을 찾는 경량 모델 |

## 다시 만들기

```bash
cd 09_HowItWorks/장표
~/.cache/weave-tools/venv/bin/python build_hiw.py          # out/HowItWorks*.pptx
~/.cache/weave-tools/venv/bin/python build_hiw.py --deck   # out/Weave_결선_HIW검토.pptx
~/.cache/weave-tools/venv/bin/python render.py states      # out/단계/*.png (PowerPoint)
~/.cache/weave-tools/venv/bin/python render.py video       # out/HowItWorks_미리보기.mp4 (PowerPoint)
```

- 문구·좌표는 `build_hiw.py`의 `CARDS`, `compose()`에서 고치면 돼요. 클릭 순서는 각 요소의 `show`/`hide`/`enter`로 정해져요.
- PowerPoint에서 직접 고칠 때: 선택 창의 이름이 `1 걸린 카드`, `5 A1 바탕묶음`처럼 클릭 번호로 시작해요. 그룹을 풀면 그 그룹에 걸린 애니메이션이 사라지니 그룹째로 옮기세요.
- 잠깐 나왔다 사라지는 도형(클릭 1~3의 비교 표시, 새 단서 빈칸, 레드 사진 강조)은 **슬라이드 오른쪽 밖(+1600px)**에 놓여 있고, 그 클릭에서 순간 이동 경로로 제자리에 들어와요. 그래서 편집 화면·썸네일·PNG/PDF 내보내기는 최종 상태(클릭 10)와 똑같이 보여요(PowerPoint 렌더 비교 차이 0). 이 도형을 옮길 땐 슬라이드 밖 위치 그대로 두세요.
