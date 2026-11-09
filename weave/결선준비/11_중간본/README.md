# 결선 중간본 덱 (2026-11-09, 15차: How it Works와 Appendix를 Argon판으로)

원본 `02_PPT/Weave_결선.pptx`는 그대로 두고, 새 파일 **`02_PPT/Weave_결선_중간본.pptx`**를 조립해요. 바뀐 글은 전부 [`문구_변경목록.md`](문구_변경목록.md)에 있어요.

## 구성 (48장)

| 구분 | 장 | 내용 |
|---|---|---|
| 본편 | 1 | **표지 (반복 영상)**: `10_표지영상/표지_루프.mp4`(v8, 4K, 22초). 자동 재생, 끝나면 반복. 왼쪽 글은 PPT 글상자(15차: 제목 54pt, 아이콘·부제·간격도 같은 비율로 키우고 묶음을 6pt 올림) |
| 본편 | 2–3 | Motivation, Pain Points (말투 수정) |
| 본편 | 4 | **모션그래픽 영상**: `08_인트로영상/Weave_모션그래픽.mp4`(v21, 1분 58초). 자동 재생 한 번. Pain Points의 세 불편에 세 장면이 차례로 답해요 |
| 본편 | 5 | **Solution**: UX 1 삼성기술전 / UX 2 집들이 와인 / UX 3 입국 갈색병. `07_소스/slides/p05_결선/`. 노트와 오른쪽 위 빛(노랑 → 보라)은 Argon판과 같아요 |
| 본편 | 6–20 | **How it Works (Argon판 15장)**: `09_HowItWorks/장표5/build.py`의 `SLIDES`. How it works? → 질문 → 흩어진 단서 → 기존 검색이라면? → 키워드 → 임베딩 → Let's think step by step! → 끊어진 고리 → 00 데이터 색인 → 01 상황 인식 → 02 질의 재작성 → 03 Hop 1 → 03 Hop 2 → 04 결과 제공 → 한눈에 보기 |
| 본편 | 21–27 | Why Samsung, Why Now, 차별화, 기대효과 1~3, END (말투 수정, 시나리오 예시 교체) |
| 부록 | 28–40 | **Appendix (Argon판 13장)**: `장표5/appendix.py`의 `APPENDIX`. 구분 장, 단계별 모델과 역할, Reasoning Embedding과 질의 재작성, 지식 그래프와 비교 2장, 검색 방식 비교, 세 UX 공통 파이프라인, Q&A 5장(PDE, 같은 날 사진, Apple, LLM, 데이터 접근), 사진 출처 |
| 참고 | 41–48 | 구분 장, 앱 데모, 이전 표지, 만화, 이전 시나리오 1~3, 이전 How it Works (발표에서 안 씀) |

5~20쪽과 28~40쪽은 `09_HowItWorks/HowItWorks_Argon.pptx`와 같은 장이에요. 두 파일 모두 `장표5/build.py`의 `add_slides`로 그려요.

## 표지

- 'Weave' 앞에 인트로 끝 화면과 같은 아이콘(보라 그라데이션 네모 + 흰 실타래)을 달았어요.
- 제목 글꼴은 인트로 로고와 같은 Samsung Sharp Sans Bold예요.
- 팀 이름 배치는 두 가지예요. 기본은 `under`예요.
  - `under`: 팀원 이름을 한 줄로 두고, 그 아래 가는 선과 팀 이름을 둬요.
  - `side`: 이름 둘을 위아래로 두고, 오른쪽에 팀 이름을 두 줄로 둬요('AI System / Team').
- 팀: 이재웅·양서윤 Samsung Research AI System Team, 장이준·이지현 Samsung Research AI Core Team, 조성빈 하만협력 오디오개발Lab. END 장도 같게 맞췄어요.
- 부제는 SamsungOneKorean 700이에요.

## 글꼴 (SamsungOne)

- 조립할 때 `samsung_fonts.remap_prs`가 Inter·Noto Sans KR을 SamsungOneKorean으로 바꿔요.
  - 보통 → 400, Medium → 500, SemiBold·Bold → 700. 굵게 표시는 700 글꼴로 대신해요.
