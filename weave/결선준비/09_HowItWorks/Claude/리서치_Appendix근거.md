# Appendix 근거 리서치: PDE 논문, Apple, HippoRAG, 지도 메모 문구 점검

- 작성일은 2026-11-08이에요. 아래 URL은 모두 이날 직접 열어 확인했고, 열지 못한 곳은 "확인 못 함"으로 표시했어요. 영어 인용은 원문 그대로예요.
- 삼성 기능은 [기존 노트](../리서치/삼성_현재기술_조사.md)(2026-10-31)에서 이미 검증했어요. 여기에는 새로 확인했거나 고칠 것만 적었어요. [S1], [A1], [O4] 같은 번호는 기존 노트의 출처 번호예요.
- 신뢰도 표기는 기존 노트와 같아요: [공식] 1차 자료 / [그룹] 삼성 자회사(OST) / [학계] 논문 / [보도] 언론.

## 0. 판정 요약

| # | 확인한 것 | 판정 |
|---|---|---|
| 1 | CEUR 논문 | OST 연구진 3명이 ISWC 2025 Industry Track에 낸 3쪽 논문이에요. PDE 구조를 설명하지만 스키마와 성능 수치는 없어요 |
| 2a | "RDFox는 그래프를 완전히 materialize해 두고, 추가·삭제는 확장 DRed로 증분 처리" | **사실** |
| 2b | "분석 결과를 트리플로 KG에 저장하고, OWL RL·Datalog 온톨로지가 함의 트리플을 추가" | **사실**(표현 두 곳만 다듬으면 됨) |
| 3 | "Apple이 iOS 27에서 Spotlight semantic index로 검색·맥락 인지 강화" | **부분적으로 맞음.** 9to5Mac 기사 문장과 거의 같아요. Apple 뉴스룸에는 "Spotlight index"로 나와요 |
| 4 | "HippoRAG 오류 대부분은 NER/OpenIE(추출)에서 나온다" | **맞음**(48%+28%). 다만 가장 큰 48%는 질문 쪽 NER이고, 색인할 때 생긴 추출 오류(OpenIE)는 28%예요 |
| 5 | 삼성 현재 기능 | 기존 노트는 유효해요. 정정할 곳은 1건(PDE 논문이 있음)이에요. 10-31 이후의 새 공식 발표는 찾지 못했어요 |
| 6 | 문구 4건 | 4건 모두 바꾼 문구가 원래 문구보다 정확해요. 더 쉬운 장표 문장을 제안해요 |
| 7 | "그래프는 기록이 들어올 때, Weave는 질문이 들어올 때 잇는다" | **공정함.** '관계를 만드는 시점'을 기준으로 하면 맞아요. GraphRAG도 Indexing Time / Query Time으로 나눠요 |

## 1. CEUR 논문: "Semantic Technology in Your Pocket" [C1] [그룹]

- **서지**
  - 저자: Peter Crocker, Ian Horrocks, Yavor Nenov. 소속은 셋 모두 "Oxford Semantic Technologies, Oxford, UK"이고, OST는 2024년에 삼성이 인수한 자회사예요.
  - 수록: CEUR-WS Vol-4085 "Joint Proceedings of Industry, Doctoral Consortium, Posters and Demos of the 24th International Semantic Web Conference (ISWC-C 2025)"(나라, 2025-11-02~06)의 **Industry Track** 섹션, 17–19쪽 [C2]. 본문은 3쪽이에요.
- 저자가 모두 OST라서 **삼성전자 명의의 자료는 아니에요.**

### 1-1. 임원용 요약 (장표 문체)
1. PDE는 여러 앱과 시스템의 데이터를 모아 AI로 분석하고, 그 결과를 '개인 지식 그래프'에 쌓는 기기 안 엔진이다.
2. 그래프의 사실에 규칙(온톨로지)을 적용해, 그로부터 따라 나오는 사실까지 미리 계산해 넣어 둔다.
3. 데이터가 추가되거나 지워지면, 영향을 받는 결론만 골라 다시 계산한다.
4. 저장, 추론, 조회가 모두 기기 안에서 일어난다(RDFox 안드로이드 빌드).
5. 이렇게 쌓은 지식으로 Now Brief, 개인화, 추천, 검색을 지원한다.

