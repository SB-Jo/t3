# Weave Assist 티저 제목 · 원인 진단 · 삼성 KV 조사 · 후보

**최종 선택: E · 채도 우선** (`out/teaser-vEs.png`) → 요청에 따라 같은 파일을 `0921/teaser-final-0927.png`로 복사했고, `0921/통합_claude0927_반영본.pptx`의 1번 표지 그림도 이 파일로 교체했습니다. 기존 `teaser-final.png`는 그대로입니다.

**2026-09-28 추가: EsB · 선제 알림 버튼** (`out/teaser-vEsB.png`)
- 최종본 덱 `0927_v1.pptx` 1쪽에 들어간 것은 이 그림입니다. vEs에서 휴대폰 자판 줄 실타래 버튼만 바꿨습니다.
  - 원: #CEADF0 → 같은 색조의 짙은 보라 #9565C7(OKLCH 0.60/0.15/305°)
  - 아이콘: 원래 선 그림을 흰색으로(0.25px만 두껍게)
  - 크기: 원과 아이콘을 5% 작게
- 사용자 피드백 순서
  1. 채운 아이콘 + #6B4EFF → '아이콘이 너무 커지고 파랑빛'
  2. SVG 색만 바꾼 #9359CC → '채도 약간만 낮추고 크기 아주 살짝 줄이자'
  3. 지금 판
- 버튼은 원본 `assets/teaser-ui-light.svg`의 타원(`#CEADF0`)과 31px 아이콘 그림이 그립니다. 사진에도 같은 자리에 옅은 원이 있습니다.
- `tools/make-btn-variant.py`가 재료 두 가지를 만듭니다.
  - `src/teaser-ui-light-btn.svg`: SVG 사본. 색·크기·아이콘을 바꾸고, 빛줄기 가림 타원도 같이 줄입니다.
  - `src/teaser-base-btn.png`: 사진 사본. 옛 원을 주변 자판 배경으로 지웁니다(OpenCV 인페인팅).
- vEsB는 이 둘을 씁니다(`src/teaser-candidates.html` 맨 아래 스크립트, `tools/render-teasers.cjs`의 사진 선택).
- vEs를 다시 렌더하면 `0921/teaser-final-0927.png`와 픽셀이 모두 같습니다.
- `0921/teaser-final-0927.png`는 그대로 두었습니다.

2026-09-27 작업입니다. 원본 `0921/teaser-final.png`와 `0921/assets/`는 읽기만 했습니다. 같은 사진·폰 UI·카드·로고 위에 **제목·부제·제목 뒤 음영만** 바꿔 렌더했습니다. 원본 설정(v0)을 다시 렌더한 결과는 `teaser-final.png`와 픽셀이 모두 같습니다(차이 0 / 1,573,352).

## 먼저 볼 것

| 파일 | 내용 |
| --- | --- |
| `out/compare-E-steps.png` | **2차** · E의 시작 보라를 단계별로 진하게 (제목 100% + 멀리서 본 크기) |
| `out/compare-title.png` | 1차 · 원본 + 후보 A–E 제목 부분 100% |
| `out/compare-far.png` | 1차 · 멀리서 본 크기(1/6 해상도를 2배로) |
| `out/compare-full.png` | 1차 · 전체 화면 1/2 |
| `out/teaser-*.png` | 후보별 원본 크기(1672×941) 이미지 — 고르면 그대로 교체 가능 |
| `analysis/diagnosis-v0.png` | 원본 진단 그림: 대비 3:1 미만 픽셀 · 정렬선 · 흑백 |
| `research/samsung-kv-reference.png` | 삼성 공식 KV 3종 · 자간 실측 |
| `analysis/contrast-all.json` | 후보별 글자 대비 측정값 |
| `v1/` | 2차 전달본(부제를 제목 왼쪽 끝에 맞춘 E 계열 이미지·비교 시트·README·대비 값). 설명은 `v1/_2차본_안내.md` |

## 결론

- **서체와 굵기는 문제가 아닙니다.** Samsung Sharp Sans Bold는 삼성 공식 KV의 제목과 같은 서체·굵기입니다. 사전 판매 KV의 캡 높이/x높이 비율이 1.23으로, 같은 서체 렌더의 1.22와 일치합니다.
- 어색하고 떠 보이는 느낌과 "멀리서 Weave가 안 보이는" 현상은 **색 처리·제목 뒤 음영·정렬·자간** 때문입니다(아래 1절).
- 1차 추천은 A(흰색 단색)였습니다. 이후 검토에서 **E(원본 유지 + 가로 그라데이션)**가 선택되어, 2차로 E의 시작색 단계안을 만들었습니다(4절).

