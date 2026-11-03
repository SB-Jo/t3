# Reasoning Embedding 학술 서베이 분석 및 와인 시나리오(Option A) 추론 고도화 설계안

> **작성 배경 (사용자 핵심 지적 반영)**
> - **사용자 질문**: *"카톡에 '이사 기념' 같은 거는 그냥 일반 Embedding도 찾을 수 있는 거 아냐? 단서로 이어질 만한 중간 추론이 맞아? Reasoning Embedding의 다양한 서베이/관련 논문들을 쭉 읽고, 이러한 reasoning을 와인 시나리오에 적용할 수 있는지 생각해보자."*
> - **핵심 진단**: **사용자님의 지적이 학술적으로 100% 정확합니다.**
>   - `'집들이'` ↔ `'이사 기념 우리 집 저녁'`, `'화이트 와인'` ↔ `'소비뇽 블랑(Sauvignon Blanc)'` 수준의 연결은 **Level 2 (의미·의역·다국어 유사성, Semantic / Paraphrase Match)**에 해당합니다.
>   - 이는 **일반 Dense Embedding(STS / MS-MARCO 학습 모델)이 이미 잘 푸는 영역**이므로, 발표 청중이나 심사위원이 *"저건 굳이 Reasoning Embedding이 아니라 일반 임베딩으로도 검색되는 것 아닌가?"*라고 반문할 수 있는 치명적 약점이 됩니다.

---

## 1. 서베이·논문 10편 종합: 일반 Embedding vs. Reasoning Embedding의 학술적 경계

[`Gauss-Embedding-V2/docs/reasoning_embed/`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/README.md)에 정리된 주요 논문·서베이([`00_RESEARCH_REVIEW.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/00_RESEARCH_REVIEW.md), [`01_BRIGHT.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/01_BRIGHT.md), [`02_REASONIR.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/02_REASONIR.md), [`03_REASONEMBED.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/03_REASONEMBED.md), [`04_LREM.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/04_LREM.md), [`05_LASER.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/05_LASER.md), [`07_MEMORA.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/07_MEMORA.md), [`09_RIR_SURVEY.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/09_RIR_SURVEY.md), [`reader/rir_survey_ko.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/reader/rir_survey_ko.md), [`21_HIQ.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/21_HIQ.md))를 종합하면, 정보 검색의 관련성(Relevance)은 명확히 **3단계**로 구분됩니다.

### 1.1 검색 관련성의 3단계 (BRIGHT & ACL 2026 RIR Survey)

| 단계 | 명칭 | 정의 및 예시 | 해결 가능한 모델 |
|---|---|---|---|
| **Level 1** | **어휘 연결 (Lexical Match)** | 질의와 문서가 동일한 표면 단어를 공유 (`"집들이"` ↔ `"집들이 선물 목록"`) | **BM25 / 키워드 검색** |
| **Level 2** | **의미·의역 연결 (Semantic / Paraphrase Match)** | 단어는 다르지만 같은 개념·동의어·번역어를 가리킴 (`"집들이"` ↔ `"이사 기념 저녁 초대"`, `"화이트"` ↔ `"Blanc"`) | **일반 Dense Embedding** (기존 Bi-encoder, STS·일반 QA 학습) |
| **Level 3** | **추론 집약적 연결 (Reasoning-Intensive Relevance, RIR)** | 표면 어휘나 단순 유의어 유사성이 아니라, **조건·제약 충족, 상태/일정 변경(취소 vs 확정), 역할·방향성 구분, 인과·속성 적용, 또는 다중 홉의 브릿지 유용성(Bridge Utility)**을 통해 연결됨 | **Reasoning Embedding** (ReasonIR, ReasonEmbed, LREM, LaSER, Gauss RIR) |