### 1-2. 원문 근거
- **무엇을 모으나:** "The PDE collects data from a wide range of sources including multiple apps and system software (see Figure 1). This can include everything from structured data through to text and (possibly moving) images." (§2)
- **어떻게 분석하나(논문에서 LLM이 나오는 곳은 여기뿐):** "The PDE analyses this data using appropriate AI technologies including machine learning and LLMs." (§2)
- **어떻게 저장하나**
  - "The result of this analysis is stored in the user’s personal knowledge graph where it is augmented with triples entailed by the ontology." (§2)
  - "RDFox ® stores data in the form of an RDF graph and an ontology in the form of OWL RL axioms and Datalog rules; it provides a high-performance incremental reasoning engine and a SPARQL query interface." (§1)
- **어떻게 추론하나**
  - "The reasoning engine exploits modern multi-core architecture to parallelise reasoning and incrementally maintains a fully materialised graph that extends the RDF data with triples entailed by the ontology" (§3)
  - "Materialisation effectively means repeatedly answering queries corresponding to the bodies of axioms/rules and adding the answer triples back into the graph" (§3)
- **어떻게 갱신하나**
  - "RDFox ® implements incremental addition and retraction using a novel extension of the Delete rederive algorithm (DRED)." (§3)
  - 개선점: "In RDFox®, deletion is interleaved with checks to determine if facts still hold via alternative derivations, which avoids excessive over-deletion and hence improves the efficiency of incremental materialisation." (§3)
- **기기 안 처리:** "The PDE uses an android build of the RDFox ® system to store, reason over and query the graph. Importantly, all this happens on the device." (§2)
- **쓰임:** "This is used to provide services to client applications supporting features such as personalisation and recommendation. For example, the PDE supports the Now Brief function on the S25 which provides a personalised briefing of selected content that updates throughout the day." (§2)
- **그림 1**(그림 속 글자를 제가 읽어 옮긴 것)
  - Data Collector: "MX Division"과 앱 아이콘
  - Data Analyzer: Statistics, Description logic, Language AI, Vision AI / Structured, Semi-structured, Unstructured
  - Personal Knowledge Graph: Ontology Design, Knowledge Management. Data Analyzer와는 양방향 화살표로 이어져요.
  - Personalized Experience: Mobile Experience, **Search**, Recommendation. 그래프에서 "Knowledge" 화살표가 들어오고, 반대 방향으로 "Feedback" 화살표가 나가요.
- **일정:** "Development of the PDE was carried out in 2024 and the PDE was deployed on Samsung’s flagship S25 smartphone platform in 2025." (§4)

### 1-3. 논문에 없는 것
- **기기 수치:** 용량, 지연 시간, 메모리, 그래프 크기 숫자가 하나도 없어요. 규모를 말하는 표현은 "millions of users now carrying a semantic reasoning engine in their pocket"뿐이고, 이 문장 앞에도 "almost certainly"가 붙어 있어요. "real-time answers to complex queries"는 요구 사항으로만 나와요.
- **구체적인 질의 예시:** 사용자 질문이나 SPARQL 예시가 없어요. 사례는 Now Brief와 그림 1의 Search·Recommendation 화면뿐이에요.
- **임베딩·벡터·semantic search:** 논문 전체에서 0회 나와요. "semantic"은 시맨틱 웹(RDF·OWL)이라는 뜻으로만 쓰였어요. 이건 언급이 없다는 뜻이지, PDE가 이 기술을 안 쓴다는 증거는 아니에요.
- **PDE의 한계:** 따로 적지 않았어요. 한계에 관한 문장은 일반론 두 개뿐이에요.
  - 기존 DRed에 대해: "eager over-deletion and the subsequent rederivation of facts can be very inefficient, particularly when facts participate in long inference chains"
  - 질의에 대해: "even with all entailed facts materialised efficient query answering can still be challenging"
- **앞으로의 계획:** "this is only the beginning"이라며 다른 휴대폰과 "a wide range of different devices"로 넓히겠다고 해요(§4).
- **스키마:** 온톨로지의 클래스, 관계, 규칙 내용은 여전히 공개되지 않았어요. 기존 노트 §2의 결론이 그대로 유지돼요.

## 2. 지도 메모의 PDE 주장 두 개