## 1. 원인 진단 (원본)

1. **Weave만 어둡고 재질이 다릅니다.**
   - 보라 시작색 `#986BCB`의 상대휘도는 0.215입니다. 제목 뒤 배경 평균은 0.065라 대비가 약 2.3:1입니다.
   - 글자 내부 픽셀로 재면 3:1 미만 비율이 **Weave 20.4% · Assist 4.9% · 부제 0%**입니다. 하위 10% 대비는 Weave 2.16:1, Assist 3.48:1입니다.
   - 흑백으로 보면 W·e가 배경에 묻히고 Assist만 남습니다(`diagnosis-v0.png` ③).
   - 위쪽 흰 하이라이트와 24° 사선 그라데이션 때문에 한 단어 안에서 밝기가 크게 바뀌어 광택 스티커처럼 보입니다. 바로 옆 Assist는 평면 흰색이라 두 단어가 다른 재질로 읽힙니다.
2. **제목 뒤 타원 음영.** 반지름 418×132px 타원(중심 불투명도 .44)이 화면 가장자리와 이어지지 않고 제목 주위에만 모여 있습니다. 그래서 사진의 빛 떨어짐보다는 글자 뒤에 깐 덩어리로 보입니다.
3. **정렬 기준이 없습니다.**
   - 왼쪽 끝: 제목 x=1072, 부제 x=1095 (23px 차이)
   - 중심: 제목 1350, 부제 1312
   - 왼쪽 정렬도 가운데 정렬도 아니어서 제목과 부제가 한 덩어리(락업)로 묶이지 않습니다. 편집 기록을 보면 부제 위치를 눈으로 몇 px씩 여러 번 옮겼습니다.
4. **자간이 공식 KV보다 좁습니다.**
   - 원본은 −3.8px(−0.041em)입니다.
   - 사전 판매 KV의 "Galaxy S26 Series"를 같은 서체로 재현해 x높이 대비 잉크 전체 폭을 비교했습니다: 공식 KV 14.03–14.15, 자간 0 렌더 14.17, 원본 자간 렌더 13.10.
   - 공식 KV는 자간 0과 1% 이내이고, 원본 자간은 약 8% 좁습니다. 좁은 자간은 멀리서 글자끼리 붙어 보이게 합니다.
5. **부제 서체 계열이 다릅니다.** 부제는 Noto Sans KR입니다. 삼성 한국 사이트 공통 CSS는 한글에 `SamsungOneKorean`을 쓰고(26곳), `"Samsung Sharp Sans", "SamsungOneKorean"` 조합도 선언합니다. 영향은 작습니다.

## 2. 조사 — 삼성 공식 KV의 제목 처리

| KV | 관찰 |
| --- | --- |
| Galaxy Unpacked 2026 초대장 | Sharp Sans Bold, 흰색 단색. 날짜 줄은 작고 가는 굵기로, 제목 왼쪽 끝에 맞춤 |
| Galaxy S26 Ultra 공개 무대 화면 | 제목 Bold, 아래 "Galaxy AI" Regular. 글자는 연보라 단색(사진 측정 `#F1E2FC` 근사). 그라데이션은 별 아이콘에만. 가운데 정렬 |
| 갤럭시 S26 시리즈 사전 판매 KV | "Galaxy S26 Series" Bold, "Galaxy AI" Regular + 그라데이션 별 아이콘, 한글 "사전판매"는 굵게. 전부 단색, 가운데 정렬. 자간은 기본(0)과 1% 이내 |

여기서 뽑은 공통 규칙과 이번 작업에 적용한 방식은 다음과 같습니다.

1. **워드마크는 단색, 그라데이션은 아이콘에만.** 티저 오른쪽 아래 Galaxy AI 로고가 이미 그라데이션 별을 갖고 있습니다.
2. **위계는 색보다 굵기·크기로 만듭니다**(Bold 제품명 / Regular 보조 줄). → 후보 C
3. **자간은 기본에 가깝게.** → 후보 A–D는 −0.02em
4. **제목과 보조 줄은 한 기준에 맞춥니다**(왼쪽 또는 가운데). → A–C는 왼쪽, D는 가운데. E는 3차 요청으로 원본 위치를 유지

