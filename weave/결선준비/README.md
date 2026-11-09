# Weave Assist · 결선 준비

예선 최종 제출본(2026-09-29)에서 결선 작업을 시작하는 폴더예요. 예전 작업 폴더 `weave/final/0921/`은 하나도 고치지 않았고, 필요한 것만 이름을 정리해서 복사해 왔어요. 회차별 백업(v1~v14, backups), 렌더 비교, 중간 시안은 원래 자리에만 있어요.

| 폴더 | 내용 |
| --- | --- |
| `01_최종제출본/` | 제출한 그대로예요. **고치지 마세요.** `Weave_제출본.pptx·pdf`, `app-demo.gif`(10MB 제한판), `pngs/p01~p19`, `seamless/` |
| `02_PPT/` | `Weave_결선.pptx`: 결선 작업본(제출본 사본)이에요. 내보내기를 돌리면 PDF와 `weave_png/`가 여기 생겨요 |
| `03_지침·기획/` | 구성안(final), 제안서 양식, **디자인_규칙.md**, 진행상황 판단, 구현 파이프라인 설계, 출처 검증, 구현 재설계안, 만화 스토리보드, 덱 수정기록(1~14차), `발표자노트/제출본_발표자노트.md`(제출본에서 뽑은 노트) |
| `04_동영상·데모/` | 앱 데모 녹화 `데모_검색·카톡·통화.mp4`, 같은 녹화의 GIF `녹화_통화·검색·카톡.gif`(16쪽 GIF의 재료), `앱데모_20fps원본.gif` |
| `05_아이콘/` | 바로 넣어 쓰는 아이콘이에요. 앱, 갤럭시앱(캘린더·파란 @ 이메일·갤러리·전화), 실타래, 손(터치 표시), 브랜드(Galaxy AI·Samsung 워드마크) |
| `06_에셋/` | 표지 티저, 인물(4·6~8쪽, 19쪽 멤버), 6~8쪽 배경 장면, 2쪽 만화, 앱 화면, 참고자료(팀 사진·Nudge·자판 등), 글꼴 |
| `07_소스/` | 장표 원본 HTML·렌더·도구예요. 파일끼리 상대 경로로 이어져 있으니 **안쪽 배치는 바꾸지 마세요** |
| `08_인트로영상/` | 결선 모션그래픽 영상 v18(118초, `Weave_모션그래픽.mp4`)·소스·음악 라이선스·참고 영상 목록(그 폴더의 README) |
| `09_HowItWorks/` | `장표5/`: How it Works 빌더(지금 쓰는 판), `리서치/`, `논문스터디/` |
| `10_표지영상/` | 표지 반복 영상 `표지_루프.mp4`, 포스터, 소스 |
| `11_중간본/` | 중간본 덱 빌드 `build_deck.py`, 쪽별 PNG, `한눈에.png`, `문구_변경목록.md`. 결과는 `02_PPT/Weave_결선_중간본.pptx` |
| `12_설문/` | 소비자 설문 결과(휴대폰 번호를 뺀 CSV와 xlsx) |

## 저장소에 두는 것 (2026-11-06)

저장소에는 지금 쓰는 판만 둬요. 아래는 `.gitignore`에 있어서 작업 컴퓨터에만 남아요.

| 작업 컴퓨터에만 있는 것 | 내용 |
| --- | --- |
| `weave/final/` | 예선 작업 폴더(제출본은 `01_최종제출본/`) |
| `08_인트로영상/이전판/`, `10_표지영상/이전판/` | 지난 판 영상 |
| `08_인트로영상/*_무음.mp4`, `08_인트로영상/배경음악/*.wav`, `08_인트로영상/소스/assets/img/trio/` | 다시 만들 수 있는 파일(무음판은 완성본에서, wav는 `tools/music.py`로, 끝 장면 그림은 `tools/trio.cjs`로) |
| `09_HowItWorks/장표/` ~ `장표4/`, `장표5/out/` | 지난 판 How it Works, 빌드 결과 |
| `Argon/` | 다른 안으로 만든 덱과 스크립트 |
| `07_소스/slides/comic/`, `07_소스/slides/p68/` | 예전 2쪽과 6~8쪽 원본(`p68/scenario.css·js`는 5쪽이 쓰므로 저장소에 둬요) |

## 이름을 바꾼 파일