- **(a) "RDFox는 그래프를 완전히 materialize해 두고, 추가·삭제는 확장 DRed 알고리즘으로 증분 처리한다" → 사실.**
  - "완전히 materialize" = "incrementally maintains a fully materialised graph"
  - "확장 DRed" = "incremental addition and retraction using a novel extension of the Delete rederive algorithm (DRED)" (둘 다 §3, 1-2 인용 참고)
- **(b) "분석 결과를 RDF 트리플로 개인 KG에 저장하고, OWL RL 공리와 Datalog 규칙으로 된 온톨로지가 함의 트리플을 추가한다" → 사실이고, 원문과 거의 같아요.** 다듬을 곳은 두 군데예요.
  - ① 원문은 '트리플로' 대신 "stored in the user’s personal knowledge graph"라고 써요. 다만 같은 논문에 "An RDF graph is just a set of subject, predicate, object triples"라는 문장이 있어서 '트리플로'라고 써도 무리는 없어요.
  - ② 트리플을 더하는 주체는 온톨로지가 아니라 추론 엔진이에요. 엔진이 규칙 본문에 맞는 답을 계산해 그래프에 되넣어요("adding the answer triples back into the graph").
  - 덧붙여, "OWL RL axioms and Datalog rules"는 PDE가 쓰는 KG 시스템(RDFox)의 형식을 설명한 문장이에요. PDE 온톨로지에 실제로 어떤 규칙이 들어 있는지는 공개되지 않았어요.

## 3. Apple: "iOS 27에서 Apple Intelligence가 Spotlight의 semantic index로 검색과 맥락 인지를 강화" → 부분적으로 맞음

- **메모 문장은 언론 기사의 문장이에요.** 9to5Mac(2026-06-08) [M1]의 "Apple Intelligence will use Spotlight’s semantic index to improve search and power awareness."와 거의 같아요.
- **Apple 뉴스룸의 WWDC26 보도자료 3건(2026-06-08)에는 "semantic index"라는 말이 없어요** [A3][A4][A5]. Apple이 실제로 쓴 문장은 다음과 같아요.
  - [A3] "Additionally, Siri AI uses the system orchestrator to tap into core capabilities like the Spotlight index and App Toolbox, which work entirely on device to keep users in control of their data." 출시 기사 [A1]에도 같은 문장이 있어요.
  - [A3] "And personal context understanding extends to third-party apps when developers integrate with Spotlight."
  - [A4] "In Spotlight, Photos, and Mail, the search experience has been rebuilt to make it more stable and efficient to help users find exactly what they are looking for."
  - [A4] "It can draw on personal context understanding to search across messages, emails, photos, and more, and get things done across apps with even more systemwide app actions."
- **Apple 1차 자료 중 "semantic index"가 나오는 곳은 개발자 가이드예요** [A6]: "Entity schemas contribute your app's content to the Spotlight semantic index, enabling personal context understanding with attribution back to your app, …"
- **'맥락 인지'라는 말도 걸려요.** Apple은 화면을 이해하는 "onscreen awareness"와 "personal context understanding"을 서로 다른 기능으로 나눠 불러요. 그러니 '맥락 인지'는 '개인 맥락 이해'로 쓰는 편이 정확해요.
- **고친 장표 문장:** "Apple은 iOS 27에서 Siri가 기기 안 Spotlight 색인을 바탕으로 메시지·메일·사진 속 개인 맥락을 찾아 답한다고 발표했다." [A3][A4]
- **공식 예시** [A3]: "For example, users can ask Siri to find a restaurant recommendation a friend messaged them about, surface a hotel confirmation number from an old email, or pull up photos with friends and family from a recent trip."

### 출시 시점과 한국어
- **iOS 26에서는 출시되지 않았어요.**
  - 2026-06-08 발표 [A3]: "Siri AI will be available as a beta later this year for users with a supported device set to English, and Apple will quickly expand support for more languages."
  - 보도 [M2]: "After Apple announced a delay for the Apple Intelligence version of Siri in March 2025, Bloomberg's Mark Gurman said that Apple had set an internal launch target for iOS 26.4." 그러나 iOS 26.4 베타에는 들어가지 않았어요.
- **2026-09-14, iOS 27에서 영어 베타로 출시됐어요** [A1].
  - "Siri AI begins rolling out today in beta in English, and will expand to French, Japanese, Korean, Portuguese, and Spanish next month."
  - "Siri AI is rolling out in beta in English in iOS 27, iPadOS 27, macOS 27, watchOS 27, and visionOS 27, and requires an Apple Intelligence-enabled device set to a supported language."
