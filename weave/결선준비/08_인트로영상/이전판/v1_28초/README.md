# 결선 인트로 영상 (28초, 1차본)

발표 시작에 트는 제품 광고 느낌의 훅 영상이에요. 1920×1080, 60fps, H.264 + AAC라서 PowerPoint의 삽입 → 비디오에 그대로 넣을 수 있어요.

| 파일 | 내용 |
| --- | --- |
| `Weave_인트로_28초.mp4` | 완성본(음악·효과음 포함) |
| `Weave_인트로_28초_무음.mp4` | 같은 영상, 소리 없음(다른 음악을 깔 때) |
| `배경음악/` | `음악+효과음.wav`, `음악만.wav`, `효과음만.wav` (48kHz, 직접 합성해서 저작권 걱정 없음) |
| `미리보기_1초간격.jpg` | 1초마다 한 장씩 모은 미리보기 |
| `표지_엔드카드.png` | 마지막 로고 화면 |
| `소스/` | 영상 원본(HTML·CSS·GSAP 타임라인 `main.js`, 글꼴·아이콘·사진) |
| `tools/` | `render.cjs`(프레임 찍기 → mp4), `music.py`(음악·효과음 합성) |
| `out/` | 도구가 쓰는 작업 폴더(events.json, bgm*.wav, weave_intro.mp4) |

## 구성 (120 BPM, 한 마디 2초)

| 시간 | 장면 | 화면 |
| --- | --- | --- |
| 0–2초 | 질문 | "그때 그 와인, 이름이 뭐였더라?" |
| 2–4초 | 흩어진 기록 | 앱 기록 조각 24개가 3D 공간에 쏟아짐 · 대화 5년 치 / 사진 1만 장 / 메모 500개 |
| 4–6초 | 불편 | "잠깐만, 찾아볼게…" (구성안 Motivation 문장) |
| 6–12초 | 엮기 | 6초 드롭. Weave 검색창 → 실이 캘린더(언제였지?) → 그날 사진(그날 찍은 사진엔?) → 라벨 글자 인식(라벨엔 뭐라고?) → "배비치 소비뇽 블랑" · "단서에서 단서로, 기억을 엮습니다" |
| 12–15.6초 | 검색할 때 | 휴대폰 속 Weave 시트 → 입력하기 → 검색창이 정확한 이름으로 바뀌고 결과가 뜸 |
| 15.6–19.6초 | 통화할 때 | 재웅 선배 통화 중 위로 올리기 → "A사 시연 관련 자료" → 메모·메일·카톡 3개 → 메일 확대 |
| 19.6–24초 | 답장할 때 | 엄마 카톡 → 가족 단체방 + 현재 위치로 문장 추천 → 입력·전송 → 엄마 답장 "감동이야 우리 딸!" |
| 24–28초 | 마무리 | Weave Assist 로고 · "그때 그거? Weave got it." · "흩어진 기록을 엮어, 필요한 순간 건네는 온디바이스 AI" → 흰 화면으로 |

- 앱 화면은 데모 녹화(`04_동영상·데모`)를 보고 HTML로 다시 그렸어요. 녹화에는 마우스 커서가 보여서 그대로 쓰지 않았어요.
- 사진은 데모의 와인 사진 한 장만 써요. 사람 얼굴은 나오지 않아요.
- 누르는 손과 보라 반짝임은 덱의 터치 표시(2쪽 만화의 손)와 같아요.
- 확대 카드와 보라 실, 손글씨 질문은 덱의 표현 방식을 따랐어요.
- 음악은 다장조예요. 도입은 Am7–Fmaj7–G6이고, 본편은 Fmaj7–G6–Em7–Am7을 두 번 돌고, 24초에 Cmaj9로 마무리해요. 효과음(키 입력, 탭, 실 연결, 카드 등장, 정답 차임, 화면 전환)은 화면 시점(`out/events.json`)에 맞춰 넣었어요.
  - 소리는 직접 들어 보지 못했어요. 스펙트로그램과 음량 곡선으로만 확인했어요. 최종 음량은 약 −15.6 LUFS, 최대 −2.3 dBFS예요.
  - 음악이 마음에 안 들면 무음판에 다른 곡을 깔면 돼요.

## 고치는 방법

1. `소스/main.js`의 타임라인(초 단위)과 `소스/index.html`의 문구를 고쳐요.
2. 효과음 시점을 뽑아요: `node tools/render.cjs --events`
3. 음악을 다시 만들어요: `~/.cache/weave-tools/venv/bin/python tools/music.py`
4. 확인용 정지 화면을 찍어요(`out/stills/`에 저장): `node tools/render.cjs --stills 3,8.9,12.6`
5. 완성본을 찍어요(약 2분 30초): `node tools/render.cjs --fps 60 --jobs 10 --blur --audio out/bgm.wav --out out/weave_intro.mp4`

실행 환경은 `~/.cache/weave-tools`예요. 여기에 node의 playwright-core·gsap, ffmpeg(`bin/ffmpeg`), 파이썬 venv(numpy, scipy, Pillow, python-pptx, imageio-ffmpeg)가 들어 있어요. Chromium은 `~/.cache/ms-playwright/chromium_headless_shell-1243`을 써요.

## 참고한 영상 (2026-10-29 확인, YouTube)

| 영상 | 참고한 점 |
| --- | --- |
| Google, "Pixel 10 With Magic Cue \| Answers" (0:31) https://www.youtube.com/watch?v=Dniq4Vfbrbs | 문제를 말 대신 대화 말풍선으로 보여 줘요. 추천 칩 하나를 크게 띄우고, 손가락으로 눌러요 |
| Samsung, "Introducing Galaxy S26 Ultra \| Galaxy AI" (3:32) https://www.youtube.com/watch?v=2gYqEi8-am4 | 2:43 Now Nudge, 3:03 Now Brief 챕터. 라벤더 그라데이션과 떠 있는 휴대폰 |
| Apple, "Apple Intelligence: Screenshots Become Calendar Events" (0:11) https://www.youtube.com/watch?v=B93UVj8MaWo | 앱 사이를 한 번 넘나드는 장면을 11초에 담아요. AI가 일할 때 휴대폰 테두리에 빛이 돌아요 |
| Rewind AI, "Rewind for iPhone in 30 seconds" (0:31) https://www.youtube.com/watch?v=7wc7se42Hx8 | 휴대폰은 왼쪽에, 한 줄 제목은 오른쪽에 둬요. 기억 검색 광고를 30초로 끊어요 |
| Notion, "Introducing the new Notion AI" (0:57) https://www.youtube.com/watch?v=S92KX8-Hmlc | 여러 앱에서 모은 답에 출처 칩을 달아요 |
| Raycast, "New Raycast. Coming 2026" (0:39) https://www.youtube.com/watch?v=Mi173xGb0ZA | 검색창을 아주 가까이 잡고, 단계마다 앱 아이콘을 붙여 차례로 진행해요 |
| Google Design, "Introducing: Material 3 Expressive" (0:39) https://www.youtube.com/watch?v=n17dnMChX14 | UI 부품을 하나씩 크게 키워 보여 줘요 |

공통점은 질문 → 단서를 이어 답 → 쓰는 순간 → 로고 순서라는 거예요. 한 화면에 요소를 적게 두고 강조색은 하나만 쓰며, 실제 제품 UI와 빛 표현을 써요. 'AI' 하면 떠오르는 입자나 뇌 그림은 피해요.

심사에서 Magic Cue나 Now Nudge와 비교될 수 있어요. 그래서 키보드 추천 칩보다 기록을 여러 번 건너 잇는 장면(6~12초)을 중심에 뒀어요.