> [!IMPORTANT]
> **ACL 2026 RIR Survey ([`rir_survey_ko.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/reader/rir_survey_ko.md) §1, §4.2.2)의 핵심 정의:**
> - *"추론 집약적 검색(RIR)은 질의와 근거 사이의 관련성이 의미적 유사성(semantic similarity)보다 **겉으로 드러나지 않은 잠재적 추론 관계(latent inferential links)**를 통해 결정되는 검색 환경이다."*
> - *"RIR에서 **Positive 문서는 실제로 질의에 답하는 데 도움이 되는(조건을 충족하거나 중간 브릿지를 제공하는) 근거**여야 하고, **Hard Negative 문서는 질의와 어휘나 의미가 훨씬 더 비슷하더라도(높은 표면/주제 유사도) 논리적 조건·상태가 어긋나 문제 해결에 도움이 되지 않는 문서**여야 한다."*

---

### 1.2 논문들이 제시하는 5대 Reasoning 유형과 개인화 기기 검색(Personal Memory)에서의 대응

서베이([`rir_survey_ko.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/reader/rir_survey_ko.md) 표 2·표 4)와 주요 논문([`00_RESEARCH_REVIEW.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/00_RESEARCH_REVIEW.md) §2)에서 정의한 추론 유형을 **온디바이스 개인 기록 검색(메시지·캘린더·노트·갤러리)**으로 옮기면 다음 **5가지 진짜 추론(Level 3)**이 도출됩니다.

| # | RIR 추론 유형 | 관련 대표 논문 / 벤치마크 | 일반 Embedding이 실패하는 이유 (Hard Negative 함정) | Reasoning Embedding이 수행하는 중간 추론 (Latent Bridge) |
|---|---|---|---|---|
| **R1** | **상태·일정 변경 및 부정/예외 추론**<br>(State Update & Negation) | **LongMemEval** (ICLR 2025), **ReasonEmbed** ([`03_REASONEMBED.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/03_REASONEMBED.md)), **BetaE** ([`11_EMBEDDING_GEOMETRY.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/11_EMBEDDING_GEOMETRY.md)) | `"지은이네 집들이 날짜"`라는 단어가 그대로 들어 있는 **취소·연기 전 원래 약속 메시지**가 코사인 유사도 1등을 차지함 | 취소·연기된 기록(Negative)을 배제하고, **조건 변경 후 최종 성사된 일정 기록**(Positive)을 유효한 시간 앵커로 선택 |
| **R2** | **역할·방향성·주체 구분 추론**<br>(Role & Perspective Disambiguation) | **ImpliRet / BESPOKE** ([`rir_survey_ko.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/reader/rir_survey_ko.md) §3.1.1), **ReasonIR** ([`02_REASONIR.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/02_REASONIR.md)) | `"집들이 와인"` 키워드가 다 들어 있는 **내가 호스트였던 작년 집들이**나 **내가 선물로 사 간 레드 와인** 대화를 1등으로 뽑음 | 질의의 주체·역할(`"친구네 집들이에서 호스트가 내놓은"`, `"내가 추천받은"`)과 문서 내 화자·행위 방향이 일치하는 기록만 연결 |
| **R3** | **목적·상황·감각 제약 → 속성 연역/유추**<br>(Constraint-to-Property Deduction) | **LREM** (WWW 2026, [`04_LREM.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/04_LREM.md)), **BRIGHT** ([`01_BRIGHT.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/01_BRIGHT.md)), **R2MED** | 사용자는 **상황·제약·감각**(`"해산물 요리랑 어울렸던"`, `"술 약한 친구도 마신 가벼운"`, `"기내 반입 안 걸리는"`)으로 묻지만, 기록은 **구체 속성·성분·규격**(`"산도 높은 소비뇽 블랑"`, `"도수 5.5% 모스카토"`, `"80ml 앰플"`)으로 적혀 있음 | 질의의 암묵적 제약 조건을 만족하는 구체적 속성·해결 수단(`구멍 안 뚫는 선반 → 무타공 압축봉`, `해산물 페어링·산뜻함 → 시트러스 산도의 소비뇽 블랑`)을 잠재 공간에서 연결 |
| **R4** | **암묵적 전제·원리 기반 인과 추론**<br>(Causal & Prerequisite Reasoning) | **BRIGHT**, **ReasonEmbed** (`ReMixer` 위상 정렬 예시, [`03_REASONEMBED.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/03_REASONEMBED.md) §2) | 표면적인 주제어만 겹치는 일반 후기나 단순 목록 문서를 가져오고, 문제 해결의 전제 조건이 담긴 문서를 놓침 | 현상·요청이 성립하기 위한 **선행 조건·원인**(`"식탁 배송 완료 후 모임"`, `"법무팀 독소조항 수정 완료본"`)을 담은 근거를 우선 회수 |
| **R5** | **다중 홉 브릿지 유용성 추론**<br>(Multi-Hop Bridge Utility & Granularity) | **MDR** ([`11_EMBEDDING_GEOMETRY.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/11_EMBEDDING_GEOMETRY.md) §4), **Hi-Q** (NeurIPS 2026, [`21_HIQ.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/21_HIQ.md)), **LaSER** ([`05_LASER.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/05_LASER.md)) | 복합 질의(`"집들이 때 마신 화이트 와인"`)를 그대로 던지면 `"집들이"`만 맞거나 `"와인"`만 맞는 파편 문서(Distractor)에 점수가 분산됨 | 현재 질의에서 **당장 답을 주진 않더라도 다음 홉 검색을 가능하게 해주는 결정적 매개 변수(Bridge Variable: 날짜·장소·식당명·코드명)**를 가진 문서를 Hop 1에서 정확히 회수 |

---

## 2. 왜 현재 와인 시나리오(`A1`)가 "일반 임베딩도 할 수 있어 보이는가?" (냉정한 진단)

현재 발표 자료의 와인 시나리오(`"지은이네 집들이 때 마신 화이트 와인 이름이 뭐였지?"`) 구성을 위 학술 기준으로 해부해 보면 다음과 같습니다.

| 구간 | 현재 시나리오의 연결 | 학술적 분류 | 청중의 의구심 (약점) |
|---|---|---|---|
| **Hop 1**<br>(질의 → 카톡) | `"지은이네 집들이"` ↔ `"지은: 이사 기념으로 10월 14일 토요일에 우리 집에서 저녁 먹자!"` | **Level 2 (단순 의역/유의어)** | `"집들이"`와 `"이사 기념 우리 집 저녁"`은 일반 Dense Embedding(심지어 멀티링구얼 E5, BGE, 기존 Gemma Embedding)에서도 코사인 유사도가 매우 높게 나옴. **일반 임베딩이 왜 실패하는지 설득력이 약함.** |
| **Hop 2**<br>(10/14 + 화이트 와인 → 갤러리 OCR) | `"화이트 와인"` ↔ `"Cloudy Bay Sauvignon Blanc"` | **Level 2 (다국어/도메인 유의어)** + 시간 필터(`10/14`) | 날짜(`10/14`)는 메타데이터 필터가 해주고, `"화이트 와인"` ↔ `"Sauvignon Blanc"`은 와인 도메인 단어 매칭처럼 보임. |

즉, **현재 와인 시나리오는 Multi-Hop(카톡 → 갤러리) 구조와 On-Device 완결성은 완벽하지만, 정작 그 안의 Embedding이 수행하는 역할이 Level 2(의역 매칭)에 머물러 있어서 "Reasoning Embedding만의 차별성"이 약해 보이는 것**입니다.

---

## 3. 와인 시나리오(`A1`)에 "진짜 Reasoning Embedding (Level 3)"을 이식하는 3가지 설계안

와인 시나리오의 직관성(누구나 1초 만에 이해하는 일상성)과 12장 슬라이드 흐름(`fail` → `hybrid` → `hop1` → `pivot` → `hop2` → `ocr` → `result`)은 **그대로 유지**하면서, **일반 Embedding은 구조적으로 틀리고(Hard Negative에 속고), Reasoning Embedding만 맞히는 Level 3 추론**을 넣는 3가지 고도화 방향입니다.

---

### 설계안 W-1 (가장 추천 ⭐): **[R1 상태·일정 변경 추론 + R3 감각·페어링 제약 추론]** 결합형

> **핵심 아이디어**: 일상 카톡에서 가장 흔히 일어나는 **"원래 부르기로 한 날(취소/연기) vs 실제로 모인 날(변경 확정)"**의 함정(Hard Negative)을 Hop 1에 배치하고, Hop 2에서는 그날 찍힌 사진/기록 중 **"상황·음식 페어링·감각 조건"**을 만족하는 와인을 추론하게 만듭니다.

#### ① 사용자 질의 (그대로 직관적임)
> **"지은이네 집들이 때 해산물 요리랑 같이 마셨던 산뜻한 와인 이름이 뭐였지?"**
> *(또는 기존처럼 짧게 **"지은이네 집들이 때 다 같이 마신 화이트 와인 이름이 뭐였지?"**로 유지해도 됨!)*

#### ② Hop 1 (카톡 대화 검색): 왜 일반 Embedding은 틀리고 Reasoning Embedding은 맞히는가?
기기에 지은이와의 카톡 메시지가 **2개** 존재합니다:

| 후보 메시지 | 카톡 본문 내용 | 어휘·단순 의미 유사도 (일반 Dense Embedding) | 추론적 관련성 (Reasoning Embedding) |
|---|---|---|---|
| **후보 A (Hard Negative — 함정)** | `지은 (10/02)`: *"얘들아 **10월 7일 토요일**에 우리 집 **집들이** 겸 **화이트 와인** 파티 하자! 기대돼 🍷"* → `지은 (10/05)`: *"미안 거실 식탁 배송이 밀려서 이번 주는 취소해야 할 듯 ㅠㅠ"* | **`"집들이"`, `"화이트 와인"` 단어가 정확히 일치하여 일반 Embedding 1위 (0.89)** → **잘못된 날짜(`10/07`) 추출!** | 뒷문맥에서 **일정이 취소(Negation/State Change)되었으므로 실제 모임 날짜가 아님**을 추론하여 배제 |
| **후보 B (True Positive — 진짜 단서)** | `지은 (10/10)`: *"식탁 드디어 도착! 미뤄졌던 거 **10월 14일 토요일** 저녁에 우리 집에서 다시 모이자!"* | `"집들이"`, `"와인"` 단어가 없어서 일반 Embedding 순위 밀림 (0.61) | **선행 제약(식탁 도착)이 해결되어 실제로 성사된 모임 확정 일정(`10/14`)**임을 추론하여 **1위로 회수!** |

- **발표 임팩트 (`fail` & `hop1` 슬라이드)**:
  - 심사위원이 보자마자 **"아! 일반 임베딩이나 키워드 검색은 `'집들이'`, `'화이트 와인'`이 그대로 적힌 10월 7일(취소된 약속) 카톡을 1등으로 가져오겠구나! 반면 Reasoning Embedding은 '미뤄졌다가 실제로 성사된 날짜(10월 14일)'라는 상태 변화와 맥락을 추론해서 진짜 브릿지 단서를 찾는구나!"**라고 100% 납득하게 됩니다.
  - 이는 [`00_RESEARCH_REVIEW.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/00_RESEARCH_REVIEW.md) §2와 [`03_REASONEMBED.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/03_REASONEMBED.md) §6에서 강조한 **"취소와 변경 구분, 조건 충족 근거 선택"**의 완벽한 실사례입니다!

#### ③ Hop 2 (10월 14일 갤러리·노트 검색): 단순 번역(`화이트=Blanc`)을 넘어선 제약·속성 추론
10월 14일 저녁에 찍힌 와인 라벨/테이스팅 기록도 **단순히 사진 1장만 있는 게 아니라 2개의 후보**가 있거나, 라벨의 속성 추론이 들어갑니다:
- **후보 1 (Hard Negative)**: 호스트가 디저트 때 잠깐 꺼낸 달콤한 스파클링/레드 와인 (또는 선물용으로 사 갔으나 안 딴 와인)
- **후보 2 (True Positive)**: `Cloudy Bay Sauvignon Blanc` (라벨/노트 정보: *"Crisp acidity, citrus & passionfruit notes, pairs with seafood"* — **산뜻한 산도와 시트러스 향, 해산물 요리와 페어링되는 드라이 화이트 와인**)
- **Reasoning Embedding의 역할**: 단순히 `'블랑 = 화이트'`라는 단어 번역을 넘어, 사용자의 암묵적 조건(**"메인 해산물 요리와 곁들인 산뜻한 화이트 와인"**)을 라벨/노트의 **구체적 속성(Sauvignon Blanc, Crisp citrus acidity)**과 연역적(Deductive)으로 연결합니다 (**LREM / BRIGHT 방식**).

---

### 설계안 W-2: **[R4 암묵적 상황·원인 추론 + R5 다중 홉 브릿지 유용성 추론]** 결합형

> **핵심 아이디어**: 카톡에 `'이사'`나 `'집들이'`라는 유사어조차 직접 쓰이지 않고, **집들이를 구성하는 구체적 행동·사건(암묵적 추론 사슬)**으로만 적혀 있는 경우입니다 (ACL 2026 RIR Survey의 **ImpliRet / BESPOKE** 스타일).

- **사용자 질의**: *"지은이네 집들이 때 마신 화이트 와인 이름이 뭐였지?"*
- **함정 메시지 (Hard Negative)**:
  - `카톡 A`: *"지은아 저번에 너네 **집들이** 때 마신 **와인** 너무 맛있더라 다음에 또 마시자!"* (날짜 정보 없이 사후에 감상만 말한 메시지 — 표면 유사도는 0.92로 1등이지만 **검색을 이어갈 날짜 브릿지(Bridge Utility)가 없음!**)
- **진짜 단서 메시지 (True Positive)**:
  - `카톡 B (10/14)`: *"지은: 새로 산 6인용 식탁 세팅 끝! 오면서 휴지랑 세제 사 오지 말고 그냥 몸만 와~ 저녁 7시에 보자"*
- **왜 진짜 Reasoning Embedding인가?**:
  1. **브릿지 유용성 추론 (Bridge Utility — MDR / Hi-Q)**: `카톡 A`는 `'집들이'`, `'와인'`이 다 들어 있어 일반 임베딩 점수가 가장 높지만, 정작 질의를 해결할 **시간 앵커(언제 모였는지)**가 없는 **무용한 문서(Uninformative Overlap)**입니다.
  2. **암묵적 상황 추론 (ImpliRet)**: `카톡 B`는 `'집들이'`나 `'이사'`라는 단어가 전혀 없지만, **"새 식탁 세팅 + 휴지·세제(집들이 대표 선물) 사 오지 말라는 맥락"**으로부터 이것이 바로 **집들이 당일(`10/14`) 초대 메시지**임을 추론해 냅니다!

---

### 설계안 W-3: **[R2 역할·방향성 구분 추론 + R1 조건 위반 배제]** 결합형

> **핵심 아이디어**: 내 폰 안에 `'집들이'`와 `'와인'` 기록이 여러 개 섞여 있을 때, **주체·역할(내가 연 집들이 vs 지은이가 연 집들이, 내가 사 간 와인 vs 그날 다 같이 마신 와인)**을 구분하는 추론입니다.

- **함정 기록 (Hard Negative)**:
  - `메모/카톡 A`: *"우리 집 집들이 때 지은이가 사 온 레드 와인 리스트"* (`'지은'`, `'집들이'`, `'와인'` 어휘가 100% 겹쳐 BM25와 일반 임베딩 모두 1위로 오탐!)
- **진짜 단서 기록 (True Positive)**:
  - `카톡 B (10/14)`: *"지은: 우리 새집 첫 손님들이네! 오늘 저녁 메뉴가 광어 카르파초니까 내가 거기에 딱 맞는 칠링된 한 병 준비해 둘게"*

---

## 4. 한눈에 비교: 기존 와인 시나리오 vs. 고도화된 와인 시나리오 (`W-1` + `W-2` 장점 결합 권장안)

가장 설득력이 높은 방법은 **`W-1(취소된 일정 vs 성사된 일정)`**과 **`W-2(휴지·세제/새 식탁 등 진짜 집들이 맥락 추론 + 날짜 없는 사후 감상 카톡 배제)`**의 핵심을 결합하는 것입니다. 이렇게 하면 **"그냥 일반 임베딩으로도 되는 것 아니냐?"는 반론을 원천 차단**할 수 있습니다.

| 비교 항목 | 기존 와인 시나리오 (수정 전) | **고도화된 와인 시나리오 (RIR 논문 반영안)** |
|---|---|---|
| **질의** | `"지은이네 집들이 때 마신 화이트 와인 이름이 뭐였지?"` | `"지은이네 집들이 때 마신 화이트 와인 이름이 뭐였지?"` *(질의는 그대로 짧고 직관적으로 유지!)* |
| **일반 Embedding이 속는 함정 (Hard Negative)** | 명확한 함정 예시 없이 단순히 `"집들이 = 이사 기념"`을 못 찾는다고 설명함 (설득력 약함) | **함정 1 (취소된 원래 일정)**: *"10/7(토) 우리 집 **집들이** 겸 **화이트 와인** 파티 하자!" → "식탁 배송 밀려서 취소 ㅠㅠ"*<br>**함정 2 (브릿지 없는 사후 대화)**: *"지은이네 **집들이** 때 마신 **와인** 진짜 맛있었지"* (날짜 단서 없음)<br>👉 일반 임베딩은 단어(`집들이`, `화이트 와인`)가 겹치는 이 함정들을 1위로 뽑아 **오답 날짜(`10/7`)를 짚거나 검색이 끊김!** |
| **Reasoning Embedding이 찾는 진짜 단서 (Hop 1 Positive)** | `"이사 기념으로 10월 14일 토요일에 우리 집에서 저녁 먹자!"` (단순 유의어 수준) | `10월 14일 카톡`: *"밀렸던 식탁 드디어 도착! 미뤄졌던 거 **10월 14일 토요일** 저녁에 우리 집에서 다시 모이자. 오면서 **휴지·세제** 사 오지 말고 몸만 와~"*<br>👉 `'집들이'`라는 단어가 없어도 **① 일정 연기 후 실제 성사된 상태(State Update)** + **② 휴지·세제/새 식탁이라는 암묵적 집들이 맥락(ImpliRet)** + **③ 다음 홉을 열 수 있는 날짜 브릿지(`10/14`) 보유 여부(Bridge Utility)**를 추론하여 정확히 1위로 회수! |
| **Hop 2 (갤러리·노트 추론)** | `"화이트 와인"` ↔ `"Sauvignon Blanc"` (단순 불어/영어 단어 매칭처럼 보임) | `10월 14일` 저녁 촬영된 사진들 중, 선물로 들어온 위스키/레드와인 사진을 배제하고 **해산물 테이블 위 칠링 버킷에 담긴 `Cloudy Bay Sauvignon Blanc` (`Crisp citrus & white wine notes`)**을 **상황·속성 추론(LREM/BRIGHT)**으로 연결 |
| **학술적 근거 대응** | Level 2 (STS / Paraphrase) | **Level 3 RIR 완벽 부합**:<br>- **ReasonEmbed / LongMemEval**: 취소·연기(Negation) vs 확정 일정 구분<br>- **ACL 2026 RIR Survey (ImpliRet)**: 어휘 중첩 없는 암묵적 일상 의도 추론<br>- **MDR / Hi-Q**: 다음 홉을 여는 유효 브릿지(Bridge Evidence) 선택 |

---

## 5. Option A의 나머지 두 시나리오(`UX 1`, `UX 3`)에도 동일한 Level 3 RIR 기준 적용 점검

사용자님이 선택하신 **포트폴리오 A (`UX 1: A사 미팅 요청 자료`, `UX 2: 집들이 화이트 와인`, `UX 3: 출장길 면세점 갈색병`)** 전체가 "일반 임베딩이 아닌 진짜 Reasoning Embedding"으로 일관되게 빛나도록, `UX 1`과 `UX 3`의 추론 포인트도 함께 고도화했습니다.

| 구분 | 시나리오 | 일반 Embedding이 빠지는 함정 (Hard Negative) | Reasoning Embedding의 진짜 중간 추론 (Level 3 RIR) |
|---|---|---|---|
| **UX 1**<br>(비즈니스) | **A사 미팅 때 요청받은 자료 파일**<br>*("지난번 A사 미팅 때 그쪽에서 수정해서 보내달라고 한 자료 파일 어디 있지?")* | `"A사 미팅 발표자료_최종.pdf"`처럼 제목에 `'A사'`, `'미팅'`, `'자료'`가 그대로 들어간 **초기 발표용 자료**를 1위로 가져옴 | **역할·상태·약속 추론 (R1+R4)**:<br>- **Hop 1 (캘린더+음성메모)**: 내가 발표한 자료가 아니라 상대방(박 팀장)이 **"독소조항 문구 빼고 보안 아키텍처 장표 추가해서 금요일까지 재송부해 달라"**고 요청한 **미해결 후속 과제(Action Item)**를 추론<br>- **Hop 2 (내 파일/노트)**: 파일명에 `'A사'`가 없더라도 해당 **보안 아키텍처 개정 조건이 반영된 내부 코드명 문서(`Project_Titan_Sec_v2.4.pptx`)**를 연결 |
| **UX 2**<br>(일상/메인) | **집들이 화이트 와인 (고도화판)**<br>*("지은이네 집들이 때 마신 화이트 와인 이름이 뭐였지?")* | `'집들이'`, `'화이트 와인'` 단어가 그대로 적힌 **취소된 10/7 카톡**이나 **날짜 없는 사후 안부 카톡**을 1위로 가져옴 | **일정 변경(취소→확정) + 암묵적 맥락 + 브릿지 유용성 추론 (R1+R3+R5)**:<br>- **Hop 1 (카톡)**: 식탁 배송 지연 후 **실제 성사된 10/14 모임 카톡(*"미뤄졌던 거 10/14에 보자, 휴지 사 오지 마"*)**에서 날짜(`10/14`) 앵커 획득<br>- **Hop 2 (갤러리 OCR)**: 10/14 촬영 사진 중 칠링된 화이트 와인 품종·속성(`Cloudy Bay Sauvignon Blanc`) 특정 |
| **UX 3**<br>(여행/쇼핑) | **출장길 면세점 갈색병**<br>*("작년 출장 갈 때 면세점에서 산 갈색병 뭐였지?")* | `'면세점'`, `'갈색병'` 키워드가 들어간 **예전 쇼핑 위시리스트 캡처**나 **면세점 할인 쿠폰 문자**, 혹은 출장 때 산 **위스키 갈색병**을 가져옴 | **일정 전후 관계(Numerical/Temporal) + 용량·외관 속성 추론 (R3+R5)**:<br>- **Hop 1 (캘린더/문자)**: `'작년 출장'` → 캘린더의 **출국 비행편 출발 직전 2시간 이내(시간 연산 추론)** 인천공항 제2터미널 신라면세점 결제 알림(`$142`) 특정<br>- **Hop 2 (영수증/갤러리)**: 일상 별명(`'갈색병'`)을 기내 반입 규격·갈색 앰플 외관 및 정식 제품명(`Estée Lauder Advanced Night Repair 100ml`)으로 속성 연결 |

---

## 6. 발표 슬라이드(How It Works 12장)에 반영할 핵심 수정 포인트 요약

와인 시나리오의 **슬라이드 구조(12장)는 그대로 유지**하면서 텍스트·다이어그램의 디테일만 위 RIR 논리에 맞춰 업그레이드하면 발표 설득력이 극대화됩니다.

1. **`fail` 슬라이드 (일반 검색·일반 임베딩의 한계)**:
   - 기존: 단순히 `"집들이"`, `"화이트 와인"` 키워드가 흩어져 있어서 못 찾는다고만 설명.
   - **고도화**: 일반 임베딩이 **표면 단어가 겹치는 함정 메시지(10/7 취소된 집들이 카톡, 또는 날짜 없는 사후 카톡)**를 고득점으로 잘못 가져와서 엉뚱한 날짜를 뒤지는 **구체적 실패 과정(Hard Negative 오탐)**을 명시.
2. **`hop1` 슬라이드 (카톡에서 1차 단서 확보)**:
   - 기존: `"이사 기념으로 10월 14일에 저녁 먹자"` (단순 유의어 매칭처럼 보임).
   - **고도화**:
     - ❌ **배제된 함정 카톡 (10/02)**: *"10/7 집들이 겸 화이트 와인 마시자 → 식탁 배송 밀려서 취소 ㅠㅠ"* (단어는 겹치지만 취소된 일정)
     - ✅ **Reasoning Embedding이 선택한 진짜 단서 (10/10)**: *"식탁 도착! 미뤄졌던 거 **10월 14일 토요일**에 우리 집에서 다시 모이자! 오면서 휴지·세제 사 오지 말고 몸만 와~"* (**일정 재확정 상태 + 집들이 암묵적 맥락 + 날짜 브릿지 보유**)
3. **`hop2` & `ocr` 슬라이드 (갤러리에서 2차 단서 및 와인명 확정)**:
   - `10월 14일` 저녁 촬영 사진 중 단순 레드와인/위스키 선물 사진을 걸러내고, 해산물 식탁에 놓인 화이트 와인 라벨(`Cloudy Bay Sauvignon Blanc`)의 품종·속성을 추론하여 확정.
4. **`scenarios` 슬라이드 (More Scenarios 3열 카드)**:
   - **카드 1 (`UX 1`)**: A사 미팅 때 수정 요청받은 보안 아키텍처 자료 (발표본 vs 상대방 수정 요청사항 구분 추론)
   - **카드 2 (`UX 2`)**: 지은이네 집들이 때 마신 화이트 와인 (취소된 일정 배제 및 성사된 모임 날짜·라벨 추론)
   - **카드 3 (`UX 3`)**: 작년 출장길 면세점에서 산 갈색병 (출국 직전 시간 연산 + 별명↔정식 제품명 추론)