- **2026-10-26, iOS 27.2에서 한국어가 추가됐고 아직 베타예요** [A2].
  - "With the 27.2 software updates released today, Siri AI … is expanding to more people around the world, with availability now in the French, Japanese, Korean, Portuguese, and Spanish languages."
  - "Siri AI is available in beta in iOS 27.2, iPadOS 27.2, macOS 27.2, watchOS 27.2, and visionOS 27.2 … It is available in English, French, Japanese, Korean, Portuguese, and Spanish."
  - 지역 제한: "Siri AI is currently unavailable in the EU in iOS, iPadOS, and watchOS."
- **기기 안 처리:** 색인은 기기 안에서 동작해요("work entirely on device"). 모델은 "These latest models run on device and on servers using Private Cloud Compute." [A1]

## 4. HippoRAG 오류 분석 → 맞음. 다만 '추출'을 둘로 나눠 읽어야 해요

- **서지:** Gutiérrez, Shu, Gu, Yasunaga, Su(Ohio State, Stanford), NeurIPS 2024, arXiv 2405.14831 [H1]
- **결론(§7):** "This is evident in the error analysis discussed in Appendix F , which shows most errors made by our system are due to NER and OpenIE and thus could benefit from direct fine-tuning. Given that the rest of the errors are graph search errors, …"
- **부록 F.1:** "In this section, we provide a detailed error analysis of 100 errors made by HippoRAG on the MuSiQue dataset." 표 11의 분류는 NER Limitation 48, Incorrect/Missing OpenIE 28, PPR 24(%)예요.
- **48%는 질문 쪽 오류예요.**
  - "The main error type, with nearly half of all error examples, is due to limitations of our NER based design. As further discussed in § F.2 , our NER design does not extract enough information from the query for retrieval."
  - F.2: "ignoring contextual cues accounts for around 48 % of errors in our small-scale error analysis."
- **색인할 때 생긴 추출(OpenIE) 오류는 28%예요.**
  - F.3: "OpenIE is a critical step in extracting structured knowledge from unstructured text. Nonetheless, its shortcomings can result in gaps in knowledge that may impair retrieval and QA capabilities."
  - 전쟁의 시작·끝 연도를 놓친 예시에 대해: "This is an example of how models routinely ignore temporal properties."
- **장표 표현**
  - 써도 되는 말: "그래프 방식의 오류는 대부분 질문과 문서에서 정보를 뽑는 단계에서 나왔다." 100건 중 76건이고, 이 76은 48+28을 제가 더한 값이에요.
  - 쓰면 안 되는 말: "그래프를 만들 때의 추출 오류가 대부분이다." 색인 쪽 오류는 28%뿐이에요.
- **범위:** 데이터셋은 MuSiQue 하나, 오류 표본은 100건이에요. 저자도 "small-scale"이라고 썼어요.

## 5. 삼성 현재 기능: 기존 노트에 더하거나 고칠 것

다음 내용은 기존 노트 그대로 유효해요: PDE 공식 문구(§1-1), Finder 자연어 검색(§3), Now Brief·Now Nudge·Bixby·Gemini 비교(§4), 경쟁사(§5). 고치거나 더할 것은 아래와 같아요.

1. **정정: PDE를 다룬 논문이 있어요.**
   - 기존 노트 §2의 "SDC 세션이나 논문도 검색에서 나오지 않았음"은 이 CEUR 논문(2025-11, [C1])으로 바꿔야 해요.
   - 다만 "스키마·엔티티·관계·규칙은 비공개"라는 결론은 그대로예요.
2. **'지식 그래프'를 쓴 1차 문헌이 하나 늘었어요.**
   - [C1]: "The PDE uses a Knowledge Graph (KG) to integrate personal data derived from multiple sources and to provide on-device AI capabilities to client applications."
   - 삼성전자 명의 자료에는 여전히 이 말이 없어요. 그래서 기존 노트 §7의 금지 문구("삼성이 PDE를 지식 그래프라고 발표했다")는 유지해요.