| 지금 | 원래 |
| --- | --- |
| `01_최종제출본/Weave_제출본.pptx·pdf` | `added_0926/0927_data/weave_png/final_0928/0927_v1.pptx·pdf` |
| `01_최종제출본/app-demo.gif` | `final_0928/p09_app-demo.gif` |
| `02_PPT/Weave_결선.pptx` | 위 pptx의 사본 |
| `03_지침·기획/구성안_슈퍼루키PPT(final).md` | `added_0926/슈퍼루키 PPT구성안 (final).md` |
| `03_지침·기획/진행상황_판단.md` 외 2개 | `claude_0927/01_~03_*.md` |
| `03_지침·기획/구현_재설계안.md` | `added_0926/research-proposal-v1/implementation-redesign.md` |
| `03_지침·기획/덱_수정기록(1~14차).md` | `claude_0927/deck-0927v1/README.md` (안의 경로는 옛 폴더 기준) |
| `04_동영상·데모/데모_*.mp4` | `0927_data/demo_*.mp4` |
| `04_동영상·데모/녹화_통화·검색·카톡.gif` | `weave_png/Demo1·2·3.gif` |
| `04_동영상·데모/앱데모_20fps원본.gif` | `weave_png/p09_app-demo.gif` |
| `07_소스/` | `claude_0927/{assets,pages,out,tools}` + `deck-0927v1/{comic,p05,p68,demo,touch,characters,refs,assets,tools}` → `slides/`, `claude-teasers` → `teaser/`, `members_codex` → `members/` |

## 07_소스 안내

| 경로 | 쪽 | 내용 |
| --- | --- | --- |
| `teaser/` | 1쪽 | 표지 티저(vEsB) 렌더 소스와 필요한 원본(삼성 글꼴, UI SVG, 사진) |
| `slides/comic/` | 2쪽 | 만화 `index.html`과 revision CSS들. `render-claude.cjs`를 돌리면 `out/overview-comic.png`가 나와요(작업 컴퓨터에만 있어요) |
| `slides/characters/` | 4쪽 | 인물(성빈·지현)과 생성 프롬프트 |
| `slides/p05/` | 5쪽 | SOLUTION |
| `slides/p68/` | 6~8쪽 | USER SCENARIO(`scenario.css/js`, 인물·배경 장면·잘라 쓴 화면). 저장소에는 `scenario.css/js`만 있어요 |
| `pages/` | 9·17·18쪽 | HOW IT WORKS(`page-07-pipeline.html`), Q&A(`page-15-qna.html`), 용어(`page-16-glossary.html`). 렌더 결과는 `out/` |
| `slides/demo/`, `slides/tools/make_demo_gif.py` | 16쪽 | App Demo GIF(입력은 `04_동영상·데모`의 녹화 GIF) |
| `members/` | 19쪽 | Members HTML·인물 |
| `slides/touch/` | | 터치 표시(손 + 보라 선) 만들기 |
| `slides/tools/` | | `export_png.py`(PowerPoint로 PNG·PDF·seamless 내보내기, 대상은 `02_PPT/Weave_결선.pptx`), `ppt_export.ps1`, `seams.py`, `header.py`(칩·제목·부제 규격), `inspect_slide.py`, `textmeasure.py`. `참고_회차스크립트/`에는 예선 1~14차 적용 스크립트가 있어요(옛 경로 기준이라 참고용) |
| `tools/` | | `render.cjs`(HTML → PNG·그래픽 층), `render_layers.cjs`, `check_fit.cjs`, `export_pdf.cjs` 등. `참고_옛덱전용/`은 0921 덱 전용이에요 |

- 옮긴 위치에 맞게 경로를 고쳤어요(글꼴, 덱, 데모 GIF, 손 아이콘).
- HTML·CSS·JS 안의 상대 경로 159개가 모두 실제 파일을 가리키는지 확인했어요.
- 10~15쪽은 팀이 만든 장표라 따로 원본이 없어요. pptx에서 바로 고치면 돼요.

## 실행 환경

- 도구는 `~/.cache/weave-tools`에 모아 뒀어요(재부팅해도 남음): node `playwright-core`·`gsap`, `bin/ffmpeg`, 파이썬 venv(numpy, scipy, Pillow, python-pptx, imageio-ffmpeg).
- Chromium은 `~/.cache/ms-playwright/chromium_headless_shell-1243`을 써요. 이제 따로 라이브러리를 깔지 않아도 돌아가요.
- 예선 때 스크립트 중 일부는 아직 `NODE_PATH=/tmp/claude-weave-0927/...`를 가리켜요. 돌리기 전에 위 경로로 바꿔야 해요.
