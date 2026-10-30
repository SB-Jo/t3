# 결선 인트로 영상 (v3, 41.6초)

발표 시작에 트는 제품 광고 느낌의 훅 영상이에요. 1920×1080·60fps, H.264 + AAC라서 PowerPoint의 삽입 → 비디오에 그대로 넣을 수 있어요.

이전판은 `이전판/v1_28초/`, `이전판/v2_40초/`에 소스·영상·음악째로 남겨 두었어요.

| 파일 | 내용 |
| --- | --- |
| `Weave_인트로_42초.mp4` | 완성본(음악·효과음 포함, 41.6초) |
| `Weave_인트로_42초_무음.mp4` | 같은 영상의 무음판 |
| `배경음악/` | `음악+효과음.wav`, `음악만.wav`, `효과음만.wav` (48kHz), 샘플 라이선스(CC0) |
| `미리보기_1초간격.jpg`, `표지_엔드카드.png` | 1초 간격 미리보기, 마지막 로고 화면 |
| `소스/` | 영상 원본(HTML·CSS·GSAP 타임라인 `main.js`, 삼성 글꼴·아이콘·사진) |
| `tools/` | `render.cjs`(프레임 → mp4), `music.py`(샘플로 음악 연주·효과음) |

## 구성 (100 BPM, 한 마디 2.4초)

| 시간 | 장면 | 화면 |
| --- | --- | --- |
| 0–9.6초 | 질문 | "그때 그 와인, 다시 사고 싶은데 / 이름이 뭐였더라?" → 기록 조각 14개가 떠오르고, "카톡이었나, 사진이었나, 캘린더였나, 메모였나…"가 1.3초 간격으로 하나씩 나오며 해당 앱 기록이 빛나요 |
| 9.6–21.6초 | 구글에서 다시 찾기 | 크롬의 구글 검색창에 "지은이네 집들이 때 먹었던 와인" 입력 → 확대해서 키보드의 Weave 아이콘 누르기 → 휴대폰이 치워지고 캘린더 → 그날 사진 → 라벨 글자 인식 → "배비치 소비뇽 블랑" → 입력하기 → 구글 쇼핑 결과(가격·오늘 도착)로 다시 살 수 있어요 |
| 21.6–28.8초 | 흩어진 기록을, 한 번에 | 휴대폰은 왼쪽, 오른쪽 위에 헤드라인 → 통화 중 위로 올려 검색 → 시트 안 카드에서 실이 뻗어 오른쪽에 큼직한 기록 카드 3장(메모·메일·카톡, 내용 포함)이 차례로 뜸 → 세 카드를 잇는 보라 점선과 'A사 시연 준비' 칩 |
| 28.8–38.4초 | 떠올리기 전에, 먼저 건네요 | 엄마 질문 강조 → 큼직한 '지금 위치(GPS)' 카드(위치 표시가 퍼짐) → '가족 단체방' 카드 → 두 실이 모여 '자동 완성 추천' 카드가 생김 → 추천이 키보드 위 Weave 시트로 날아감 → 입력하기 → 전송 → 엄마 답장 "감동이야 우리 딸!" |
| 38.4–41.6초 | 마무리 | Weave Assist 로고 · "그때 그거? Weave got it." · 한 줄 소개(v2보다 글자를 키움) → 흰 화면 |

## v2에서 바꾼 것 (2026-10-29 피드백)

- **글꼴:** 모두 삼성 계열로 바꿨어요.
  - 한글: SamsungOne Korean 400·500·700
  - 영문: SamsungOne 400·500·700
  - 로고·영문 태그: Samsung Sharp Sans Bold
  - 손글씨 질문은 보라 칩으로 바꿨어요.
  - 글꼴 파일은 samsung.com·design.samsung.com이 공개로 제공하는 웹 글꼴이에요. 출처는 `06_에셋/글꼴/SOURCES.md`에 있어요.
- **음악:** 합성음을 모두 빼고 실제 악기 녹음 샘플로 다시 연주했어요(아래 샘플).
  - 첫 두 마디는 피아노 아르페지오 독주로 시작해요.
  - 4.8초부터 피치카토 베이스·탬버린(엇박에만), 9.6초부터 부드러운 베이스드럼과 브러시 스네어가 들어와요.
  - 장면이 열릴 때는 하프 글리산도, 로고에서는 하프와 글로켄으로 마무리해요.
