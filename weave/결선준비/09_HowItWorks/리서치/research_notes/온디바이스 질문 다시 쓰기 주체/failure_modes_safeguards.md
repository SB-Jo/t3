# Small-model query rewriting and decomposition for multi-hop personal retrieval: failure modes, safeguards, evaluation (state as of 2026-11-02)

Conventions (read first). `LOCAL:<key> L<n>` = line n of `/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/<key>/src.txt`, re-read on 2026-11-02; table cells of local papers were read from `raw.html` in the same folder. Keys → papers: longmemeval = [arXiv 2410.10813](https://arxiv.org/abs/2410.10813) (ICLR 2025); hiq = [arXiv 2608.30468](https://arxiv.org/abs/2608.30468) (venue "NeurIPS 2026 (Poster)" comes from the local `meta_ko.json` / project-page badge, not from the paper text); ircot = [2212.10509](https://arxiv.org/abs/2212.10509) (ACL 2023); efficientrag = [2408.04259](https://arxiv.org/abs/2408.04259) (EMNLP 2024); reasonir = [2504.20595](https://arxiv.org/abs/2504.20595); mdr = [2009.12756](https://arxiv.org/abs/2009.12756) (ICLR 2021); bright = [2407.12883](https://arxiv.org/abs/2407.12883); hipporag = [2405.14831](https://arxiv.org/abs/2405.14831). Web sources were downloaded on 2026-11-02 (arXiv HTML, ACL Anthology / LREC PDFs, GitHub raw files) and grepped for the exact strings quoted. Inside quotes, LaTeX delimiters such as `\(`, `\)` are dropped; wording is otherwise verbatim. Tags: **[EN]** English public benchmark (mostly Wikipedia/web), **[PERS-EN]** English synthetic personal-memory data, **[KO]** Korean-language evidence. **No number in these notes is Weave's performance.** "(my calc)" = a number I derived from table cells; the source does not state it.

## 1. Temporal expressions: how reliably small LLMs extract and normalize time; rule-based normalizers vs LLMs; Korean relative dates; hybrid designs

### Takeaway
Small (≤8B) LLMs are the weak link for time. In LongMemEval, Llama 3.1 8B invents time ranges for questions that have no time reference, and these wrong ranges cut the gold evidence out of the search; by my calculation from its Table 4, the 8B time-range extractor gives no net recall gain. In 2023–2025 benchmarks, small open models are near the floor on few-shot TIMEX normalization and on zero-shot date arithmetic. Fine-tuned small models and rule/grammar normalizers, on the other hand, handle the arithmetic well. Rule systems are still the reference for normalization, but they need the right anchor date, and they encode conventions that are themselves ambiguous. Korean resources are thin. All the evidence points to a hybrid: the model finds the span and picks the anchor, and deterministic code computes the date.

### Cited Findings

#### 1a. LongMemEval §5.4 and Appendix E.4 (exact quotes and numbers) [PERS-EN]
- Mechanism: "Specifically, values are additionally indexed by the dates of the events they contain. During retrieval, an LLM M_T extracts a time range for time-sensitive queries, which is used to filter out a large number of irrelevant values." — LOCAL:longmemeval L244 ([arXiv 2410.10813](https://arxiv.org/abs/2410.10813))
- Motivation: "However, when queries involve temporal references (e.g., “Which restaurant did you recommend last weekend?”), naive similarity search proves insufficient." — LOCAL:longmemeval L193
- Headline numbers plus the small-model failure, verbatim: "As shown in Table 4, this simple design improves recall by an average of 11.3% when using rounds as the value and by 6.8% when using sessions as the value. This improvement remains consistent when key expansion is applied during indexing. We also find that the effectiveness of this method depends on using a strong LLM for M_T to accurately infer time ranges from queries. Llama 8B, on the other hand, struggles to generate accurate time ranges, often hallucinating or missing temporal cues even with numerous in-context examples." — LOCAL:longmemeval L247
- Abstract wording of the same result: "improving the memory recall for temporal reasoning by 6.8%∼11.3% when a strong LLM is employed for query expansion." — LOCAL:longmemeval L31
- Setup. The 8B model is used on the indexing side, and both models are tried on the query side: "At the indexing stage, we instruct Llama 3.1 8B Instruct to extract the event mentions in the text whose timestamp could be inferred. At the retrieval stage, we instruct an LLM (we explore GPT-4o and Llama 3.1 8B Instruct) to extract the a time range for retrieval for the problems that specifically focus on a range of time. We present the corresponding prompts in Figure 12. Ten human-written in-context examples are additionally provided." — LOCAL:longmemeval L454. Retriever: "dense retrieval with the 1.5B Stella V5 model" — L211.
- Appendix E.4, verbatim: "In Section 5.4, we concluded that a strong model is required to accurately extract the time ranges from the questions, even if in-context examples (with balanced labels) are provided. In this section, we further illustrate this finding with examples in Table 11. We find that the Llama 3.1 8B Instruct model can generate a correct temporal range when the time references are clearly defined (example 2). However, in many of the cases where the question does not have any temporal reference (example 1, 2, 4), the model often mistakenly extracts a time range, which erroneously prunes out the search space, leading to a low memory recall. By contrast, GPT-4o is able to refuse to generate a time range when the question does not have a time reference." — LOCAL:longmemeval L517
  - Source inconsistency: Table 11 marks Llama's false positives on examples **1, 3 and 4** and marks example 2 as correct, so "(example 1, 2, 4)" in the text looks like a typo for 1, 3, 4.
- Table 11 cells, verbatim (LOCAL:longmemeval raw.html, "Table 11: Example of time span extraction outputs from GPT-4o and Llama 3.1 8B Instruct."):
  - Ex. 1. "Question Date: 2023/05/28"; "How long had I been taking guitar lessons when I bought the new guitar amp?" GPT-4o: "No date extracted [correct]"; Llama 3.1 8B: "2023/05/01 ∼ 2023/05/28 [false positive]".
  - Ex. 2. "Question Date: 2023/04/27"; "Which airline did I fly with the most in March and April?" Both models: "2023/03/01 ∼ 2023/04/30 [correct]".
  - Ex. 3. "Question Date: 2023/06/28"; "How many days before the ’Rack Fest’ did I participate in the ’Turbocharged Tuesdays’ event?" Llama: "2023/06/21 ∼ 2023/06/28 [false positive]".
  - Ex. 4. "Question Date: 2023/03/10"; "Which seeds were started first, the tomatoes or the marigolds?" Llama: "2023/03/01 ∼ 2023/03/10 [false positive]".
- Table 4 cells ("Retrieval performance on the temporal reasoning subset of LongMemEval_M"), Recall@5 / Recall@10:
  - (1) K = V. Session: base 0.639 / 0.651; +QE GPT-4o 0.654 / 0.707; +QE Llama 3.1 8B 0.624 / 0.647. Round: base 0.421 / 0.499; GPT-4o 0.451 / 0.495; Llama 8B 0.384 / 0.489.
  - (2) K = V + fact. Session: base 0.684 / 0.721; GPT-4o 0.722 / 0.797; Llama 8B 0.677 / 0.711. Round: base 0.489 / 0.550; GPT-4o 0.526 / 0.722; Llama 8B 0.481 / 0.570.
- (my calc) The paper's 11.3% (rounds) and 6.8% (sessions) match the mean *relative* change of the four Recall cells (R@5 and R@10 under settings 1 and 2) with GPT-4o. Rounds: +7.1, −0.8, +7.6, +31.3% → 11.3%. Sessions: +2.3, +8.6, +5.6, +10.5% → 6.8%. Averaged the same way, Llama 3.1 8B gives about **−2.2% (rounds)** and **−1.3% (sessions)**, i.e., a net loss against no time filter. Only one cell (round R@10, setting 2: 0.550 → 0.570) improves.
- How the data was built, relevant to time: evidence statements were rephrased "into more natural, colloquial language, especially for time mentions, which LLMs often express too formally ... For questions involving temporal information, we then manually add timestamps to both the evidence sessions and the questions." — LOCAL:longmemeval L106. Non-anchored sessions: "Other wise, we randomly assign tiemstamps in May 2023." (sic) — L355.

#### 1b. Temporal-reasoning benchmarks that report small-model results [EN]
- **TempReason**, Tan et al. ([arXiv 2306.08952](https://arxiv.org/abs/2306.08952)).
  - L1 questions "have the form of ‘What is the date x years and y months before/after t ?’."
  - Table 4, L1 (Time-Time), CBQA, EM / F1: FLAN-T5-L **0.0 / 2.9**; ChatGPT **30.5 / 56.7**; T5-SFT **100 / 100**; TempT5 **100 / 100**.
  - Setup: FLAN-T5-Large is evaluated zero-shot. For T5-SFT, "We use the T5-base model in our experiments and we fine-tune this model on each setting". ChatGPT (gpt-3.5-0301) was run on "only ... 200 examples for each setting".
  - Pilot finding: "not only do LMs perform poorly on the time-time relation task, but they are also heavily biased in favor of contemporary years (2000 - 2020)."
- **TimeBench**, Chu et al. ([arXiv 2311.17667](https://arxiv.org/abs/2311.17667)).
  - Task definition: "When provided with a date, the model needs to accurately calculate the date a certain amount of time before or after the given date. The smallest unit is one day."
  - Table 5 (zero-shot, "All models are alignment models (-chat or -instruct)"), "Arith" accuracy: Human **100.0**; GPT-4 **98.0**; GPT-3.5 **97.0**; LLaMA2-70b **78.5**; LLaMA2-13b **22.5**; LLaMA2-7b **13.0** (+CoT **5.0**); Mistral-7b **26.5**; Baichuan2-7b **4.5**; Vicuna1.5-7b **5.0**; ChatGLM3-6b **2.0**.
  - Table 9 confirms that the "Date Arith" metric is "Acc".
- **ChronoSense** ([arXiv 2501.03040](https://arxiv.org/abs/2501.03040)). True/False questions.
  - Table 9, all arithmetic questions, 0-shot average: Gemma2-9B-it **0.76**; Llama3.1-8B **0.48**; Mistral-7B **0.36\***; Phi-3-mini **0.67**; GPT-4o 0.55; GPT-4o-mini 0.60.
  - Same table with CoT: **0.94 / 0.92 / 0.70 / 0.98** (same model order); GPT-4o 0.99; GPT-4o-mini 0.99.
  - "Next-Occurence (0-shot)": Llama3.1-8B **0.104\***; Mistral-7B **0.082\***; Phi-3-mini **0.432**; Gemma2-9B-it **0.678**. With CoT: 0.82 / 0.768 / 0.962 / 0.874.
  - The asterisk: "(*) indicates the models that perform poorly due to producing a high number of unclear answers (≥ 250) in the majority of the tasks. These models fail to follow the instruction by not answering with "True" or "False" as required."
  - Next-occurrence template: "Did ‘Event A’ occur again in the year [next-occurrence]? Answer True or False."
- **Test of Time**, Fatemi et al. ([arXiv 2406.09170](https://arxiv.org/abs/2406.09170)). Evaluates **no small models**: "we evaluate the performance of three frontier large language models (LLMs) on our benchmark. The models evaluated include Claude-3-Sonnet [4], GPT-4 [1], and Gemini 1.5 Pro [47]."
  - Table 8 (ToT-Arithmetic accuracy; Claude-3-Sonnet / GPT-4 / Gemini 1.5 Pro): AddSubtract 58.57 / 76.28 / 71.14; Duration 15.00 / 16.00 / 13.50; Trick 40.40 / 45.60 / 41.20; Timezone 74.00 / 88.00 / 90.00.
  - Example "Trick" item: "If the date for the day before tomorrow in yyyy-mm-dd format is 2016-01-20, what is the date 27 days from now in the same format?"
- **TimeQA**, Chen et al. ([arXiv 2108.06314](https://arxiv.org/abs/2108.06314)). Pre-LLM QA models: "the performance drops from 60% to 45% on the hard version ... When comparing with human performance of 87% on TimeQA-hard, the existing neural models are still significantly lagging behind."
- **LoCoMo** [PERS-EN] ([arXiv 2402.17753](https://arxiv.org/abs/2402.17753)). Table 2, answer F1, "Temporal" column: Human **92.6**; Mistral-Instruct-7B **16.1**; Llama-2-Chat-70B 13.3; GPT-3.5-turbo 17.5; GPT-4-turbo 10.4. Text: models "still significantly lag behind human levels (by 56%), especially in temporal reasoning, (by 73%)".

#### 1c. Rule-based normalizers (HeidelTime, SUTime, Duckling) vs LLMs [EN unless tagged]
- **TempEval-3**, UzZaman et al., SemEval 2013 ([PDF](https://aclanthology.org/S13-2001.pdf)).
  - "For temporal expression normalization (identifying the timex attribute value), all participants used rule-engineered approaches."
  - "While normalisation is currently (and perhaps inherently) done best by rule-engineered systems, recognition is now done well by a variety of methods."
  - Metric: "(Value F1 = Timex F1 * Value Accuracy)".
  - Task A (English) value F1: HeidelTime-t **77.61**; NavyTime-1,2 70.97; **SUTime 67.38**; ClearTK-1,2 64.66.
- **SUTime**, Chang & Manning, LREC 2012 ([PDF](http://www.lrec-conf.org/proceedings/lrec2012/pdf/284_Paper.pdf)). The official SUTime web page refused connections on 2026-11-02, so these come from the paper and the CoreNLP docs.
  - Scope: "a temporal tagger for recognizing and normalizing temporal expressions in English text ... It is a deterministic rule-based system designed for extensibility."
  - Anchoring: "SUTIME uses document dates as references. For example, for a document from 2011-09-19, SUTIME would resolve the date referred to by last Friday as 2011-09-16."
  - Stated limitation: "Even with a reference date, there can be inherent ambiguity about the time point to which a relative time expression refers. For instance, given a reference date of 2011-09-19, a Monday, it is unclear whether Friday refers to 2011-09-16 or 2011-09-23. In addition, SUTIME resolves all temporal expressions to one reference date, the document date."
  - CoreNLP: "The DocDateAnnotator provides a variety of options for setting the document date." Options include `useFixedDate`, `useMappingFile`, `usePresent` and `useRegex` ([CoreNLP NER docs](https://stanfordnlp.github.io/CoreNLP/ner.html)).
- **HeidelTime** ([README](https://github.com/HeidelTime/heideltime)).
  - "HeidelTime currently contains hand-crafted resources for 13 languages: English, German, Dutch, Vietnamese, Arabic, Spanish, Italian, French, Chinese, Russian, Croatian, Estonian and Portuguese." Korean is not among them.
  - "HeidelTime contains automatically created resources for 200+ languages in addition to manually created ones for 13 languages."
  - The repo's `resources/` folder contains `auto-korean` ([GitHub listing](https://github.com/HeidelTime/heideltime/tree/master/resources), read via the GitHub API).
  - "English colloquial (e.g., Tweets and SMS) and scientific articles (e.g., clinical trails) are supported." This colloquial support is English-only.
- **Duckling** ([README](https://github.com/facebook/duckling)).
  - "Duckling supports many languages, but most don't support all dimensions yet."
  - Its `Time` dimension outputs ISO values with a grain.
  - Korean time rules exist (`Duckling/Time/KO/Rules.hs`, `Corpus.hs`). The test corpus fixes an anchor: "The reference time for the corpus is Tuesday Feb 12, 2013 at 4:30am." Korean examples are in §1d.
- **LLM in-context normalization**, "Discourse-Aware In-Context Learning for Temporal Expression Normalization" ([arXiv 2404.07775](https://arxiv.org/abs/2404.07775)).
  - Table 4, TempEval3 accuracy, all prompted with "Target-centric + CW": GPT3.5 **72.6**; Zephyr-7B **48.1**; Llama2-7B **7.75**; Mistral-7B **7.0**.
  - Table 1: "MLM (Lange et al., 2023)" scores **79.0** on TempEval3.
  - Table 2 (real-world extraction + normalization), TempEval3 Extract / Norm: HeidelTime **84.1 / 80.0**; GPT-ICL (end-to-end) **52.1 / 40.5**; NER+MLM 82.8 / 70.5. On ECJ (court): HeidelTime 43.3 / 43.0; GPT-ICL 24.6 / 18.2; NER+MLM 69.5 / 66.0.
  - Error analysis: "Most challenging are relative and under-specified expressions, where the model lacks enough context or fails to incorporate context information." Table 3: Relative 23 correct / 08 false; Under-specified 05 / 04.
  - Why anchors matter: "relative expressions like ‘‘tomorrow’’ rely on an anchoring date, e.g., the Document Creation Time (DCT). Under-specified expressions are missing the relation to the anchor and cannot be fully normalized by the given context."
  - Small-model format failure: "(1) The LLM does not output machine-readable JSON, when there are not enough examples to learn the output format."
- **Multilingual MLM normalizer**, Lange et al. ([arXiv 2205.10399](https://arxiv.org/abs/2205.10399)).
  - "outperforms the state of the art for multilingual temporal tagging, HeidelTime ... especially for low-resource languages by more than 33 F1 on average."
  - Its weak labels come from rules: "use spacy for tokenization and HeidelTime for the annotation with temporal expressions."
  - Table 3 ("Distribution of explicit / relative values according to HeidelTime by domains (in %)"): English News 52.3 / 47.7; English Wiki 44.2 / 55.8. Relative values are about half of all values.
- **Hybrid, neural detection + grammar normalizer** ([arXiv 2304.14221](https://arxiv.org/abs/2304.14221)): "we present a modular multilingual temporal processing system combining a fine-tuned Masked Language Model for detection, and a grammar-based normalizer ... We obtain best results in gold timex normalization, timex detection and type recognition, and competitive performance in the combined TempEval-3 relaxed value metric. A detailed error analysis shows that detecting only those timexes for which it is feasible to provide a normalization is highly beneficial in this last metric." Evaluated on English and Spanish only.
- **Hybrid, LLM writes code and the interpreter computes dates**: PAL ([arXiv 2211.10435](https://arxiv.org/abs/2211.10435)).
  - The Date task "involves inferring dates from natural language descriptions, performing addition and subtraction of relative periods of time".
  - Table 2, "Date" solve rate: Direct (Codex) 49.9; CoT (Codex) 64.8; **PaL (Codex) 76.2**; CoT PaLM-540b 65.3.

#### 1d. Korean relative dates [KO]
- KTimeML, Im et al. 2009 ([PDF](https://aclanthology.org/W09-3417.pdf)): "Korean is an agglutinative language whose words are formed by joining morphemes together ... consideration of morphemes is important for TimeML markup of Korean text."
- ExoTime, Jeong, Lim & Choi, JKSCI 2017 ([PDF](https://koreascience.or.kr/article/JAKO201707464565210.pdf)), on Korean TimeBank.
  - Table 9, rule-based timex3 "value": P **60.17**, R **67.29**, F1 **63.53**.
  - Surface variation: "‘2010-05-05T15:00’ can be expressed by ‘2010년 5월5일 15시’, ‘2010월 5월5일 오후 3시’, or ‘2010/5/5 15시’. Such various ways of representing same temporal value could not be captured by the machine-learning models".
  - The same paper reports other systems' results (**secondary citations; the originals were not checked**). Seon, Kang & Seo (2010): "lexicalized rules ... achieved about 93% accuracy using manually annotated SMS (Short Message Service) datasets". Angeli & Uszkoreit (2013): "The performance of extraction of temporal values with Korean was 42% accuracy."
- Duckling Korean test corpus ([Corpus.hs](https://github.com/facebook/duckling/blob/main/Duckling/Time/KO/Corpus.hs)). The anchor is Tuesday 2013-02-12 04:30. Expected outputs, verbatim pairs:
  - "일요일" → 2013-02-17.
  - "다음주 화요일" and "다음 화요일" → 2013-02-19.
  - "모레" and "내일모레" → 2013-02-14.
  - "오늘저녁" and "오늘밤" → interval 2013-02-12 18:00 to 2013-02-13 00:00.
  - "이번주말" → 2013-02-15 18:00 to 2013-02-18 00:00.
  - "저번주 일요일", "지난주 일요일", "지난 일요일" and "저번 일요일" → 2013-02-10.
  - **"월요일" and "이번주 월요일" → 2013-02-18.** Said on a Tuesday, the rule set maps "이번주 월요일" to the *next* Monday, not to the previous day.
  - "이번 일요일" (with a space) and "6시" are not in the corpus, so their behavior is untested here.
- HeidelTime has only automatically created Korean resources (`auto-korean`; see 1c). Lange et al.'s weak-label table lists "ko" with **483** annotations, rank 71 of 87 languages (Table 4, [arXiv 2205.10399](https://arxiv.org/abs/2205.10399)).

#### 1e. Message time vs event time [PERS-EN]
- "Beyond Dialogue Time" ([arXiv 2601.07468](https://arxiv.org/abs/2601.07468)) names "Temporal inaccuracy: memories are organized by dialogue time rather than their actual occurrence time". Example: "when a user talks on May 28 about a trip happening on May 29, dialogue time and event time are misaligned; using the dialogue timeline alone can cause the system to store or retrieve memories under the wrong time context." Its method "achieves up to 12.2% absolute improvement in accuracy" on LongMemEval and LoCoMo. That number is for its method, not a rewriter.

### Inferences
- Weave's example (a KakaoTalk message sent Thu 3/12 saying "이번 일요일 6시", which should become 3/15 (일) 저녁) combines the three things that fail most for small models: a relative weekday, an anchor that is the *message* time rather than the question time, and an under-specified hour. The evidence (1a–1c) says to let the small model (i) copy the span "이번 일요일 6시" from the record and (ii) name the anchor (`sent_at` of that record). A deterministic resolver should compute the date. Weave would have to decide and test the conventions itself: does "이번 X" said on Thursday mean the coming X; do "6시" plus a social context default to evening, or is it marked ambiguous.
- The documented small-model failure on the query side is a *false-positive* filter: a window invented to end on today's date. Wrong arithmetic is not the main failure. That points to two cheap guards: a separate "does the question contain an explicit time reference?" decision, where a no-reference question gets no filter; and a post-filter check that falls back to unfiltered retrieval when the filter leaves too few candidates. This follows from LongMemEval L517, but it has not been tested in Korean.
- Duckling's own Korean test corpus maps "이번주 월요일" on a Tuesday to the next Monday. So even rules encode a convention that a Korean user may read differently ("yesterday"). Ambiguous weekday phrases should be resolved to a range or flagged, and shown to the user as a clue rather than silently used as a hard filter.
- Zero-shot date arithmetic in 2023-era 7B models is near zero (TimeBench 2.0–26.5%). 2024–25 8–9B models with CoT reach 0.70–0.94 on binary questions where chance is 0.5 (ChronoSense). Fine-tuned T5-base gets 100 EM on synthetic month arithmetic (TempReason). Together this suggests: compute dates in code, or fine-tune on synthetic Korean date arithmetic. Neither is measured for Korean.

### Gaps
- No benchmark or paper was found that measures LLM normalization of Korean relative dates ("이번/다음/저번 주 X", "모레/글피", colloquial "낼/담주/이따"), let alone in KakaoTalk-style text. Korean numbers above are rule/ML systems on Korean TimeBank (2017) or secondary citations.
- No small-model (≤4B) results on Test of Time. No LongMemEval-style false-positive rate for 2025–26 small models (Qwen3, Gemma 3, EXAONE, etc.).
- Not verified (search snippets only): a 2024 IOS Press paper (FAIA240940) that reportedly fine-tunes Gemma/Mistral/Llama-3 for multilingual normalization, and MultiTempBench ([arXiv 2603.19017](https://arxiv.org/abs/2603.19017); download timed out).
- Duckling output for "이번 일요일 6시" and how it resolves AM/PM for Korean were not tested.

## 2. Bridge-entity hallucination and memorization: the placeholder is filled from parametric memory instead of the retrieved record

### Takeaway
Hi-Q reports that a strong rewriter (GPT-5) "frequently supplies bridge entities that were never retrieved". Independent work finds that reliance on memorized answers grows with model size. For small models the documented failure is different: rewrites that are factually inconsistent, drift off topic, or contain non-existent entities. With personal data, no parametric memory can hold the correct bridge (the user's housewarming date), so any filler not copied from the record is a fabrication. The interventions with evidence are grounding/citation constraints, which Hi-Q shows cost almost no accuracy, corpus-extracted expansions (CSQE), and counterfactual training (Longpre et al.).

### Cited Findings
- [EN] Hi-Q, backbone sensitivity: "Repeating the closed-book control on MuSiQue with GPT-5 yields 25.0 EM / 37.6 F1, well above GPT-4o-mini’s 13.1 / 21.7, and when GPT-5 refines sub-queries it frequently supplies bridge entities that were never retrieved. A stronger backbone therefore answers a larger share of questions from parametric knowledge, which makes answer accuracy a weaker diagnostic of retrieval–query alignment." — LOCAL:hiq L447
- [EN] Hi-Q, the bridge-error mechanism in iterative methods: "A reformulation can be logically plausible while still poorly aligned with the atomic facts the corpus exposes, and once an early step selects the wrong bridge entity or drops a constraint, later queries amplify the error." — LOCAL:hiq L58
- [EN] Hi-Q, the grounding constraint costs little. Hi-Q evaluates "a stricter variant that requires document-level grounding for each answer on a filtered subset of 634 MuSiQue queries" (LOCAL:hiq L429). Table 15: Hi-Q **47.5 EM / 61.9 F1**; "Strict evidence-grounded variant" **47.6 / 61.7**.
- [EN] Hi-Q, closed-book GPT-4o-mini (Table 16): MuSiQue 13.1 / 21.7; 2Wiki 23.1 / 28.8; HotpotQA 29.4 / 39.7 (EM / F1). — LOCAL:hiq L438
- [EN] Longpre et al., Entity-Based Knowledge Conflicts ([arXiv 2109.05052](https://arxiv.org/abs/2109.05052)).
  - "we measure their over-reliance on memorized information (the cause of hallucinations)".
  - "The Memorization Ratio (M_R) measures how often the model generates the original answer (parametric knowledge) as opposed to the answer in the context (contextual knowledge)."
  - "We finetune T5 small (60M), large (770M), XL (3B), and XXL (11B) models on NQ, finding the memorization ratio increases with model size for all inference sets."
  - Mitigation: "training with our substituted instances not only reduces hallucination to negligible levels, but also improves F1 by 4% to 7% on out-of-distribution (OOD) examples".
- [EN] IRCoT ([arXiv 2212.10509](https://arxiv.org/abs/2212.10509)).
  - "Without retrieval, a model is likely to generate an incorrect reasoning step due to hallucination." — LOCAL:ircot L25
  - "Since NoR relies completely on parametric knowledge, it often makes a factual error in the first sentence, which derails the full CoT." — L239
  - "IRCoT reduces the factual errors over OneR by 50% on HotpotQA and 40% on 2WikiMultihopQA". This is a manual check of "40 randomly sampled questions from each of the four datasets" with GPT3. — L230
- [EN] Abe et al., SIGIR 2025 ([arXiv 2505.12694](https://arxiv.org/abs/2505.12694)).
  - "When the LLM lacks knowledge of the query, it may introduce non-existent entities or unrelated terms, decreasing retrieval accuracy."
  - "When the query is ambiguous, the LLM may generate biased expansions, which narrow the search coverage and exclude relevant documents."
  - "LLM-based QE can significantly degrade the retrieval effectiveness when knowledge in the LLM is insufficient or query ambiguity is high."
- [EN] Small rewriters specifically, Anand et al., context-aware query rewriting ([arXiv 2308.16753](https://arxiv.org/abs/2308.16753)): "We also observe that LLMs of smaller scales like Ada-001, Babbage-001 and Curie-001 generate rewrites which are factually inconsistent and drift away from the relevant topic."
- [EN] Crafting the Path ([arXiv 2407.12529](https://arxiv.org/abs/2407.12529)).
  - "relying heavily on inherent knowledge of LLMs for query rewriting often leads to the generation of irrelevant information and causes numerous factual errors". Example: "Q2C asserts that coffee originated in ancient Egypt or Yemen, whereas its origin is Ethiopia".
  - Reports "10% higher FActScore ... compared to baselines".
  - Rewriters used: "we employ Mistral-7b ... and Phi-2 ... as query rewriting models". For Phi-2: "we obtain results using models trained with the new queries written by Mistral-7b."
- [EN] Weller et al. ([arXiv 2309.08541](https://arxiv.org/abs/2309.08541)): "parametric knowledge encoded in model weights affect terms selected for expansion (in contrast to classic PRF that typically selects new terms from the top relevant documents from the collection)."
- [EN] Rewriter size, BRIGHT: "GritLM-generated reasoning steps improve BM25 performance but are less effective for other models likely due to having fewer parameters." — LOCAL:bright L178
- [EN] ReasonIR: "rewritten queries decrease all dense retrievers’ performance on GPQA, which we hypothesize is caused by the small-scale reader model not being able to write good queries for this task, unlike in BRIGHT where a strong model, GPT-4, was used to write good queries." — LOCAL:reasonir L191. Earlier in the same paragraph, the rewriter is the reader model (Llama3.1-8B-Instruct for MMLU, Qwen2.5-7B-Instruct for GPQA; Table 2 caption, L176).

### Inferences
- In Weave's setting a filled placeholder like "[그날 → 3/15 (일) 저녁]" cannot be right from memory; it must come from hop-1. So the relevant risk for a small on-device model is fabrication or default-filling: the question date, a "typical" weekend, a guessed wine. Large-model memorization of real-world entities is not the issue. Hi-Q's point still applies: end-to-end accuracy can hide this, so bridge provenance has to be checked separately (see §5 and §6).
- Longpre et al.'s size trend suggests that a *smaller* rewriter is less likely to override context with memorized facts. It says nothing about invention when context is missing, and the small-model evidence above says invention and drift are common.

### Gaps
- No study was found that measures how often a ≤4B rewriter fills a bridge with a value absent from the retrieved record, in any language or on personal data. Hi-Q's GPT-5 statement is qualitative ("frequently") and gives no rate.
- No Korean evidence on rewriter hallucination.

## 3. Error propagation across hops, and under-specified sub-queries issued before the bridge is resolved

### Takeaway
A wrong or premature intermediate query is the main way multi-hop pipelines fail. Ordering dependent sub-queries after their prerequisites matters more than any other Hi-Q component: removing dependency awareness costs 10.8 EM on average and 20.0 EM on 2Wiki. Interleaving retrieval with reasoning reduces factual errors versus one-shot retrieval, and this holds even for small Flan-T5 models. Two things limit propagation: returning "unresolved" instead of a guessed value, and verifying splits. Hi-Q reports that a poor split is mostly absorbed rather than propagated when unanswerable sub-queries return ⊥.

### Cited Findings
- [EN] Hi-Q, the failure: "iterative retrieval methods adapt the query over time, but their reformulations are not explicitly checked for evidence support, so an early wrong intermediate query can propagate through later retrieval steps." — LOCAL:hiq L16
- [EN] Hi-Q, dependency ablation (§4.4, Table 6): "Removing dependency awareness causes a larger drop to 47.1 EM / 56.0 F1, because dependent sub-queries can become under-specified when issued before prerequisite facts are resolved." — LOCAL:hiq L245
  - Table 6 EM cells, Hi-Q vs w/o Dependency-aware Decomp.: HotpotQA 64.3 → 62.5; MuSiQue 45.0 → **34.2**; 2Wiki 64.5 → **44.5**; Avg 57.9 → 47.1.
  - Static one-shot decomposition ("w/o Hierarchical Decomp."): Avg 51.5 EM / 63.7 F1.
- [EN] Hi-Q, by hop count: "At 3 and 4 hops, Hi-Q reaches 55.2 and 39.2 F1, compared with 43.4 and 35.4 for IRCoT and 43.1 and 26.9 for PropRAG. This supports the mechanism in Section 3: dependency-ordered resolution mitigates error propagation in deeper chains." — LOCAL:hiq L254
- [EN] Hi-Q, whether early split errors survive: "That the gains are small is itself informative: it indicates that early decomposition errors rarely survive to the final answer. A sub-query that cannot be answered from the corpus returns unresolved rather than committing a wrong intermediate value, so a poor split tends to be absorbed by further refinement or by the verifier instead of being propagated." — LOCAL:hiq L465 (k root decompositions with majority vote; L462)
- [EN] Hi-Q, causes of unresolved triggers in 100 manual cases: "Annotation errors (14%) reflect defective benchmark evidence and malformed sub-queries (10%) are upstream formulation failures ... Only false abstention (7%) and reader failure (3%) do, giving an unambiguous false-trigger rate of 10%". — LOCAL:hiq L224
- [EN] Hi-Q, own limitation: "Reader errors can affect the refinement policy: false abstention may cause over-refinement, while unsupported answer generation may stop refinement too early ... the current binary resolved/unresolved signal does not capture finer states such as partial evidence, conflicting evidence, or multiple competing bridge entities." — LOCAL:hiq L507
- [EN] Hi-Q setup, for context: GPT-4o-mini reader; "NV-Embed-v2, k=5, ... maximum recursion depth d_max=4" (LOCAL:hiq L173). Table 8: Hi-Q (full) **13.5 s**, **5.7** LLM calls per question; IRCoT 6.4 s, 2.92 calls. These are cloud API costs and exclude retrieval.
- [EN] IRCoT, on the interleaving that limits drift: "OneR can retrieve relevant information closest to the question and is less likely to make such errors early on, but it still makes errors later in the CoT. IRCoT, on the other hand, is often able to prevent such errors in each step." — LOCAL:ircot L239
  - Small models: "IRCoT with even the smallest model (0.2B) is better than OneR ... For all sizes except the smallest (0.2B), we see IRCoT QA is better than OneR QA. Moreover, IRCoT with a 3B model even outperforms OneR and NoR with a 58X larger 175B GPT3 model in all datasets." — LOCAL:ircot L245
  - Source inconsistency: the Fig. 8 and Fig. 9 captions call the smallest model "0.3B" (L209, L212), while the text and the size list say "base (0.2B)".
  - Recall gains with Flan-T5-XXL over one-step retrieval: "on HotpotQA by 7.9, on 2WikiMultihopQA by 14.3, on MuSiQue by 3.5, and on IIRC by 10.2 points." — L197
- [EN] EfficientRAG on LLM-based iterative baselines: "they require LLMs to generate partial answers with noisy knowledge inputs, but they always fail in the intermediate steps." — LOCAL:efficientrag L124
- [EN] MDR, decomposition errors: errors "only made by the decomposed system. These errors could be potentially avoided if the model has access to the full information in the original question or previous hop results." — LOCAL:mdr L273 (Table 9 caption)
  - Bridge-question errors: "in half of these cases, our retrieval model predicts an alternative passage sequence that is also valid ... Other remaining errors are due to the dense method’s inability to capture the exact n-gram match between the question and passages ... a hybrid multi-hop retrieval method with both term and dense index might be used". — L141
- [EN] Self-Ask, compositionality gap ([arXiv 2210.03350](https://arxiv.org/abs/2210.03350)).
  - "We measure how often models can correctly answer all sub-problems but not generate the overall solution, a ratio we call the compositionality gap."
  - "the compositionality gap remains at a roughly constant 40% between different model sizes and training techniques".
  - Later models: "estimated at 42.9% for ChatGPT and 23.0% for GPT-4".
  - Hardest categories: "GPT-3 answers only 1.2% of the questions correctly. However, it answers 80% of the sub-questions on this dataset correctly".

### Inferences
- For Weave, the "[그날]" placeholder is the dependency marker that Hi-Q's ablation is about. Issuing hop-2 ("마신 화이트 와인은?") before hop-1 is resolved is exactly the under-specified-sub-query failure. Weave's split into a bridge question plus a placeholder question, resolved strictly in order, is supported by this ablation. It was measured on English Wikipedia QA with GPT-4o-mini.
- The safest propagation behavior is Hi-Q's: if hop-1 has no supported value, return ⊥ ("찾은 단서까지만 보여 주기") rather than a guessed date.

### Gaps
- No measurement of error propagation for ≤4B rewriters in a dependency-ordered pipeline. The IRCoT small-model numbers are recall/F1, not propagation rates.
- No personal-data or Korean propagation study.

## 4. Over-decomposition: always splitting, or splitting into short queries, can hurt

### Takeaway
Decomposition helps when the single query fails, but hurts when applied unconditionally. Hi-Q's always-decompose policy loses 3.4 EM. ReasonIR finds that one information-rich long query beats several decomposed short queries on BRIGHT. MDR finds no gain from oracle decomposition with a strong dense encoder. A learned complexity router that decides before seeing evidence collapsed to "always multi-step". The supported design is: try once, and split only on evidence failure.

### Cited Findings
- [EN] Hi-Q, always-decompose ablation: "replacing the failure-aware trigger with an always-decompose policy reduces performance from 60.7 EM / 70.8 F1 to 57.3 EM / 68.5 F1 on the sampled 100-query setting. This shows that unconditional decomposition fragments already answerable queries ... Because always-decompose is the limiting case of over-triggering, firing on every query, this 3.4-point drop also bounds what any trigger error can cost." — LOCAL:hiq L245
  - Table 6 cells (N=100, EM): HotpotQA 62.0 → 58.0; MuSiQue 49.0 → 45.0; 2Wiki 71.0 → 69.0.
  - The table footnote says 100 queries were used "due to the prohibitive cost of recursive always-decompose". — L248
- [EN] Hi-Q, why: "a query that is already answerable should not be split merely because it looks complex, since unnecessary decomposition can drop constraints and introduce spurious intermediate goals." — LOCAL:hiq L127
  - Binary splits: "Hi-Q splits binary rather than N-ary (multi-way) to avoid over-fragmenting the question or skipping essential intermediate bridge facts". — L140
- [EN] Hi-Q, how often decomposition is needed: "The trigger rate is much lower on HotpotQA (10.7%) than on MuSiQue (45.2%) and 2WikiMHQA (48.6%)". — LOCAL:hiq L420
  - When it fires, it pays off: on Clean triggered MuSiQue cases, all-gold cover goes "from 7.9% to 42.7%" at a matched top-5 budget (Leaf@5), and "Leaf@all reaches 57.7%, with answer recovery of 38.7%". — L215 (Table 3)
- [EN] Hi-Q Appendix D, router that decides before evidence: Adaptive-RAG's classifier routes "959 of the 1,000 questions ... to multi-step retrieval, 41 to single-step, and none to no-retrieval, and a control policy that always selects multi-step scores above Adaptive-RAG itself." — LOCAL:hiq L375
  - Table 9 (Qwen3.6-27B reader; not comparable to the main tables): Adaptive-RAG 26.4 EM; Always multi-step 27.3; Hi-Q 47.9.
- [EN] ReasonIR: "we evaluated a popular query decomposition method implemented by LangChain on BRIGHT and found that it reduces performance from 12.1 to 10.5 with Nomic and 20.4 to 17.3 with GRIT-7B when compared with directly retrieving with the original query ... This indicates that **an information-rich long query is better than several decomposed short queries on BRIGHT**." The same paragraph notes decomposition "has been shown to be effective in multi-hop retrieval tasks ... where the question can be easily decomposed into simple factual sub-queries". — LOCAL:reasonir L74
- [EN] MDR, oracle decomposition with a dense retriever.
  - "we did not observe any strong improvements from explicit question decomposition ... when the 1st hop of the decomposed retrieval (i.e., SubQ1) is replaced with the original question, no performance degradation is observed ... some information in one decomposed subquestion could be useful for the other retrieval hop." — LOCAL:mdr L159
  - Table 4 (100 bridge questions, R@2 / R@10 / R@20): MDR 54.9 / 63.7 / 70.6; Decomp (SubQ1;SubQ2) 50.0 / 64.7 / 67.6; Decomp (Q;SubQ2) 51.0 / 64.7 / 68.6.
  - This "gives advantages to the decomposed method as we ignore any intermediate errors" (oracle bridge inserted). — L153
- [EN] Counterpoint, EfficientRAG: "the number of oracle chunks retrieved by one-time decomposition (LLM Decompose ...) outperforms the Direct retrieval for the original query." — LOCAL:efficientrag L34. Table 2 on MuSiQue: Decompose-R 67.23 recall at K=19.74 chunks vs Direct-R@20 57.12.

### Inferences
- For Weave, single-record questions should not be split. The sequence should be: one retrieval with the original question; then a split only if hop-1 retrieval does not support an answer. The second query should keep the original question's other constraints ("화이트 와인", "마신") alongside the filled bridge, which is MDR's "(Q; SubQ2)" pattern. Keeping the original text in the next-hop query is cheap insurance against dropped constraints.

### Gaps
- No over-decomposition study with ≤4B decomposers, on personal data, or in Korean.
- Weave's own trigger rate (how often hop-1 fails) is unknown. Hi-Q's 10.7–48.6% are Wikipedia QA numbers.

## 5. Safeguards, and the evidence that each works

### Takeaway
The best-supported safeguards are:
- (a) Resolve dependencies in order, and return ⊥ instead of a guess (Hi-Q).
- (b) Keep the original query in the next-hop query, or fall back to it. Expansions/rewrites help weak retrievers but often hurt strong ones.
- (c) Ground fillers in retrieved text: extractive labelers (EfficientRAG), corpus-extracted expansions (CSQE), and strict grounding, which costs about 0 EM in Hi-Q.
- (d) Bounded depth and explicit stop tokens.

Round-trip verification helps mostly at depth: +1.0 F1 at 4 hops, and it repairs 14.8–18.8% of triggered splits. Evidence on constrained decoding/JSON grammars conflicts: it hurts reasoning in one study and helps by up to 4% with Llama-3.1-8B in another. Confidence-based abstention has good numbers only with an LLM reader (Hi-Q FAR 2%, FRR 11%).

### Cited Findings

#### 5a. Extractive / copy constraints (placeholder filled only with spans from the retrieved record)
- [EN] EfficientRAG: the Labeler "annotates preserved tokens "KGOT in the Dimond Center" from the <Continue> chunks" (LOCAL:efficientrag L43). Training labels mark "each word in the chunk with a binary label to determine if it is important and should be preserved" (L70).
  - Model: "fine-tuned based on DeBERTa-v3-large ... with 24 layers and 304M parameters" (L106).
  - Table 2, Recall@K with K = chunks retrieved: HotpotQA **81.84 @ 6.41**; 2WikiMQA **84.08 @ 3.69**; MuSiQue **49.51 @ 6.09**. For comparison, Direct-R@10 is 70.52 / 61.58 / **50.86** and SelfASK is 73.42 @ 35.27 / 88.90 @ 33.68 / 60.43 @ 32.36. On MuSiQue the extractive approach is below plain retrieval at K=10.
- [EN] CSQE ([arXiv 2402.18031](https://arxiv.org/abs/2402.18031)): "CSQE utilizes the relevance assessing capability of LLMs to systematically identify pivotal sentences in the initially-retrieved documents. These corpus-originated texts are subsequently used to expand the query together with LLM-knowledge empowered expansions". The extracted texts "are much less prone to issues such as hallucinations and shortness of long-tail knowledge".
- [EN] Hi-Q strict document-level grounding: 47.6 EM vs 47.5 EM for default Hi-Q (Table 15; see §2).
- [PERS-EN] TimelineQA ([arXiv 2306.01069](https://arxiv.org/abs/2306.01069)): "for atomic queries, an extractive QA system significantly out-performs a state-of-the-art retrieval-augmented QA system."
- [PERS-EN] PerLTQA ([arXiv 2402.16288](https://arxiv.org/abs/2402.16288)), span anchoring in gold data: "We employ exact match techniques and human verification to annotate the start and end positions of memory anchors".
- [EN] Temporal normalization: "detecting only those timexes for which it is feasible to provide a normalization is highly beneficial" ([arXiv 2304.14221](https://arxiv.org/abs/2304.14221)).
- [EN] Counterfactual training against memorized answers: "reduces hallucination to negligible levels" ([arXiv 2109.05052](https://arxiv.org/abs/2109.05052); see §2).

#### 5b. Constrained decoding / JSON grammars
- [EN] Tam et al., "Let Me Speak Freely?" ([arXiv 2408.02442](https://arxiv.org/abs/2408.02442)).
  - "we observe a significant decline in LLMs’ reasoning abilities under format restrictions ... stricter format constraints generally lead to greater performance degradation in reasoning tasks."
  - But: "We hypothesize that JSON-mode improves classification task performance by constraining possible answers resulted in reducing errors in answer selection".
  - On parse failures: "parsing errors, when present, can be effectively mitigated through a simple corrective step."
- [EN] JSONSchemaBench ([arXiv 2501.10868](https://arxiv.org/abs/2501.10868)), with Llama-3.1-8B-Instruct.
  - "Constrained decoding consistently improves the performance of downstream tasks up to 4%, even for tasks with minimal structure like GSM8k."
  - Table 8, GSM8K: LM only 80.1%; Guidance 83.8%; XGrammar 83.7%; Llamacpp 82.4%; Outlines 81.6%. Last Letters: LM only 50.7%; Guidance 54.0%.
  - It records the disagreement: "Kurt [2024b] argued that the performance decline observed in previous studies [Tam et al., 2024] comes from inadequate prompting, insufficient contextual information, and poorly crafted schemas."
  - And the caveat: "Over-constrained grammar engines risk limiting the expressive power of LMs".
- [EN] Small-model format failure without constraints: Zephyr-7B "does not output machine-readable JSON, when there are not enough examples to learn the output format" ([arXiv 2404.07775](https://arxiv.org/abs/2404.07775)).

#### 5c. Verification against the original question
- [EN] Hi-Q, the verifier: it "checks whether resolving q_left followed by q_right would recover the intent of q without adding, omitting, or reordering essential constraints. If the split is inconsistent, V repairs the two sub-queries ...; we allow at most one repair attempt, and if the revised split is still inconsistent, the node is marked non-decomposable and decomposition stops for that branch." — LOCAL:hiq L146
  - Effect: "removing it has a small overall effect, but the gap widens with reasoning depth (Table 7), reaching 1.0 F1 at 4-hop depth on MuSiQue ... The verifier repairs 14.8–18.8% of triggered decompositions". — L245
  - Table 7, F1 with vs without verification: Overall 57.2 vs 56.5; 2-hop 64.3 vs 63.7; 3-hop 55.2 vs 54.4; 4-hop 39.2 vs 38.2.
  - The rewrite is also anchored to the question: "Refinement rewrites the current query from the accumulated history H while keeping it anchored to the original question Q, and it has to precede retrieval because dependent sub-queries often contain references whose meaning is fixed only by earlier steps." — LOCAL:hiq L121
- [EN] CRAG ([arXiv 2401.15884](https://arxiv.org/abs/2401.15884)): "a lightweight retrieval evaluator is designed to assess the overall quality of retrieved documents for a query, returning a confidence degree based on which different knowledge retrieval actions can be triggered." The actions are "{Correct, Incorrect, Ambiguous}".

#### 5d. Confidence thresholds and abstention ("찾은 단서까지만 보여 주기")
- [EN] Hi-Q, trigger and abstention test: FRR and FAR measured "on 100 normal MuSiQue queries and ... 50 adversarially unanswerable MuSiQue queries constructed by replacing answerable conditions following the SQuAD 2.0 methodology". Result: "Table 5 shows FRR = 11% on normal queries ... Hi-Q identifies 49 of 50 as unanswerable, yielding FAR = 2%." — LOCAL:hiq L230
  - Table 5 ⊥ breakdown: normal queries, Missing 7 / Incomplete 4; adversarial, Missing 35 / Incomplete 13 / Conflicting 1, plus 1 hallucinated.
- [EN] Hi-Q Appendix C, calibrated stop/expand: "Platt calibration reduces expected calibration error from 0.111 to 0.082 and decision regret by 0.024 (95% CI [0.005,0.047])." — LOCAL:hiq L366
  - Policies that do not see evidence: "any policy measurable with respect to the query alone incurs a strictly positive regret that no amount of query-only training data can remove". — L134
- [PERS-EN] LongMemEval E.4: "GPT-4o is able to refuse to generate a time range when the question does not have a time reference." The 8B model is not (LOCAL:longmemeval L517). LongMemEval also scores "abstention" as one of its "five core memory abilities" (L19).
- [EN] FLARE ([arXiv 2305.06983](https://arxiv.org/abs/2305.06983)): "we actively trigger retrieval if any token of ŝ_t has a probability lower than a threshold θ∈[0,1]". Its premise: "large LMs tend to be well-calibrated and low probability/confidence often indicates a lack of knowledge". The claim is about *large* LMs.
- [EN] Self-Ask: "as the perplexities assigned to correct sub-question answers decrease (i.e., the model becomes more confident about the correct answers), the probability of answering the compositional question correctly increases." — [arXiv 2210.03350](https://arxiv.org/abs/2210.03350)
- [EN] Abe et al. propose, as future work, "a module that assesses LLM’s knowledge and query ambiguity for adaptive QE." — [arXiv 2505.12694](https://arxiv.org/abs/2505.12694)

#### 5e. Fallback to no-rewrite, or concatenating the question with the retrieved record
- [EN] Weller et al.
  - "there exists a strong negative correlation between retriever performance and gains from expansion: expansion improves scores for weaker models, but generally harms stronger models ... this trend holds across a set of eleven expansion techniques, twelve datasets with diverse distribution shifts, and twenty-four retrieval models."
  - Recipe: "use expansions for weaker models or when the target dataset significantly differs from training corpus in format; otherwise, avoid expansions to keep the relevance signal clear."
  - Exception: "except for long query shift, where expansions generally help most-to-all models." — [arXiv 2309.08541](https://arxiv.org/abs/2309.08541)
- [EN] MDR, vector-level "rewrite" without generation: "we simply concatenate the question and the retrieved passages as the inputs to g(·)" — LOCAL:mdr L51. Replacing SubQ1 with the original question caused "no performance degradation" (LOCAL:mdr L159; Table 4 in §4).
- [EN] Query2doc ([arXiv 2303.07678](https://arxiv.org/abs/2303.07678)): it "concatenates them with the original query to form a new query." For sparse retrieval: "we boost the query term weights by repeating the query n times before concatenating with the pseudo-document d′".
- [PERS-EN] LongMemEval, the risk a fallback guards against: a wrong time range "erroneously prunes out the search space, leading to a low memory recall" (L517).
- [EN] ReasonIR (L191, small rewriter hurts dense retrievers on GPQA) and BRIGHT (L178, LLM queries "are out-of-distribution for trained models") both show that a rewrite can be worse than the original question.

#### 5f. Hop limits and stop rules
- [EN] IRCoT: "If the generated CoT sentence has the ‘‘answer is:’’ string or the maximum number of steps has been reached, we terminate the process". Footnote: "set to 8 in our experiments." — LOCAL:ircot L101, L104. Evaluation caps retrieval at "a maximum of 15 paragraphs for all retriever systems" (L152).
- [EN] Hi-Q.
  - "maximum recursion depth d_max=4" (L173).
  - Bound: "at d_max=4 they permit 31 visited nodes, each costing at least one LLM call, against a measured mean of 5.7 calls per question (Section 4.5), because most nodes resolve without expanding." — L287
  - Depth-1 cap: "Hi-Q (cost-matched) shortens rationales and caps recursion depth at 1 ... At essentially the same number of LLM calls as IRCoT (2.93 versus 2.92), it uses 9.4× fewer input tokens, runs 25% faster ... while improving accuracy by 10.4 EM / 11.6 F1 macro-averaged over the three benchmarks". — L266
- [EN] EfficientRAG uses tags instead of an LLM stop decision: chunks are tagged "<Terminate> or <Continue>" (L43). "Once our approach gets enough information to answer the initial question, it stops" (L58).
  - Table 4 (200 MuSiQue samples): EfficientRAG **1.00 LLM call**, **2.73 iterations**, **3.62 s**; Iter-RetGen iter3: 3.00 / 3.00 / 9.68 s; SelfASK: 7.18 / 3.59 / 27.47 s.

### Inferences
- Concrete guard set for an on-device rewriter (design proposal, not evidence of Weave performance):
  - (1) Fill the placeholder only with a span copied from the cited hop-1 record, or with a deterministic transform of such a span (date resolver). Reject the fill otherwise.
  - (2) Emit a tiny fixed JSON (`{bridge_span, record_id, anchor, type}`) under a grammar. This is a classification/extraction-shaped output, where the evidence favors constraints. Keep any free-text reasoning outside the constrained field.
  - (3) Always also retrieve with the original question, or the MDR-style concatenation, and fuse the results, so a bad rewrite cannot remove the original signal.
  - (4) Apply a time filter only when the question or record contains an explicit time phrase. Drop the filter when it leaves too few candidates.
  - (5) Use at most 2–3 hops with an explicit stop. When the bridge cannot be resolved, show the found clue and stop (Hi-Q ⊥).
- A round-trip check ("does the filled hop-2 question plus the hop-1 answer still ask the original question?") is cheapest as a rule check for Weave's fixed two-slot template: slot-type match, span-in-record, and date within the record's plausible range. LLM verification gave only +0.6 to +1.0 F1 in Hi-Q at 2–4 hops.

### Gaps
- No direct experiment was found on "copy-only" placeholder filling vs free generation for small rewriters. Evidence is indirect (extractive labelers, CSQE, strict grounding).
- Chain-of-Verification ([arXiv 2309.11495](https://arxiv.org/abs/2309.11495)) was downloaded but its numbers were not extracted or verified. It is not used here.
- No study of calibrated abstention for ≤4B rewriters. FLARE's calibration premise is stated for large LMs.
- No on-device (phone NPU) latency numbers for any of these pipelines. Hi-Q latencies are cloud GPT-4o-mini; EfficientRAG's are A100-class GPUs.

## 6. How to evaluate a rewrite-only component, and how to build a synthetic personal-data test set

### Takeaway
Score the rewriter by what it enables downstream, and score each stage separately. Do not score it by similarity to human rewrites, which ConQRR shows are not aligned with retrieval goals. Hi-Q's protocol is a usable template:
- Budget-matched next-hop evidence recall (Leaf@5 vs Root@5; pooled recall inflates with more calls).
- EM/F1.
- Trigger quality (FRR/FAR on answerable vs adversarially unanswerable questions).
- Calls and latency.
- A compositionality-gap style check linking bridge (sub-answer) correctness to the final answer.

Synthetic personal data built with a large LLM works only with heavy human filtering: LongMemEval kept about 5% of LLM-proposed questions, and LoCoMo annotators edited about 15% of dialogue turns. All public personal-memory sets found are English (or Chinese) chat or lifelog text, not Korean multi-app phone records.

### Cited Findings

#### 6a. Metrics
- [EN] Hi-Q evaluation: "EM and token-level F1 measure final QA accuracy, while Recall@k for k∈{2,5} measures whether gold supporting documents appe[ar]". — LOCAL:hiq L167
  - Caveat on pooled recall: "Self-Ask attains the highest average Recall@5, but it issues more sub-queries and retrieves roughly 33% more documents per question than Hi-Q, and because k is applied per retrieval call while recall is computed over the union of all returned passages, more calls buy a larger effective budget at the same nominal k ... Self-Ask accordingly reaches higher average recall with much lower answer accuracy, 35.7 EM against Hi-Q’s 57.9." — L200
  - Budget-matched alternative: "Leaf@5, the top-5 of the leaf-union pool ranked by retriever similarity and therefore budget-matched to root@5". "EM-recov" is "the fraction of triggered cases the system ultimately answers correctly". — L215, L218
- [EN] EfficientRAG reports Recall@K together with K, the number of chunks actually retrieved (Table 2). Efficiency is reported as "LLM calls, iterations, latency, and GPU utilization" on "200 samples from the MusiQue dataset". — LOCAL:efficientrag L130
- [PERS-EN] LongMemEval scores the time-aware query step on retrieval alone: Recall@5/10 and NDCG@5/10 on the temporal-reasoning subset (Table 4). Answers are scored by a GPT-4o judge: "our evaluation prompt still achieves 90% or higher accuracy under all settings" against experts. — LOCAL:longmemeval L373
- [PERS-EN] LoCoMo shows retrieval recall and answer quality diverge for temporal questions. Table 3, RAG GPT-3.5-turbo-16k, Dialog retrieval, top-5: Temporal **R@5 89.2** but Temporal **answer F1 21.3**.
  - Table oddity: the paper prints "247.4" for Multi Hop R@10, which looks like a typo.
- [EN] Self-Ask's compositionality gap (definition in §3) is a ready-made way to relate "sub-answers correct" to "final answer correct".
- [EN] ConQRR, against using human rewrites as references: "humans are usually instructed to rewrite conversational queries to be unambiguous to a human outside the dialogue context, which does not necessarily align with the goal in our task—to optimize the retrieval performance." It optimizes rewrites "towards retrieval performance, using only weak supervision from retrieval". — [arXiv 2112.08558](https://arxiv.org/abs/2112.08558)
- [EN] Training a small rewriter from downstream feedback: "A small language model is adopted as a trainable rewriter to cater to the black-box LLM reader. The rewriter is trained using the feedback of the LLM reader by reinforcement learning." The model: "The trainable model is initialized with the pre-trained T5-large (770M)". — [arXiv 2305.14283](https://arxiv.org/abs/2305.14283)
- [EN] Latency and calls per question, for reference only (cloud, LLM time only): Hi-Q Table 8. "Costs cover reader (LLM) usage only; retrieval and embedding are excluded." — LOCAL:hiq L269

#### 6b. Building synthetic test and training sets with a large LLM
- [EN] EfficientRAG synthesis.
  - "The process consists of multi-hop question decomposition, token labeling, next-hop question filtering, and negative sampling." — LOCAL:efficientrag L64
  - Steps: decompose and "parse the dependency for the sub-questions" (L67); label important chunk words (L70); "Given a single-hop question and the labeled tokens from its dependent questions, we prompt the LLM to generate a next-hop question" (L76); hard negatives, the "most similar but not relevant chunk" tagged <Terminate> (L79).
  - Generator: "Llama-3-70B-Instruct" (L109).
  - Table 1 sizes, Labeler: 357k (HotpotQA) / 93k (MuSiQue) / 70k (2WikiMQA). Filter: 73k / 25k / 13k.
- [PERS-EN] LongMemEval construction.
  - "We define an ontology of 164 user attributes in five categories ... For each attribute, we leverage an LLM to generate attribute-focused user background paragraphs ... As these LLM-proposed questions often lack depth and diversity, human experts manually filter and rewrite all the questions". — LOCAL:longmemeval L94
  - "Llama 3 70B Instruct is used to propose question and answers for each question type ... for the question type temporal-reasoning, multi-session reasoning, and single-session-preference, we use GPT-4o to propose several questions. Nevertheless, we find most of the questions to be unsatisfactory ... approximately 1000 questions were generated for each question type, and the final yield rate is about 5%." — L319
  - Final size: "500 manually created questions" (L19). Time mentions were made colloquial and timestamps added by hand (L106).
- [PERS-EN] LoCoMo ([arXiv 2402.17753](https://arxiv.org/abs/2402.17753)).
  - "a machine-human pipeline to generate high-quality, very long-term dialogues by leveraging LLM-based agent architectures and grounding their dialogues on personas and temporal event graphs ... verified and edited by human annotators".
  - Size: "50 very long-term dialogues, each consisting of 300 turns and 9K tokens on avg., over up to 35 sessions".
  - Human-fix rate: "annotators edited nearly 15% of the dialog turns and removed or substituted approx. 19% images present in the LLM-generated dataset."
- [PERS-EN] PerLTQA ([arXiv 2402.16288](https://arxiv.org/abs/2402.16288)).
  - Size: "a comprehensive benchmark of 8,593 questions for 30 characters".
  - Pipeline: "A six-step process: Step 1. Seed data collection. Step 2. PRO generation. Step 3. SR generation. Step 4. EVT generation. Step 5. DLG generation and Step 6. Validation." Questions: "Utilizing ChatGPT, we generate questions and answers prompted by the memory sentences".
  - Validation: "We conduct random sampling of the generated memory data, identifying types of issues ... and then manually refine the memories."
  - Small-model note: "the BERT ... model excels in memory classification tasks, surpassing LLMs like ChatGLM3 ... and ChatGPT".
- [PERS-EN] TimelineQA ([arXiv 2306.01069](https://arxiv.org/abs/2306.01069)), lifelog generator not driven by an LLM: "The benchmark includes a generator that produces lifelogs for imaginary people with different personas (e.g., age, gender, education and family status)". Episodes "are generated via a model that depends on several probability distributions of episodes".
- [PERS-EN] 2025–2026 additions.
  - PersonaMem ([arXiv 2504.14225](https://arxiv.org/abs/2504.14225)): "over 180 simulated user-LLM interaction histories, each containing up to 60 sessions"; "frontier models such as GPT-4.1, o4-mini, GPT-4.5, o1, or Gemini-2.0 achieving only around 50% overall accuracy".
  - LoCoMo-Plus ([arXiv 2602.10715](https://arxiv.org/abs/2602.10715)): "a benchmark for assessing cognitive memory under cue–trigger semantic disconnect ... conventional string-matching metrics and explicit task-type prompting are misaligned with such scenarios".
  - Beyond Dialogue Time ([arXiv 2601.07468](https://arxiv.org/abs/2601.07468)): dialogue time vs event time (see §1e).
- [EN] Hi-Q's adversarial unanswerable set is reusable for abstention tests. It was built "by replacing answerable conditions following the SQuAD 2.0 methodology". — LOCAL:hiq L230

### Inferences
- Proposed metric set for Weave's rewriter (design, not results). Evaluate with the fixed embedding model and index, and always against three references: original question only; MDR-style question + hop-1 record concatenation; and an oracle rewrite with the gold bridge filled in.
  - (1) Next-hop evidence recall@k, budget-matched and per hop, not pooled.
  - (2) Bridge exact match after normalization, split by slot type (date/time, person, place, item). Also the provenance rate (fill appears in, or is computed from, the cited record).
  - (3) Time-filter metrics: exact-interval match; false-filter rate on questions with no time phrase (the LongMemEval failure); and the "filter excludes gold" rate.
  - (4) Split decision quality: FRR/FAR, and the over-decomposition rate on single-hop questions.
  - (5) End-to-end answer accuracy, plus correct abstention on adversarially unanswerable variants.
  - (6) On-device latency, tokens generated, and calls per question.
- Synthetic Korean phone-record set, combining EfficientRAG, LongMemEval and LoCoMo:
  - A large LLM generates a persona and an event timeline (temporal event graph).
  - It renders per-app records with metadata: KakaoTalk messages with `sent_at` and relative phrases like "이번 일요일 6시", gallery OCR text, payment rows with merchant/time, calendar entries.
  - It then writes multi-hop questions with gold decompositions, gold bridge spans plus record IDs, and gold time intervals.
  - Add time-free questions and SQuAD-2.0-style unanswerable variants.
  - Budget for heavy human filtering: LongMemEval's ~5% yield and LoCoMo's ~15% turn edits are the only quantified references found.

### Gaps
- No public Korean multi-app personal-record multi-hop benchmark was found.
  - Korean long-term dialogue memory datasets appeared only in search snippets and were not verified verbatim: CareCall_mem, from "Keep Me Updated!" ([arXiv 2210.08750](https://arxiv.org/abs/2210.08750)), and KEEM ([arXiv 2601.05548](https://arxiv.org/abs/2601.05548)). The 2210.08750 abstract does not itself say "Korean", so the Korean-language claim is unverified.
- No published metric for "bridge exact match" specifically for rewriters was found. The closest are Self-Ask's compositionality gap and Hi-Q's EM-recov / Leaf@5.
- No benchmark reports on-device latency for multi-hop rewrite pipelines.