**출처** (확인일 2026-09-27, `research/crops`의 이미지는 아래 기사 이미지에서 잘라낸 것)
- Samsung Global Newsroom, "[Invitation] Galaxy Unpacked February 2026: The Next AI Phone Makes Your Life Easier" — https://news.samsung.com/global/invitation-galaxy-unpacked-february-2026-the-next-ai-phone-makes-your-life-easier
- Samsung Global Newsroom, "Samsung Unveils Galaxy S26 Series: The Most Intuitive Galaxy AI Phone Yet" — https://news.samsung.com/global/samsung-unveils-galaxy-s26-series-the-most-intuitive-galaxy-ai-phone-yet
- 삼성전자 뉴스룸, "삼성전자, '갤럭시 S26 시리즈' 사전 판매 시작" — https://news.samsung.com/kr/%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90-%EA%B0%A4%EB%9F%AD%EC%8B%9C-s26-%EC%8B%9C%EB%A6%AC%EC%A6%88-%EC%82%AC%EC%A0%84-%ED%8C%90%EB%A7%A4-%EC%8B%9C%EC%9E%91
- samsung.com 한국 사이트 공통 CSS — https://www.samsung.com/sec/static/_css/common.css
- Samsung Developers, "Font": "The SamsungOne font provides a consistent voice to our wide range of products." — https://developer.samsung.com/design-system/font
- Sharp Type, "Samsung Sharp Sans" — https://www.sharptype.co/news/samsung-sharp-sans
  - **원문을 열지 못했습니다**(HTTP 429·보안 검사).
  - 검색 결과 요약에서는 삼성의 브랜딩·옥외광고·방송용 서체로 소개됩니다.
  - 장표 등에 인용하려면 원문 확인이 필요합니다.

## 3. 후보 (1차)

**A–D 공통 설정**
- 제목: Sharp Sans Bold 88px, 자간 −0.02em, 단색
  - 폭 553px로 원본 557px과 거의 같아서, 폰과의 간격과 오른쪽 여백이 그대로입니다.
  - 기준선(y≈194)도 원본과 같습니다.
- 부제: SamsungOne Korean 500 28px
- 음영: 타원 대신 오른쪽 위 모서리 비네트. 폰 가장자리와 떠 있는 카드에는 닿지 않습니다.
- 자간을 공식 KV처럼 0으로 하려면 85px로 줄이면 같은 폭이 됩니다.

| 후보 | 바꾼 점 | Weave 3:1 미만 | Weave 하위 10% | Assist 3:1 미만 |
| --- | --- | --- | --- | --- |
| 원본 | — | 20.4% | 2.16:1 | 4.9% |
| A · 흰색 단색 | 두 단어 모두 흰색 | 0% | 6.81:1 | 0% |
| B · Weave 연보라 단색 | Weave `#DDD2FF` | 0% | 4.78:1 | 0% |
| C · Bold + Regular | Assist를 Regular로 | 0% | 6.81:1 | 0% |
| D · 가운데 정렬 | 제목·부제 중심축 x≈1350 | 0% | 6.80:1 | 0% |
| E · 최소 변경 | 원본 크기·자간·위치·음영·부제 유지. Weave만 가로 그라데이션(`#D2C3FF`→흰색, 상단 하이라이트 제거). 부제는 3차에서 원본 위치로 되돌림 | 6.6% | 3.28:1 | 4.9% |

대비 측정 방법: 글자 내부 픽셀마다, 최종 이미지의 글자 색과 같은 위치에서 제목을 뺀 배경(음영 포함) 색의 WCAG 대비를 계산했습니다. 글자 그림자 효과는 배경에 넣지 않았으므로 보수적인 값입니다(`tools/contrast.py`).

## 4. E 시작색 단계 (2차 요청)

> "그라데이션이 왼→오인 느낌인거지? 근데 왼쪽에서도 보라색이 잘 안보이는데, 기존 티저 보라색과 지금 보라색 사이 느낌의 채도정도로 시작을 좀만 더 진하게"

- E의 그라데이션은 **왼쪽(W) → 오른쪽 흰색 가로 방향**입니다. 정지점은 0% 시작색, 45% 중간색, 100% 흰색입니다.
- 시작색은 E의 `#D2C3FF`에서 원본의 `#986BCB` 쪽으로 **OKLab(지각 균일 색공간)**에서 보간했습니다. 중간색은 이전 E와 같은 규칙(시작색에서 흰색 쪽으로 40%)으로 맞췄습니다.
- 이전 E(`teaser-vE.png`)는 그대로 두었습니다.