3. **PDE가 LLM도 쓴다는 문장이 새로 나왔어요**(1-2 인용). 그래서 "PDE는 규칙만 쓰는 옛 방식"이라는 대비는 틀린 말이 돼요.
4. **PDE도 검색에 쓰여요.** 그림 1의 출력에 "Search"가 있어요. S25 보도자료의 갤러리 자연어 검색 문장([S1])과도 맞아요.
5. **2026-10-31 이후의 새 삼성 공식 발표(PDE, Finder, Now Brief)는 이번 검색에서 찾지 못했어요.**
   - Computer Weekly 기사 "Samsung unpacks Galaxy AI’s personal data engine"은 열지 못했어요(403). 검색 요약에는 이 기사가 삼성이 'personal knowledge graph'를 말했다고 인용했다고 나와요. 이 부분은 **확인 못 함**이에요.
   - 검색 요약에 삼성 설명처럼 나온 "converts scattered data … into structured, AI-readable context" 문장은 [S4], [S6], [S14] 어디에도 없어요. 출처를 **확인 못 함**이라 쓰면 안 돼요.
6. Apple 항목([A1], [A2])과 RDFox 문서([O4])는 오늘 다시 열어 봤고, 인용한 문장이 그대로 있었어요.

## 6. 지도 메모의 문구 4건

**6-1. "One-hop으로는 … 절대 넘을 수 없습니다" → "한 번의 검색으로 필요한 근거가 함께 회수되지 않을 수 있습니다"**
- **판정:** 원래 문구의 '절대'는 틀렸어요. 그래프 색인을 쓰면 여러 단계를 한 번에 찾을 수 있어요: "Single-step retrieval with HippoRAG achieves comparable or better performance than iterative retrieval like IRCoT …" [H1]. 바꾼 문구는 정확하지만, '~수 있습니다'는 약하고 '회수'는 전문 용어예요.
- **제안:** **"답의 근거가 두 기록에 나뉘어 있다. 먼저 찾은 기록이 다음 검색의 단서가 된다."**
- **근거:** IRCoT [L2] "Here, what to retrieve depends on what has already been derived, which in turn may depend on what was previously retrieved."
- **바꾼 점:** 'One-hop'과 '회수'를 뺐어요. 능력을 단정하는 대신, 이 시나리오의 사실(카톡과 사진, 두 기록)을 적었어요.

**6-2. "그래프에 없는 '휴지 = 집들이'" → "사전 추출·추론되지 않은 관계는 원문 근거로 보완합니다"**
- **판정:** 원래 문구는 PDE 그래프에 무엇이 있는지 단정해요. 스키마가 비공개라 근거가 없어요. 바꾼 문구는 논문이 밝힌 구조와 맞아요. 그래프에는 분석 결과와, 온톨로지에서 따라 나오는 트리플만 들어가요 [C1]. 다만 '휴지' 예시가 빠졌고 '사전 추출·추론'이 어려워요.
- **제안:** **"미리 그래프로 만들어 두지 않은 연결(‘휴지 안 사 와도 돼’ → 집들이)은 원문 기록에서 찾아 보완한다."**
- **근거**
  - [C1] "The result of this analysis is stored in the user’s personal knowledge graph where it is augmented with triples entailed by the ontology."
  - [L5] 개선 방향: "(2) Combining structured graph information with raw text to improve retrieval robustness and completeness."
- **바꾼 점:** 빠진 예시를 되살렸어요. '사전 추출·추론되지 않은'은 '미리 그래프로 만들어 두지 않은'으로 바꿨어요. '보완'은 PDE와 경쟁하지 않고 보완한다는 포지션이라 그대로 뒀어요.

**6-3. "미리 정한 항목 없이" → "모든 의미 관계를 사전 구조화하지 않고도 원문을 검색합니다"**
- **판정:** 원래 문구는 틀렸어요. Weave도 날짜·앱 같은 정해진 메타데이터 칸을 미리 붙여요. 2홉도 날짜 메타데이터로 사진을 걸러요. 바꾼 문구는 정확한데, 부정이 두 번 들어가고 '사전 구조화'가 어려워요.
- **제안:** **"기록은 원문 그대로 두고, 날짜·앱 같은 기본 정보만 붙여 둔다. 의미 관계는 질문이 들어올 때 찾는다."**
- **근거:** MDR [L4] "Contrary to previous work, our method does not require access to any corpus-specific information, such as inter-document hyperlinks or human-annotated entity markers, and can be applied to any unstructured text corpus."
- **바꾼 점:** 부정문을 긍정문 두 개로 나눴어요. 메타데이터를 드러내서 실제 설계와 맞췄어요.