- 그대로 두는 것은 손글씨 강조(Nanum Pen Script)와 표지 제목(Samsung Sharp Sans)이에요.
- 이 덱을 제대로 보려면 아래 글꼴이 설치돼 있어야 해요.
  - SamsungOneKorean 400, 500, 700
  - Samsung Sharp Sans (Bold)
  - Nanum Pen Script
- 이 컴퓨터에는 웹 글꼴을 TTF로 바꿔 Windows 사용자 글꼴로 설치했어요. TTF는 `~/.cache/weave-tools/fonts`에 있어요.
- 삼성 글꼴 파일은 공개 저장소에 올리지 않아요(`../.gitignore`, 받는 곳은 `06_에셋/글꼴/SOURCES.md`).
- 받는 사람이 글꼴 없이 보게 하려면 `--embed-fonts`로 글꼴을 파일 안에 넣어 저장해요. 용량이 늘고, 삼성 글꼴이 파일에 들어가므로 공개 저장소에는 올리지 마세요.

## 다시 만들기

```bash
flock /tmp/weave-ppt.lock ~/.cache/weave-tools/venv/bin/python build_deck.py           # 조립 → 글꼴 바꾸기 → 영상 넣기(PowerPoint) → png/·한눈에.png·문구_변경목록.md
flock /tmp/weave-ppt.lock ~/.cache/weave-tools/venv/bin/python build_deck.py --no-png
flock /tmp/weave-ppt.lock ~/.cache/weave-tools/venv/bin/python build_deck.py --hiw a1_deck00 --out /tmp/중간본_00판.pptx   # 예전 How it Works(00판 12장) + 예전 Appendix 7장 + Q&A 2장
flock /tmp/weave-ppt.lock ~/.cache/weave-tools/venv/bin/python build_deck.py --team-style side                            # 표지 팀 배치 바꾸기
```

- 솔루션 장표는 `07_소스/slides/p05_결선/apply_solution.py`로 다시 채워요.
- How it Works와 Appendix는 `09_HowItWorks/장표5/build.py`의 `add_slides`로 덱 안에 바로 그려요(Argon판). 앞 장을 흐리게 깐 그림(`장표5/out/blur_sol.png`, `blur_emb.png`)이 없으면 먼저 `장표5/build.py`를 한 번 돌려요.
- 예전 판(`--hiw a1_deck00`)의 How it Works는 `장표5`의 옛 엔진(`scene5.py`, `build5.add_steps`), Appendix와 Q&A는 `07_소스/slides/appendix_결선/apply_appendix.py`로 채워요.
- 영상은 PowerPoint(COM)로 넣어요. 표지는 '자동 재생 + 반복', 모션그래픽은 '자동 재생 한 번'이에요. 열려 있는 PowerPoint 창은 건드리지 않아요.
- 나머지 장의 글과 노트는 `build_deck.py`의 `EDITS`, `NOTES`에서 고쳐요. 글자 조각(run)마다 바꿔서 색과 굵기를 그대로 둬요.

## 원본에서 바뀐 것

- 1쪽 표지: 사진 한 장 → 반복 영상 + 아이콘·제목·부제·팀. 이전 표지는 참고 구간으로 옮겼어요.
- 2쪽 만화: 참고 구간으로 옮겼어요. 그 대신 Pain Points 뒤(4쪽)에 모션그래픽 영상을 넣었어요.
- 5쪽 Solution: 시나리오를 최종 셋으로 바꿨어요.
- 6~8쪽 시나리오, 9쪽 How it Works: 새 How it Works로 대체하고(15차부터 Argon판 15장), 이전 장표는 참고 구간으로 옮겼어요.
- Appendix와 Q&A: 15차부터 Argon판 Appendix 13장이에요(예전 Appendix 7장과 Q&A 2장 대신).
- App Demo: 이전 시나리오(A사 시연, 무화과시루, 캘린더 집들이)라서 참고 구간으로 옮겼어요.
- 글꼴: 전체를 SamsungOne 계열로 바꿨어요(위 '글꼴').