- **효과음:** 쉭쉭거리던 바람 소리는 전부 뺐어요. 연결·카드 등장은 하프 한 음, 정답은 글로켄, 탭·메시지는 마림바 소리를 작게 넣었어요.
- **도입:** '메모였나…'를 추가하고, 구절 간격을 1.1초에서 1.3초로 늘렸어요.
- **와인 장면:** 문구에 '다시 사고 싶은데'를 넣고, 검색 화면을 크롬 구글로 다시 그렸어요. 끝은 구글 쇼핑 결과로 마무리해요.
- **통화 장면:** 휴대폰을 왼쪽으로 옮기고, 오른쪽에 내용이 들어간 큼직한 카드 3장을 실과 점선으로 연결했어요(PPT 6쪽 모양).
- **카톡 장면:** GPS와 대화 카드를 키우고 순서를 천천히 보여 줘요(연결 → 추천 생성 → 키보드로 전달 → 누르기 → 전송 → 답장).
- **엔드 카드:** 태그 문구는 50px에서 58px로, 한 줄 소개는 28px에서 33px로 키웠어요.

소리는 직접 들어 보지 못했어요. 스펙트로그램과 음량으로만 확인했어요(약 −16.8 LUFS, 최대 −1.5 dBFS).

## 음악 샘플

VSCO 2 Community Edition(Versilian Studios)을 썼어요: https://github.com/sgossner/VSCO-2-CE
- **라이선스:** CC0 1.0 퍼블릭 도메인. 사용 제한이 없고, 출처 표기도 의무가 아니에요.
- **쓴 악기:** 업라이트 피아노(Simon Dalzell, Ivy Audio 녹음), 솔로 콘트라베이스 피치카토, 하프, 글로켄슈필, 마림바, 탬버린·콩가 탭·스네어 탭·베이스드럼
- **로컬 사본:** `~/.cache/weave-tools/samples/vsco2`

## 고치는 방법

1. `소스/main.js`의 타임라인(초 단위)과 `소스/index.html`의 문구를 고쳐요.
2. 효과음 시점을 뽑아요: `node tools/render.cjs --events` (손 위치도 함께 출력)
3. 음악을 다시 만들어요: `~/.cache/weave-tools/venv/bin/python tools/music.py`
4. 확인용 정지 화면을 찍어요(누르는 자리에 빨간 점): `node tools/render.cjs --debug --stills 13.2,19.65,35.15`
5. 완성본을 찍어요(약 3분 30초): `node tools/render.cjs --fps 60 --jobs 10 --blur --audio out/bgm.wav --out out/weave_intro.mp4`

## 참고한 영상 (2026-10-29 확인, YouTube)

| 영상 | 참고한 점 |
| --- | --- |
| Rewind AI, "Rewind for iPhone in 30 seconds" (0:31) https://www.youtube.com/watch?v=7wc7se42Hx8 | 속도·문구·음악의 기준. 한 줄 문구를 2~5초씩 띄우고, 휴대폰과 문구를 나란히 둬요 |
| Google Design, "Introducing: Material 3 Expressive" (0:39) https://www.youtube.com/watch?v=n17dnMChX14 | 카메라 움직임의 기준. UI를 크게 키웠다 줄이며 보여 줘요 |
| Google, "Pixel 10 With Magic Cue \| Answers" (0:31) https://www.youtube.com/watch?v=Dniq4Vfbrbs | 대화 말풍선으로 문제를 보여 주고, 추천 칩 하나를 크게 띄워 눌러요 |
| Samsung, "Introducing Galaxy S26 Ultra \| Galaxy AI" (3:32) https://www.youtube.com/watch?v=2gYqEi8-am4 | 2:43 Now Nudge, 3:03 Now Brief 챕터 |
| Apple, "Apple Intelligence: Screenshots Become Calendar Events" (0:11) https://www.youtube.com/watch?v=B93UVj8MaWo | AI가 일할 때 휴대폰 가장자리에 빛이 돌아요 |
| Notion, "Introducing the new Notion AI" (0:57) https://www.youtube.com/watch?v=S92KX8-Hmlc | 답에 출처 칩을 달아요 |
| Raycast, "New Raycast. Coming 2026" (0:39) https://www.youtube.com/watch?v=Mi173xGb0ZA | 단계마다 앱 아이콘을 붙여 차례로 진행해요 |