**6-4. "Reasoning Embedding이 집들이를 추론해 날짜를 획득" → "Retriever가 카톡을 찾고, 근거 해석 단계가 문맥과 날짜를 연결합니다"**
- **판정:** 원래 문구는 역할이 섞였어요. 임베딩은 기록을 찾는 부품이고, 날짜를 만들어 내지 않아요. 날짜는 찾은 카톡의 메타데이터(수신일 3/15)에서 와요. 바꾼 문구는 역할을 정확히 나눴지만, 'Retriever'와 '근거 해석 단계'가 덱의 다른 장표 용어(Reasoning Embedding, 질문 다시 쓰기)와 이름이 달라요.
- **제안:** **"추론도 잘하도록 튜닝한 임베딩이 ‘집들이’라는 말이 없는 지은이의 카톡을 찾는다. 그 카톡의 날짜(3/15)로 질문을 다시 쓰고, 사진을 거른다."**
- **근거:** ReasonIR [L6]
  - "We present ReasonIR-8B, the first retriever specifically trained for general reasoning tasks." Reasoning Embedding류가 '찾는 부품'(retriever)이라는 근거예요.
  - "its performance consistently increases with longer and more information-rich rewritten queries" 질문 다시 쓰기와 함께 쓴다는 근거예요.
- **바꾼 점:** 영어 용어를 뺐어요. '추론해 획득'을 '찾는다'와 '날짜로 다시 쓰고 거른다' 두 동작으로 나눴어요.

## 7. "그래프(KG)는 기록이 들어올 때 잇고, Weave는 질문이 들어올 때 잇는다" → 공정함, 조건 하나

- **PDE 쪽은 원문이 직접 뒷받침해요.**
  - [C1] "incrementally maintains a fully materialised graph"
  - RDFox 문서 [O4] "RDFox uses materialization-based reasoning to precompute and store all triples that logically follow from the input graph and rules in a query-independent way."
- **같은 구분을 쓰는 문헌이 있어요.** GraphRAG [L1] 그림 1은 파이프라인을 "Indexing Time"과 "Query Time"으로 나눠요. 그래프를 만드는 일은 Indexing Time에 해요: "Our approach uses an LLM to build a graph index in two stages: first, to derive an entity knowledge graph from the source documents, then to pregenerate community summaries for all groups of closely related entities."
- **질문이 들어올 때 잇는 방식**
  - IRCoT [L2]: "interleaves retrieval with steps (sentences) in a CoT, guiding the retrieval with CoT and in turn using retrieved results to improve CoT"
  - Self-Ask [L3]: "the model explicitly asks itself (and answers) follow-up questions before answering the initial question"
  - MDR [L4]: 링크나 개체 표시 없이 원문에서 홉을 이어요(6-3 인용).
- **비용 구조는 서로 반대예요.** HippoRAG 부록 G [H1]
  - 색인 쪽: "Although offline indexing time and costs are higher for HippoRAG than IRCoT—around 10 times slower and $ 15 more expensive for every 10,000 passages …"
  - 질문 쪽: "retrieval costs for IRCoT are 10 to 30 times higher than HippoRAG"
  - 즉 미리 이어 두면 질문할 때 싸고 빨라요. 질문할 때 이으면 미리 잇지 못한 관계까지 찾지만, 질문마다 계산이 더 들어요.
- **그래프 쪽 약점의 근거** [L5]: "In Appendix C , we show that only about 65.8% of answer entities appear in the constructed KG for HotPotQA and 65.5% for NQ, highlighting the sensitivity of KG-based retrieval to graph construction quality." 이 수치는 LLM이 공개 QA 문서로 만든 그래프에서 잰 것이에요. PDE를 잰 값이 아니에요.
- **조건:** 그래프도 질문할 때 저장된 관계를 따라 조인해요(SPARQL). Weave도 기록이 들어올 때 임베딩과 메타데이터 색인을 만들어요. 그래서 '잇는다'는 **의미 관계를 만드는 시점**이라는 뜻으로만 써야 정확해요. 각주가 필요하면 "그래프: 관계를 저장할 때 만든다 / Weave: 관계를 질문할 때 찾는다"로 쓰면 돼요.
- **둘을 함께 쓰면 좋아진다는 근거**
  - [H1] "integrating HippoRAG into IRCoT brings further substantial gains"
  - [L5] "we explore selection and integration strategies that combine the strengths of both paradigms, leading to consistent performance improvements."

