# DocHop-QA 논문 심층 분석 및 발표 파이프라인·시나리오 적용안

> **분석 대상 논문**:
> 1. **`DocHop-QA: Towards Multi-Hop Reasoning over Multimodal Document Collections`** (`arXiv:2508.15851`, Jiwon Park, Seohyun Pyeon, Jinwoo Kim, Rina Carines Cabral, Yihao Ding, Soyeon Caren Han — **POSTECH**, Univ. of Sydney, UWA, Univ. of Melbourne)
> 2. **`DocHop: Benchmarking Out-of-domain Multi-hop Reasoning in Information-Dense Documents`** (`arXiv:2609.02059`, Zhuoran Yu et al. — UW-Madison, MIT, Stanford, Kookmin Univ., MIT-IBM)
> 3. **(연계 논문) `Hi-Q: Hierarchical Query Decomposition for Multi-hop Retrieval`** (**NeurIPS 2026**, POSTECH — 저장소 내 [`21_HIQ.md`](file:///home/jaeung/samsung/t3/Gauss-Embedding-V2/docs/reasoning_embed/21_HIQ.md))

---

## 1. `DocHop-QA` 논문 핵심 내용 요약

### 1.1 기존 Multi-Hop QA 벤치마크의 한계와 `DocHop-QA`의 문제의식
기존 대표적 Multi-Hop 벤치마크(`HotpotQA`, `2WikiMultihopQA`, `MuSiQue`)는 모두 세 가지 비현실적인 가정을 전제로 설계되어 있었습니다.
1. **단일 모달리티(Plain Text)**: 위키백과(Wikipedia)의 순수 텍스트 문단만 다룹니다.
2. **명시적 하이퍼링크(Explicit Gold Links)**: 문서와 문서 사이에 미리 정의된 하이퍼링크(위키 링크)가 존재하여 그 링크를 타고 이동합니다.
3. **레이아웃/시각 구조 무시**: 실제 문서에 존재하는 **표(Table), 시각 레이아웃(Visual Layout), 바운딩 박스(BBox) 위치 정보**를 전혀 활용하지 못합니다.

반면, 실제 세계의 문서 탐색(그리고 **스마트폰 온디바이스 개인 데이터 탐색**)에서는 **문서/앱 간에 명시적 하이퍼링크가 전혀 없고(Unlinked)**, 단서가 **비정형 텍스트(메신저·회의록)**와 **구조화된 표·시각 이미지(갤러리 사진 OCR·문서 장표)**에 파편화되어 있습니다. **`DocHop-QA`**는 바로 이 **"링크가 없는 다중 문서·다중 모달리티(텍스트 + 표 + 레이아웃 BBox) 환경에서의 Multi-Hop 추론"**을 최초로 정식화한 논문입니다.

---

### 1.2 `DocHop-QA`의 두 가지 Multi-Hop 추론 구조: `Fan-Hop` vs. `Chain-Hop`

논문은 총 11,359개의 QA 쌍을 구축하면서 멀티홉 추론을 크게 두 가지 패러다임으로 분류합니다.

| 구분 | **Fan-Hop (Paragraph-Oriented, 75.3%)** | **Chain-Hop (Table/Multimodal-Oriented, 24.7%)** |
| :--- | :--- | :--- |
| **구조적 특징** | 하나의 복합 질문에 답하기 위해 링크가 없는 여러 문서에서 **의미적으로 상호보완적인 텍스트 스니펫(Problem, Solution, Mechanism, Effect 등)을 병렬·교차 수집**하여 종합 | **순차적 징검다리 추론(Sequential Step-by-Step Bridge)**으로, **Hop 1에서 찾은 텍스트 스니펫(`Snippet 2`)이 징검다리가 되어 다른 모달리티(표/시각 레이아웃, `Snippet 3`)를 선택·연결** |
| **논리 스캐폴드** | `PSM` (`Problem → Solution → Mechanism`), `PSR` (`Problem → Solution → Effect`), `ME` (`Mechanism → Effect`), `FF`/`SS` (비교 추론) 등 8종 | **`PST` (`Problem → Solution → Table`)**, **`TS`/`TSL` (`Table → Studytopic → Limitation`)** |
| **우리 발표와의 접점** | 여러 앱에 흩어진 정황 증거들을 의미 기반으로 모으는 추론 | **우리 발표의 핵심 2-Hop 시나리오 (`텍스트 앱 단서 → 갤러리/문서함 시각·표 단서`)와 100% 일치!** |

---

### 1.3 `DocHop-QA`의 핵심 파이프라인 메커니즘 (Appendix A.3 분석)

논문 본문 및 Appendix A.3(`Logical Answer Chain Construction`)에 기술된 파이프라인에서 **우리 발표의 아키텍처(`How It Works`)와 시나리오에 즉시 적용할 수 있는 3대 핵심 원리**가 등장합니다.

#### ① 하이브리드 검색 공식: `0.2 × Lexical (TF-IDF) + 0.8 × Dense Semantic Embedding`
- `DocHop-QA`는 질문과 후보 스니펫 간의 연관도를 계산할 때 다음 하이브리드 공식을 사용합니다:
  $$\text{Score}(Q, S) = 0.2 \times \text{Lexical}_{\text{TF-IDF}}(Q, S) + 0.8 \times \text{Dense}_{\text{Embedding}}(Q, S)$$
- **의미**: 정확한 고유명사/용어 매칭을 잡아주는 **Lexical(0.2)**과 문맥·논리적 역할을 잡아주는 **Dense Embedding(0.8)**을 결합합니다. 이는 우리 발표 장표의 **Hybrid Search (BM25 + Dense Embedding)** 설계가 학술적으로도 가장 표준적이고 강력한 구성임을 직접 뒷받침합니다.

#### ② `PST (Problem → Solution → Table)` 체인의 **Snippet-to-Snippet 징검다리 검색**
- `DocHop-QA`의 `PST` 체인 파이프라인(Appendix A.3.2)은 다음과 같이 동작합니다:
  1. **Hop 1 (`Question → Snippet 1 & Snippet 2 [Text]`)**: 사용자의 질문으로부터 문제(`Snippet 1`)와 **해결책 텍스트 문단(`Snippet 2`)**을 하이브리드 검색으로 먼저 찾습니다.
  2. **Hop 2 (`Snippet 2 [Text Bridge] → Snippet 3 [Table/Visual]`)**: 최종 정답이 들어 있는 **표/시각 자료(`Snippet 3`)는 원래 질문(`Question`)으로 직접 검색해서 찾는 것이 아니라, Hop 1에서 찾은 중간 단서(`Snippet 2`)와의 의미 유사도(Semantic Similarity)를 기준으로 검색**합니다!
- **왜 중요한가?**: 사용자가 질문할 때는 최종 표나 사진에 적힌 구체적인 기술 명칭/상표명을 모른 채 질문합니다. 따라서 **`Question`으로 바로 `Snippet 3(표/사진)`을 찾으면 실패**하고, 반드시 **Hop 1에서 찾은 중간 텍스트 단서(`Snippet 2`)를 쿼리 삼아 `Snippet 3(표/사진)`으로 건너가야만(Hop) 정답을 찾을 수 있습니다.**

#### ③ 4단계 태스크 설계와 **BBox 공간 위치 그라운딩 (Task 1 & Task 2)**
- `DocHop-QA`는 단순히 정답 텍스트만 생성하는 것이 아니라, **문서 이미지(OCR 레이아웃) 상에서 정답 엔티티가 위치한 정확한 Bounding Box (`BBox`, Task 1) 및 구조 태그(`XML`, Task 2)를 지목**하도록 요구합니다.
- 실험 결과(Table 2), 최신 멀티모달 LLM(Gemini 1.5 Pro, GPT-4o, Qwen2.5-VL 등)조차 단순 텍스트 추출(Task 4)에 비해 **실제 이미지 상의 BBox 위치를 짚어내는 멀티홉 추론(Task 1)에서 성능이 크게 하락**하며, 이를 해결하려면 정교한 멀티홉 검색 파이프라인이 필수적임을 입증했습니다.

---

### 1.4 동명의 최신 논문 `DocHop (arXiv:2609.02059)`의 핵심 포인트 보완
- 함께 검색되는 **`DocHop: Benchmarking Out-of-domain Multi-hop Reasoning in Information-Dense Documents`** (`arXiv:2609.02059`) 역시 매우 유사한 핵심 통찰을 제시합니다:
  - **"간접 지칭 엔티티 해소(Indirect Entity Resolution across Narrative & Visuals)"**: 질문은 타겟 엔티티의 이름을 직접 부르지 않고, **서술형 텍스트(Narrative Text)에 정의된 조건/사건**으로만 지칭합니다.
  - 모델은 반드시 **Hop 1(텍스트 구간)에서 그 조건에 해당하는 구체적 엔티티/단서를 먼저 특정**한 뒤, **Hop 2(시각 차트/표 구간)로 넘어가 해당 값을 추출**해야 합니다.

---

## 2. 우리 발표 파이프라인(`How It Works`)에 적용할 3대 핵심 인사이트

발표의 `How It Works`(12장 시퀀스)를 설명할 때, `DocHop-QA`의 파이프라인 개념을 차용하면 심사위원에게 **"왜 이 구조가 진짜 Multi-Hop이고 왜 Reasoning Embedding이 핵심인지"**를 훨씬 설득력 있게 전달할 수 있습니다.

1. **Unlinked Cross-App Hop (링크 없는 앱 간 추론)**
   - 위키백과와 달리 스마트폰 내 **카톡, 삼성노트, 갤러리, 내 파일 사이에는 하이퍼링크(Link)가 전혀 없습니다.**
   - `DocHop-QA`가 링크 없는 문서 집합을 의미적 단서(Bridge)로 연결하듯, 온디바이스 에이전트는 **앱 간 경계를 넘어 중간 스니펫(`Snippet 2`)을 의미적으로 연결**합니다.
2. **Snippet-to-Snippet Cross-Modal Bridge (`Text Snippet → Visual/Table Snippet`)**
   - 원래 질문(`Query`)만으로는 갤러리 사진(OCR)이나 문서 표(Table)를 바로 찾을 수 없습니다.
   - **Hop 1**에서 텍스트 앱(카톡/노트)의 **중간 단서 스니펫(`Snippet 2`)**을 Reasoning Embedding으로 먼저 찾고, **`Snippet 2`의 구체화된 단서를 징검다리 삼아 Hop 2의 시각/표 스니펫(`Snippet 3`)을 검색**합니다 (`DocHop-QA`의 `PST` 체인 구조).
3. **BBox Spatial Grounding (`DocHop-QA` Task 1 ↔ 우리 발표 Slide 12 `ocr`)**
   - Hop 2에서 갤러리 사진이나 문서 이미지를 찾은 뒤, 단순히 사진을 보여주는 데 그치지 않고 **와인 라벨이나 문서 표의 정답 영역에 정확한 Bounding Box(`BBox`)를 하이라이트**하여 근거를 제시합니다 (현재 우리 발표의 `12. ocr` 슬라이드 연출과 완벽히 부합!).

---

## 3. 우리 발표 시나리오(안 A: `UX 1`, `UX 2`, `UX 3`)에의 구체적 적용안

사용자님께서 말씀하신 **"시간 연산 같은 복잡한 군더더기는 빼고, 임베딩으로 핵심 중간 단서(Bridge)를 찾아 건너가는 직관적인 구조"**를 유지하면서, `DocHop-QA`의 **`PST (Problem → Solution → Table/Visual)`** 및 **`Cross-Modal Chain-Hop`** 패턴을 우리 3대 시나리오(`UX 1`, `UX 2`, `UX 3`)에 적용한 설계입니다.

---

### 📌 적용 1: `UX 1` (비즈니스) — **`DocHop-QA`의 `PST (Problem → Solution → Table)` 체인을 그대로 적용!**

기존 `UX 1`("A사 미팅 때 요청받은 자료")을 `DocHop-QA`의 대표 체인인 **`Problem → Solution → Table/Slide (PST)`** 구조로 구체화하면, 비즈니스 시나리오의 설득력이 극대화됩니다.

* **사용자 질문 (`Query`)**:
  > *"지난번 **A사 미팅 때 박 팀장님이 문제 삼았던 보안 이슈 해결책** 정리된 **표(장표)**가 어느 파일에 있지?"*
* **왜 1-Hop으로는 못 찾는가?**:
  - 내 파일함의 기술 문서(`Cloud_Arch_v2.pdf`) 안에는 `'A사'`나 `'박 팀장'`이라는 단어가 전혀 없습니다. 질문으로 문서함을 바로 뒤지면 못 찾습니다.
* **Hop 1 (`Question → Snippet 2 [회의록 텍스트: Problem & Solution Bridge]`)**:
  - **삼성노트 회의록**에 적힌 텍스트:
    > *"[10/12 회의] 박 팀장 지적사항(**Problem**): 망분리 환경에서 외부 API 호출 시 키 유출 우려 제기 → 우리 측 대응(**Solution**): **온프레미스 KMS 프록시 게이트웨이** 구조로 우회 적용하기로 합의"*
  - **Reasoning Embedding의 역할**: 질문의 *"문제 삼았던 보안 이슈 해결책"*이라는 추상적 요구를 회의록 속 **`Problem → Solution` 논리 구조(`DocHop-QA`의 `PST` 스캐폴드)**와 매칭하여, 중간 단서인 **`"온프레미스 KMS 프록시 게이트웨이"`(`Snippet 2`)**를 정확히 포착!
* **Hop 2 (`Snippet 2 [Text Bridge] → Snippet 3 [문서 내 Table/장표]`)**:
  - Hop 1에서 얻은 구체적 해결책 단서(`"온프레미스 KMS 프록시 게이트웨이"`)와의 **Snippet-to-Snippet 유사도**를 통해, 내 파일함 `Cloud_Arch_v2.pdf` 14페이지의 **`[Table 3] 온프레미스 KMS 프록시 구간별 암호화 명세표`(`Snippet 3`)**를 정확히 찾아냄!

---

### 📌 적용 2: `UX 2` (일상/메인 데모) — **집들이 화이트 와인 (`Unlinked Text Bridge → Visual BBox OCR`)**

시간 연산이나 일정 변경 같은 복잡한 요소를 모두 제거하고, **`DocHop-QA`의 "링크 없는 텍스트 단서(`Snippet 2`) → 시각 레이아웃 BBox(`Snippet 3`)" 징검다리**만 깔끔하게 남긴 메인 데모 시나리오입니다.

* **사용자 질문 (`Query`)**:
  > *"지은이네 **집들이** 때 **해산물 요리랑 같이 마셨던 산뜻한 화이트 와인** 이름이 뭐였지?"*
  *(또는 심플하게: "지은이네 집들이 때 마신 화이트 와인 이름이 뭐였지?")*
* **왜 1-Hop으로는 못 찾는가?**:
  - 카톡에는 `'집들이'`나 `'와인'`이라는 단어가 없고, 갤러리 사진에는 `'지은이네'`나 `'집들이'`라는 태그가 없습니다 (두 앱은 **Unlinked** 상태).
* **Hop 1 (`Question → Snippet 2 [카톡 대화 텍스트: Situational & Pairing Bridge]`)**:
  - **카톡 대화 (`10/14`)**:
    > *"지은: 언니 어제 이삿짐 박스 드디어 다 풀었어! 휴지랑 세제 사 오지 말고 몸만 와~ 저녁에 **광어 카르파초** 해 둘게 ㅎㅎ"*
  - **Reasoning Embedding의 역할**:
    - `'집들이'`라는 단어가 전혀 없어도 `"이삿짐 박스 다 풀었어 + 휴지/세제 사 오지 말고 놀러 와"`라는 묘사에서 **'집들이 초대의 암묵적 상황(Situational Bridge)'**을 추론해 `10/14` 대화를 찾아냅니다.
    - 동시에 이 대화에서 **`10/14` 날짜 단서**와 함께 당일 메인 요리 단서(**`광어 카르파초 / 해산물`**)를 중간 스니펫(`Snippet 2`)으로 획득합니다!
* **Hop 2 (`Snippet 2 [Text Bridge] → Snippet 3 [갤러리 사진 BBox OCR]`)**:
  - Hop 1에서 확보한 단서(`10/14` + `광어 카르파초 식탁`)를 징검다리 삼아 **갤러리 앱(`10/14`)**을 탐색합니다.
  - 식탁 사진 속 와인병 라벨을 **OCR 및 BBox Grounding (`DocHop-QA` Task 1 방식)**으로 읽어내어 **`"Cloudy Bay Sauvignon Blanc (Crisp citrus notes, pairs ideally with raw seafood)"`** 영역에 바운딩 박스를 치고 최종 와인 이름을 응답합니다!

---

### 📌 적용 3: `UX 3` (여행/쇼핑) — **출장길 면세점 갈색병 (`Text/Schedule Bridge → Receipt Table Row`)**

* **사용자 질문 (`Query`)**:
  > *"지난번 **해외 출장길 면세점**에서 엄마 사드린 **갈색병 화장품** 정확한 제품명이 뭐였지?"*
* **Hop 1 (`Question → Snippet 2 [일정/문자 텍스트 Bridge]`)**:
  - 캘린더/항공권 문자에서 `'해외 출장'`에 해당하는 출국 일자 및 공항 단서(**`11/05 인천공항 T2 출국`**) 확보.
* **Hop 2 (`Snippet 2 → Snippet 3 [모바일 영수증 Table / 사진 BBox]`)**:
  - `11/05` 면세점 모바일 구매 내역 **표(Table)**에는 `'갈색병'`이라는 별명이 없고 공식 영문명만 적혀 있으나, 일상 별명(`갈색병 에센스`)과 공식 제품 속성(`Estée Lauder Advanced Night Repair Synchronized Multi-Recovery Complex`) 간의 **개념적 브릿지 매칭**으로 영수증 표의 해당 행(Row)을 정확히 짚어냅니다.

---

## 4. 요약: `DocHop-QA`에서 가져올 핵심 메시지 한 줄 정리

> **`DocHop-QA`의 핵심 통찰**:
> *"현실의 멀티홉 QA는 하이퍼링크가 없는(Unlinked) 텍스트와 표·이미지 사이에서 일어난다. 최종 정답이 담긴 표나 사진(`Snippet 3`)은 질문(`Query`)으로 직접 찾아지지 않으며, 반드시 **Hop 1에서 Reasoning Embedding으로 찾은 중간 텍스트 단서(`Snippet 2`)를 징검다리(Bridge) 삼아 Hop 2의 시각·표 영역(BBox)으로 건너가야만** 해결할 수 있다."*
