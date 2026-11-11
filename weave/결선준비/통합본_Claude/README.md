# Weave 통합본 (Claude, 2026-11-11)

인트로, 모션그래픽, 솔루션과 How it Works, 뒷부분, Appendix를 한 덱으로 합친 판이에요.

| 파일 | 내용 |
| --- | --- |
| `Weave_통합본_Claude.pptx` | 통합 덱 61장(본 발표 41장, Appendix 16장, 제안 장표 3장, 교체 전 1장) |
| `Weave_통합본_Claude_미리보기.mp4` | 본 발표 41장을 처음부터 끝까지 말하며 넘긴 영상(낭독, 자막) |
| `제안장표_미리보기.mp4` | 제안 장표 두 장을 말하며 넘긴 영상 |
| `대본.md` | 장마다 말할 글과 영상에서 잰 시간, 줄이는 순서, 가져오면서 바꾼 글 |
| `한눈에.jpg` | 61장을 한 장에 모은 그림 |
| `assets/` | 마무리 사진 세 장(CC0), 아웃트로 덱에서 가져온 그림. 출처는 `assets/CREDITS.md` |

## 덱 차례

| 쪽 | 묶음 | 어디서 왔나 |
| --- | --- | --- |
| 1 | 표지 | 우리 중간본의 표지(표지 영상 v8)에 인트로 덱 1쪽 노트 |
| 2~12 | 인트로 | jjun-0824/t3 `Weave_결선_중간본_도입부수정.pptx` 2~12쪽을 화면, 효과, 노트 그대로 |
| 13 | 잇는 장 | 새로 그림(인트로 덱 13쪽 자리, 노트 문장은 그대로) |
| 14 | 모션그래픽 | 우리 중간본의 영상 장(v23) |
| 15~31 | 솔루션 3장, How it Works 14장 | `../09_HowItWorks/장표5_claude` 그대로 |
| 32~34 | 기대효과 세 장 | WIWLEE/t3-2 `Weave_BI_아웃트로_통합_1110_v7.pptx` 1~3쪽의 내용을 같은 엔진으로 다시 그림 |
| 35 | 비즈니스 임팩트 | 같은 덱 4쪽 |
| 36 | 기존 기능과의 비교 | 새로 그림 |
| 37 | Why Now · Why Samsung 연표 | 같은 덱 5쪽의 연표 내용 그대로 |
| 38~40 | 마무리 세 장 | 같은 덱 6~8쪽의 문구를 사진 위에 |
| 41 | 끝 화면 | 같은 덱 9쪽 |
| 42~57 | Appendix | How it Works Appendix 15장, 마무리 사진 출처 1장 |
| 58~60 | 제안 장표 | 가름 장, 설문의 저장 채널 그림, 새 연표 |
| 61 | 교체 전 | 인트로 덱 13쪽 |

## 다시 만들기

```
~/.cache/weave-tools/venv/bin/python make.py --png     # 덱 + out/png (PowerPoint로 렌더)
~/.cache/weave-tools/venv/bin/python talk.py           # 낭독 → 덱 → 녹화 → 낭독, 자막, 모션그래픽 소리를 얹은 영상
~/.cache/weave-tools/venv/bin/python talk.py --proposal
~/.cache/weave-tools/venv/bin/python trim.py           # 줄인 대본 안의 시간을 같은 목소리로 잼
~/.cache/weave-tools/venv/bin/python doc.py            # 대본.md
```

- `원본/`에 두 덱을 받아 둬야 해요(저장소에는 올리지 않아요).
  - https://github.com/jjun-0824/t3/blob/claude/pull-push-permissions-eacsir/weave/결선준비/02_PPT/Weave_결선_중간본_도입부수정.pptx
  - https://github.com/WIWLEE/t3-2/blob/main/Weave_BI_아웃트로_통합_1110_v7.pptx
- 바탕 덱은 `../02_PPT/Weave_결선_중간본.pptx`예요. 읽기만 하고, 표지와 모션그래픽 장, 장 틀을 빌려 써요.
- `slides_new.py`에 새로 그린 장이 있어요(잇는 장, 뒷부분 열 장, 제안 장표). 그리는 엔진과 낭독 도구는 `../09_HowItWorks/장표5_claude` 것을 그대로 써요.
- `foreign.py`는 다른 덱의 장을 도형, 그림, 전환, 효과째로 옮겨요.
- 낭독은 이 컴퓨터 안에서만 만들어요(Supertonic 3, 목소리 F2F1_70, 속도 1.15).