## Appendix에 쓸 수 있는 임원용 핵심 문장

1. 삼성 PDE는 여러 앱의 기록을 AI로 분석해, 기기 안 '개인 지식 그래프'에 쌓는다. — [C1] §2
2. 그래프는 규칙으로 알 수 있는 사실까지 미리 계산해 넣어 둔다. — [C1] §3 "fully materialised graph", [O4] "precompute and store"
3. 저장, 추론, 조회가 모두 기기 안에서 일어난다. — [C1] §2 "Importantly, all this happens on the device."
4. 그래프는 기록이 들어올 때 잇고, Weave는 질문이 들어올 때 잇는다. — [C1], [O4], [L1] 그림 1(Indexing Time / Query Time)
5. 그래프 방식은 그래프를 만들 때 정보를 얼마나 뽑아 두었는지에 좌우된다. — [L5] "sensitivity of KG-based retrieval to graph construction quality"
6. 미리 그래프로 만들어 두지 않은 연결은 원문 기록에서 찾아 보완한다. — [L5] 개선 방향 (2)
7. 답의 근거가 두 기록에 나뉘어 있다. 먼저 찾은 기록이 다음 검색의 단서가 된다. — [L2]
8. 막연한 질문은 작은 질문으로 나눠 차례로 찾는다. — [L3]
9. 추론도 잘하도록 튜닝한 임베딩은 질문에 바로 답하지 않는 기록도 찾도록 학습된다. — [L6] "existing training datasets focus on short factual queries tied to documents that straightforwardly answer them"
10. Apple도 iOS 27에서 Siri가 메시지·메일·사진 속 개인 맥락을 찾아 답하게 했다(10/26 한국어 베타). — [A1], [A2]
11. Apple Siri가 쓰는 Spotlight 색인은 기기 안에서 동작한다. — [A3] "which work entirely on device"
12. 미리 잇는 그래프와 질문할 때 잇는 검색은 함께 쓸 때 더 좋아진다. — [H1], [L5]

## 쓰면 안 되는 말

- **"Apple이 'semantic index'로 강화한다고 발표했다"(뉴스룸 출처로)**: 뉴스룸에는 "Spotlight index"로 나와요. 이 말을 쓰려면 개발자 가이드 [A6]를 출처로 달아야 해요.
- **"Apple 개인 맥락 Siri는 아직 안 나왔다", "한국어는 안 된다"**: 9/14에 영어 베타, 10/26에 한국어 베타가 나왔어요 [A1][A2].
- **"Apple Siri AI는 전부 기기 안에서 돈다"**: 모델은 기기와 PCC 서버를 함께 써요 [A1].
- **"PDE는 LLM 없이 규칙만 쓴다", "PDE는 옛 방식"**: 논문에 "machine learning and LLMs"로 분석한다고 나와요 [C1].
- **"PDE는 임베딩이나 의미 검색을 안 쓴다"**: 논문에 언급이 없을 뿐이에요.
- **"PDE는 검색을 못 한다", "PDE는 질문에 답하지 못한다"**: SPARQL 질의 엔진이 있고, 그림 1에 Search가 있어요 [C1].
- **PDE의 크기, 속도, 메모리, 그래프 규모 숫자**: 논문에 없어요. 규모 표현은 "millions of users"(추정 표현) 하나뿐이에요.
- **"PDE 그래프에는 ‘휴지 = 집들이’가 없다"**: 스키마가 비공개예요.
- **"그래프는 멀티홉을 못 한다", "One-hop으로는 절대 못 한다"**: 규칙 추론과 HippoRAG의 단일 단계 멀티홉이 반례예요 [O4][H1].
- **"HippoRAG 오류는 대부분 그래프를 만들 때 생긴 추출 오류"**: 색인 쪽 OpenIE는 28%이고, 가장 큰 48%는 질문 쪽 NER이에요 [H1].
- **"Reasoning Embedding이 날짜를 알아낸다/추론해 획득한다"**: 날짜는 카톡 메타데이터에서 와요.
- **"Weave는 미리 정한 항목이 없다"**: 날짜·앱 메타데이터 칸이 있어요.
- **"질문할 때 이으니 비용이 들지 않는다", "그래프보다 빠르다"**: 질문할 때 잇는 방식은 질문마다 계산이 더 들어요 [H1] 부록 G.
- **본 장표의 RDFox, DRed, OWL RL, Datalog, 트리플, SPARQL**: 이런 용어는 각주나 Q&A로만 쓰세요.
- **"삼성이 PDE를 RDFox·지식 그래프로 만들었다고 발표했다"**: 삼성전자 명의 자료에는 "OST 협업 개발"까지만 나와요([S12]). RDFox와 KG를 명시한 곳은 OST 자료예요([O1], [C1]).

