# 결선 중간본 덱 (2026-11-02)

원본 `02_PPT/Weave_결선.pptx`는 그대로 두고, 새 파일 **`02_PPT/Weave_결선_중간본.pptx`**를 조립해요.

## 구성 (35장)

| 구분 | 장 | 내용 |
|---|---|---|
| 본편 | 1 | **표지 (반복 영상)**: `10_표지영상/표지_루프.mp4`. 자동 재생, 끝나면 반복 |
| 본편 | 2–3 | Motivation, Pain Points (원본 3·4쪽 그대로) |
| 본편 | 4 | **Solution**: 새 시나리오 셋(요청 자료 / 집들이 와인 / 갈색병). `07_소스/slides/p05_결선/` |
| 본편 | 5–17 | **How it Works**: 장표5 A1 덱용 13장(`09_HowItWorks/장표5/a1_deck.py`, A1에서 결과 화면 한 장만 뺌) |
| 본편 | 18–24 | Why Samsung, Why Now, 차별화, 기대효과 1~3, END (원본 그대로) |
| 부록 | 25–27 | App Demo, Q&A 2장 (원본 그대로) |
| 참고 | 28–35 | 구분 장, 이전 표지, 만화, 이전 시나리오 1~3, 이전 How it Works, 인트로 영상 79초 (발표에서 안 씀) |

## 다시 만들기

```bash
~/.cache/weave-tools/venv/bin/python build_deck.py           # 조립 → 영상 넣기(PowerPoint) → png/·한눈에.png
~/.cache/weave-tools/venv/bin/python build_deck.py --no-png
```

- 솔루션 장표는 `07_소스/slides/p05_결선/apply_solution.py`로 다시 채워요.
- How it Works는 `09_HowItWorks/장표5`의 엔진(`scene5.py`, `build5.add_steps`)으로 덱 안에 바로 그려요.
- 영상은 PowerPoint(COM)로 넣어요. 표지는 '자동 재생 + 반복', 인트로는 '자동 재생 한 번'이에요. 열려 있는 PowerPoint 창은 건드리지 않아요.

## 원본에서 바뀐 것

- 1쪽 표지: 사진 한 장 → 반복 영상. 이전 표지는 참고 구간으로 옮겼어요.
- 2쪽 만화: 참고 구간으로 옮겼어요.
- 5쪽 Solution: 시나리오를 새 셋으로 바꿨어요(바뀐 문구는 `07_소스/slides/p05_결선/` 보고 참고).
- 6~8쪽 시나리오, 9쪽 How it Works: 새 How it Works 13장으로 대체하고, 이전 장표는 참고 구간으로 옮겼어요.
- 인트로 영상 79초: 02·03 장면이 새 시나리오와 달라 참고 구간에만 넣었어요.