| 안 | 시작색 | 밝기 L / 채도 C (OKLCH) | Weave 3:1 미만 | Weave 하위 10% |
| --- | --- | --- | --- | --- |
| E · 이전 | `#D2C3FF` | .850 / .084 | 6.6% | 3.28:1 |
| E35 | `#BDA4ED` | .767 / .106 | 13.8% | 2.56:1 |
| **E50 · 요청안(중간)** | `#B597E5` | .732 / .115 | 15.5% | 2.30:1 |
| E65 | `#AC8ADD` | .697 / .124 | 17.4% | 2.05:1 |
| E · 채도 우선 | `#BE9CFA` | ≈.76 / ≈.135 | 14.4% | 2.47:1 |
| 원본 | `#986BCB` (사선 + 하이라이트) | .614 / .146 | 20.4% | 2.16:1 |

- 보라를 진하게 할수록 W의 저대비 비율이 원본 쪽으로 올라갑니다. E50은 이전 E와 원본의 중간쯤입니다.
- 채도와 밝기는 따로 조절할 수 있습니다. "채도 우선"은 채도를 E50보다 높이면서 밝기는 덜 낮춘 안이라, 보라가 더 선명하면서 저대비 비율은 E50보다 낮습니다.
- E65의 하위 10% 대비가 원본보다 낮은 이유가 있습니다. 원본은 글자 윗부분을 흰 하이라이트로 밝혔지만, E는 W 전체가 시작색이기 때문입니다.

## 4-1. 부제 위치 (3차 요청)

> "부제 (흩어진 기억..) 위치를 원본과 좀 맞춰줄래? 지금 계속 왼쪽으로가고있어"

- E 계열(E, E35, E50, E65, 채도 우선)의 부제를 원본 위치(제목 기준 left 23px · top 92.83px, 잉크 x 1095–1530)로 되돌렸습니다.
- 검증: E 계열은 원본과 **Weave 글자 영역(x 1072–1369, y 126–195)에서만** 다르고, 부제를 포함한 나머지 픽셀은 원본과 모두 같습니다.
- A–D(1차 후보)는 각 안의 정렬 방식(A–C 왼쪽, D 가운데)을 그대로 두었습니다.
- 이전 전달본(부제를 제목 왼쪽 끝에 맞춘 E 계열)은 `v1/`에 있습니다.

**측정 보정 (3차):** 단어 상자(줄 상자)가 아래로 부제 윗부분(y 215–222)과 겹쳐, 부제 픽셀 일부가 Weave·Assist로 집계되고 있었습니다. 부제 상자 위에서 잘라 다시 쟀고, 수치가 0.1–1%p 바뀌었습니다(원본 Weave 3:1 미만 19.4% → 20.4%). 안들 사이의 순서와 결론은 같습니다. 이 문서의 표는 모두 보정 후 값입니다.

## 5. 이번에 넣지 않은 것

- **Medium 굵기:** 이전에 폐기한 안입니다(`assets/IMAGE-EDIT-NOTES.md`).
- **SamsungOne Latin 제목:** v16에서 시도했고, 최종은 Sharp Sans Bold로 정했습니다.
- **실타래 아이콘을 제목 옆에 두는 방식(Galaxy AI 별 아이콘처럼):**
  - v2에서 Weave 옆 위첨자로 넣었다가 v3에서 뺐습니다.
  - 오른쪽 아래 Galaxy AI 로고에 이미 그라데이션 별이 있어, 넣으면 아이콘이 둘이 됩니다.

## 6. 폴더 구성 · 다시 만들기

- `src/teaser-candidates.html` — 원본 `assets/teaser-typography.html`과 같은 레이어 구성입니다. `?v=` 값으로 안을 고릅니다(v0, vA–vD, vE, vE35, vE50, vE65, vEs).
- `tools/render-teasers.cjs` — 원본 v19 렌더러와 같은 합성 방식입니다.
  - 사진 베이스 + 1× 레이어 + 4× 작은 글자 레이어를 합칩니다.
  - v0는 `teaser-final.png`와 픽셀 비교까지 합니다.
- `tools/contrast.py` — 대비 측정
- `tools/make-sheets.py` — 비교 시트·진단 그림
- `tools/make-research.py` — 조사 시트

```bash
node tools/render-teasers.cjs v0 vA vB vC vD vE vE35 vE50 vE65 vEs   # playwright-core·sharp 필요 (NM 환경변수로 node_modules 경로 지정)
python tools/contrast.py
python tools/make-sheets.py
python tools/make-research.py
```

`analysis/`의 `bg-*.png`(제목을 뺀 배경), `headline-*.png`(제목만), `boxes-*.json`(글자 영역)은 대비 측정용 중간 파일이라, 렌더러를 다시 실행하면 새로 만들어집니다.