## 출처 (2026-11-08 접속)

- [C1] Crocker, Horrocks, Nenov, "Semantic Technology in Your Pocket", ISWC 2025 Companion(CEUR-WS Vol-4085), Industry Track, pp. 17–19. https://ceur-ws.org/Vol-4085/paper5.pdf
- [C2] CEUR-WS Vol-4085 목차. https://ceur-ws.org/Vol-4085/
- [A1] (기존 노트, 재확인) Apple Newsroom, 2026-09-14. https://www.apple.com/newsroom/2026/09/siri-ai-a-profoundly-more-capable-and-personal-assistant-is-here/
- [A2] (기존 노트, 재확인) Apple Newsroom, 2026-10-26. https://www.apple.com/newsroom/2026/10/siri-ai-is-available-in-more-languages-starting-today/
- [A3] Apple Newsroom, "Apple introduces Siri AI, a profoundly more capable and personal assistant", 2026-06-08. https://www.apple.com/newsroom/2026/06/apple-introduces-siri-ai-a-profoundly-more-capable-and-personal-assistant/
- [A4] Apple Newsroom, "Apple unveils next generation of Apple Intelligence, Siri AI, and more", 2026-06-08. https://www.apple.com/newsroom/2026/06/apple-unveils-next-generation-of-apple-intelligence-siri-ai-and-more/
- [A5] Apple Newsroom, "Apple Intelligence brings powerful AI capabilities into everyday experiences", 2026-06-08("semantic index"와 "Spotlight" 모두 없음). https://www.apple.com/newsroom/2026/06/apple-intelligence-brings-powerful-ai-capabilities-into-everyday-experiences/
- [A6] Apple Developer, "WWDC26 Apple Intelligence guide". https://developer.apple.com/wwdc26/guides/apple-intelligence/
- [M1] [보도] 9to5Mac, "Apple unveils new Siri AI, dedicated app, and enhanced Apple Intelligence features in iOS 27", 2026-06-08. https://9to5mac.com/2026/06/08/new-siri-whats-new/
- [M2] [보도] MacRumors, "iOS 26.4 Beta Launches Without Apple Intelligence Siri Features", 2026-02-17. https://www.macrumors.com/2026/02/17/ios-26-4-no-new-siri-features/
- [H1] Gutiérrez et al., "HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models", NeurIPS 2024. https://arxiv.org/abs/2405.14831 (부록 F·G는 https://arxiv.org/html/2405.14831v3)
- [L1] Edge et al., "From Local to Global: A Graph RAG Approach to Query-Focused Summarization", arXiv 2024. https://arxiv.org/abs/2404.16130
- [L2] Trivedi et al., "Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions"(IRCoT), ACL 2023. https://arxiv.org/abs/2212.10509
- [L3] Press et al., "Measuring and Narrowing the Compositionality Gap in Language Models"(Self-Ask), Findings of EMNLP 2023. https://arxiv.org/abs/2210.03350
- [L4] Xiong et al., "Answering Complex Open-Domain Questions with Multi-Hop Dense Retrieval"(MDR), ICLR 2021. https://arxiv.org/abs/2009.12756
- [L5] Han et al., "RAG vs. GraphRAG: A Systematic Evaluation and Key Insights", arXiv v3 2026-03-04. https://arxiv.org/abs/2502.11371
- [L6] Shao et al., "ReasonIR: Training Retrievers for Reasoning Tasks", arXiv 2504.20595. https://arxiv.org/abs/2504.20595
- [O4] (기존 노트, 재확인) RDFox 문서, "Reasoning". https://docs.oxfordsemantic.tech/reasoning.html
