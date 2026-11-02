# 결선 중간본 덱 (2026-11-02, 4차)

원본 `02_PPT/Weave_결선.pptx`는 그대로 두고, 새 파일 **`02_PPT/Weave_결선_중간본.pptx`**를 조립해요.

## 구성 (35장)

| 구분 | 장 | 내용 |
|---|---|---|
| 본편 | 1 | **표지 (반복 영상)**: `10_표지영상/표지_루프.mp4`(v3, 4K, 18초). 자동 재생, 끝나면 반복. 왼쪽 글은 PPT 글상자 |
| 본편 | 2–3 | Motivation, Pain Points (원본 3·4쪽 그대로) |
| 본편 | 4 | **인포그래픽 영상 자리**: Pain Points의 세 불편 바로 뒤. 영상 넣을 자리 표시만 있음 |
| 본편 | 5 | **Solution**: 새 시나리오 셋(요청 자료 / 집들이 와인 / 갈색병). `07_소스/slides/p05_결선/` |
| 본편 | 6–17 | **How it Works**: 장표5 A1 덱용 00판 12장, 클릭 23번(`09_HowItWorks/장표5/a1_deck00.py`). 00 사전 준비(모든 기록 → 벡터 숫자 + `{date, app}`)부터, 키워드·임베딩 검색은 한 장(왼쪽·오른쪽), Query Rewriting 판은 왼쪽에 둔 채 홉마다 채움 |
| 본편 | 18–24 | Why Samsung, Why Now, 차별화, 기대효과 1~3, END (원본 그대로) |
| 부록 | 25–27 | App Demo, Q&A 2장 (원본 그대로) |
| 참고 | 28–35 | 구분 장, 이전 표지, 만화, 이전 시나리오 1~3, 이전 How it Works, 인트로 영상 79초 (발표에서 안 씀) |

## 표지

- 'Weave' 앞에 인트로 끝 화면과 같은 아이콘(보라 그라데이션 네모 + 흰 실타래)을 달았어요.
- 제목 글꼴은 인트로 로고와 같은 Samsung Sharp Sans Bold예요.
- 팀 이름 배치는 두 가지예요. 기본은 `under`예요.
  - `under`: 팀원 이름을 한 줄로 두고, 그 아래 가는 선과 팀 이름을 둬요.
  - `side`: 이름 둘을 위아래로 두고, 오른쪽에 팀 이름을 두 줄로 둬요('AI System / Team').
- 팀: 이재웅·양서윤 AI System Team, 장이준·이지현 AI Core Team, 조성빈 오디오개발Lab.

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
~/.cache/weave-tools/venv/bin/python build_deck.py           # 조립 → 글꼴 바꾸기 → 영상 넣기(PowerPoint) → png/·한눈에.png
~/.cache/weave-tools/venv/bin/python build_deck.py --no-png
~/.cache/weave-tools/venv/bin/python build_deck.py --hiw a1_deck --out /tmp/중간본_00없음.pptx                   # How it Works 00 없는 판
~/.cache/weave-tools/venv/bin/python build_deck.py --team-style side                                             # 표지 팀 배치 바꾸기
```

- 솔루션 장표는 `07_소스/slides/p05_결선/apply_solution.py`로 다시 채워요.
- How it Works는 `09_HowItWorks/장표5`의 엔진(`scene5.py`, `build5.add_steps`)으로 덱 안에 바로 그려요.
- 영상은 PowerPoint(COM)로 넣어요. 표지는 '자동 재생 + 반복', 참고 구간 인트로는 '자동 재생 한 번'이에요. 열려 있는 PowerPoint 창은 건드리지 않아요.
- PowerPoint를 쓰는 작업은 `flock /tmp/weave-ppt.lock …`으로 하나씩 돌려요(장표5 렌더와 겹치지 않게).

## 원본에서 바뀐 것

- 1쪽 표지: 사진 한 장 → 반복 영상 + 아이콘·제목·부제·팀. 이전 표지는 참고 구간으로 옮겼어요.
- 2쪽 만화: 참고 구간으로 옮겼어요. 그 대신 Pain Points 뒤(4쪽)에 인포그래픽 영상 자리를 넣었어요.
- 5쪽 Solution: 시나리오를 새 셋으로 바꿨어요(바뀐 문구는 `07_소스/slides/p05_결선/` 참고).
- 6~8쪽 시나리오, 9쪽 How it Works: 새 How it Works 12장(00판)으로 대체하고, 이전 장표는 참고 구간으로 옮겼어요.
- 인트로 영상 79초: 02·03 장면이 새 시나리오와 달라 참고 구간에만 넣었어요.
- 글꼴: 전체를 SamsungOne 계열로 바꿨어요(위 '글꼴').
