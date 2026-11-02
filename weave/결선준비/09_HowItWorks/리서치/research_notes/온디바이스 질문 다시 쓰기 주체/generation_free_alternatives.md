# Generation-free and lightweight alternatives to an LLM query rewriter (EfficientRAG, MDR, LaSER, hybrids) vs. cloud LLM rewriting, judged for Weave (state as of 2026-11-02)

Reading conventions (not a section):
- `work/<key>/src.txt Lnn` means `/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/<key>/src.txt`, line nn. Those are the verified full texts. Table rows marked "(raw.html Table n)" were extracted cell by cell from `work/<key>/raw.html`, the saved arXiv HTML copy of the same paper version, and are quoted as `cell | cell`. HTML entities such as `&lt;Continue&gt;` are decoded. LaTeX such as `\(r=64,\alpha=32\)` is simplified to plain text.
- **Every benchmark number below is someone else's result on an English public benchmark** (Wikipedia multi-hop QA, StackExchange/BRIGHT, etc.). None of them is Weave's performance. None of the papers evaluates Korean or personal data unless explicitly noted.
- Arithmetic I did myself is labelled "(my arithmetic)" and appears only under **Inferences**.

---

## Q1. EfficientRAG (EMNLP 2024): architecture, model sizes, accuracy vs. LLM-iterative RAG, latency/LLM calls (Table 4), training-data synthesis, limitations

### Takeaway
EfficientRAG drops per-hop LLM rewriting. Two DeBERTa-v3-large token classifiers (24 layers, 304M parameters each) build each hop's query by copying words from the question and the retrieved chunk. On 200 MuSiQue questions this cut LLM calls to 1 and latency to 3.62 s, against 9.68 s (Iter-RetGen) and 27.47 s (SelfAsk). It is close to the LLM-iterative baselines on HotpotQA and 2Wiki but clearly behind on MuSiQue. The paper does not list "extractive-only / no date normalization" as a limitation. That limit follows from the design ("The Filter extracts words and concatenates them"), so it is my inference.

### Cited Findings
**Venue / version**
- ACL Anthology record: "Anthology ID: 2024.emnlp-main.199 … Pages: 3392–3411". [ACL Anthology](https://aclanthology.org/2024.emnlp-main.199/). Local text is arXiv 2408.04259v2 ([arXiv](https://arxiv.org/abs/2408.04259), `work/efficientrag/src.txt` L1).

**Architecture (Labeler & Tagger + Filter)**
- "EfficientRAG consists of two lightweight components: the Labeler & Tagger and the Filter. These components share the same model structure, with the Labeler & Tagger producing outputs from separate heads within the same model and the filter's output comes from another model. Both the Labeler and the Filter function as token-level classifiers, classifying tokens as either true or false." ([`work/efficientrag/src.txt` L52](https://arxiv.org/html/2408.04259v2))
- How the next query is built: "The filter module takes both the labeled tokens and the current query to construct a new query for the next round of retrieval. It is done by replacing the unknown part of the query with labeled tokens (useful information)." (L52)
- When a branch stops: "If the tag indicates there needs more information to answer the query, *i.e.*, tagged as <Continue>, we will add this chunk to a candidate pool, which will be fed to the LLM-based generator to have the final answer. Otherwise, if the document is labeled useless or irrelevant, we stop searching for the successor branches from this query." (L52)
- Heads: "Subsequently, we use one fully connected layer to project the token embedding into a 2-dimensional space, indicating "useful token" and "useless token". Another fully connected layer is adapted to project the average pooling of the sequence embedding into a 2-dimensional space, representing the chunk tag <Continue> and <Terminate>." (L94)
- **Extractive by construction:** "We train EfficientRAGFilter similarly, while its input sequence is the concatenation of query and labeled tokens. The Filter extracts words and concatenates them to formulate the next-hop query." (L94)
- Figure 3 example: "*"Q: How large is the shopping mall where KGOT radio station has its studios? Info: KGOT, in the Dimond Center"*, and annotates the next-hop query tokens *"How large is Dimond Center?"*" (L43)
- Design rationale: "we are inspired by the intuition that the types of relations in multi-hop questions are limited, or significantly fewer compared to the number of entities." (L13)

**Exact model sizes and stack**
- "EfficientRAG Labeler and Filter are fine-tuned based on DeBERTa-v3-large … with 24 layers and 304M parameters. We adopt Llama-3-8B-Instruct for the question-answering stage and all other baselines. We utilize Contriever-MSMARCO … as the retriever for both data synthesis and inference stages." (L106)

**Training-data synthesis (teacher LLM)**
- "We constructed the training data following Section 3.2 with Llama-3-70B-Instruct (Prompts are detailed in Appendix B.2). We trained our model on 4× Nvidia A100 GPUs for about 10 GPU-hours separately, with AdamW … optimizer and a learning rate of 5e-6." (L109)
- Pipeline: "We utilize LLM to synthesize training data for the Labeler and Filter. The process consists of multi-hop question decomposition, token labeling, next-hop question filtering, and negative sampling." (L64)
- "Given a multi-hop question and relevant chunks, we first prompt the LLM to decompose the original question into several single-hop questions. Each single-hop question corresponds to a chunk. Then, we ask the LLM to parse the dependency for the sub-questions." (L67)
- "Given a single-hop question and the labeled tokens from its dependent questions, we prompt the LLM to generate a next-hop question, which is ideally the next query for retrieval. We extract the next-hop question tokens same as the Token Labeling procedure." (L76)
- Amount of synthesized data, columns HotpotQA | MuSiQue | 2WikiMQA: "Labeler | 357k | 93k | 70k" and "Filter | 73k | 25k | 13k" (raw.html Table 1; [arXiv HTML](https://arxiv.org/html/2408.04259v2))
- Teacher prompt constraint, Table 8 (Llama-3 70B): sub_question "MUST NOT contain information more than the original question and its dependencies. NEVER introduce information from documents." (raw.html Table 8)

**Accuracy vs. LLM-based iterative RAG.** Table 3, generator Llama-3-8B-Instruct; columns EM | F1 | Acc for HotpotQA, then MuSiQue, then 2WikiMQA (raw.html Table 3; caption at L88):
- "Direct-R@10 | 38.24 | 44.55 | 44.56 | 13.39 | 18.14 | 17.12 | 26.18 | 31.88 | 32.70"
- "Iter-RetGen iter2 | 55.45 | 59.47 | 59.29 | 26.95 | 29.15 | 26.28 | 43.85 | 49.96 | 49.22"
- "Iter-RetGen iter3 | 56.76 | 60.89 | 57.56 | 28.20 | 30.31 | 25.31 | 43.07 | 49.83 | 46.59"
- "SelfASK | 33.58 | 39.10 | 42.36 | 24.56 | 29.22 | 26.97 | 47.56 | 54.84 | 55.16"
- "EfficientRAG | 50.59 | 57.93 | 57.86 | 16.44 | 21.18 | 20.00 | 44.18 | 51.64 | 53.41"
- Authors' reading: "our EfficientRAG framework achieves the second-highest accuracy on both HotpotQA and 2WikiMQA, and it also performs well on MuSiQue even with low recall." (L121). Acc is judged by GPT-3.5: "We evaluate the model answer with accuracy metric by GPT-3.5" (L22).
- Retrieval, Table 2, columns Recall@K | K per dataset (raw.html Table 2):
  - "EfficientRAG | 81.84 | 6.41 | 49.51 | 6.09 | 84.08 | 3.69"
  - "Iter-RetGen iter3 | 83.05 | 16.42 | 58.26 | 17.19 | 74.29 | 17.32"
  - "SelfASK | 73.42 | 35.27 | 60.43 | 32.36 | 88.90 | 33.68"
  - "Direct-R@10 | 70.52 | 10.00 | 50.86 | 10.00 | 61.58 | 10.00"
- "However, the performance of EfficientRAG on the MuSiQue dataset was less satisfactory. This suboptimal result may be attributed to the smaller number of chunks retrieved and the increased complexity of the dataset." (L118)
- With GPT-3.5-turbo-1106 as generator on 2Wiki, columns EM | F1 | Acc: "EfficientRAG | 49.00 | 56.93 | 61.88" vs "Iter-RetGen iter3 | 49.41 | 60.60 | 60.60" (raw.html Table 5)
- Out-of-domain, columns Test | Train | EM | F1 | Acc:
  - "HotpotQA | 2WikiMQA | 43.38 | 49.70 | 53.38" vs in-domain "HotpotQA | HotpotQA | 50.59 | 57.93 | 57.86"
  - "2WikiMQA | HotpotQA | 44.54 | 51.98 | 56.59" vs "2WikiMQA | 2WikiMQA | 44.18 | 51.64 | 53.41"
  - (raw.html Table 6)
- Recall per chunk budget vs. LLM decomposition (Figure 2, MuSiQue): "When retrieving approximately 20 chunks, the Recall achieved by EfficientRAG Decompose has comparable performance with the LLM Decompose when retrieving around 200 chunks … the LLM endpoint is gpt35-turbo-1106." (L34)

**Latency and LLM calls (Table 4)**
- Setup: "We randomly selected 200 samples from the MusiQue dataset for empirical research and calculated four indicators: LLM calls, iterations, latency, and GPU utilization. As shown in table 4 our method requires fewer iterations and achieves a 60%-80% improvement in time efficiency compared to other iterative methods while maintaining similar GPU utilization." (L130)
- Rows, columns # LLM calls | # Iteration | Latency (s) | GPU utils (%) (raw.html Table 4):
  - "Direct | 1.00 | - | 2.16 | 15.55"
  - "Direct-R | 1.00 | - | 2.47 | 35.05"
  - "Iter-RetGen iter3 | 3.00 | 3.00 | 9.68 | 66.37"
  - "SelfASK | 7.18 | 3.59 | 27.47 | 65.02"
  - "EfficientRAG | 1.00 | 2.73 | 3.62 | 65.55"
- Caption: "EfficientRAG exhibits a speed equivalent to direct retrieval methods and is three times faster than LLM-based baselines while maintaining a similar number of iterations." (L133)

**Stated limitations and data**
- The paper's whole Limitations section: "The EfficientRAG framework can theoretically adapt to other models, but we opt not to implement a larger LLM as the final QnA reasoner due to time and resource limits. We analyze our method mainly on open-domain datasets, as it is hard to identify multi-hop question-answering datasets in in-domain settings." (L163)
- "The datasets used in the training and evaluation come from publicly available sources and do not contain sensitive content such as personal information." (L169)
- What it is replacing: iterative LLM methods "require multiple LLM calls concerning rewriting or generating new queries for the next round of retrieval, thus increasing the latency and cost" and "require dedicated prompting and few-shot examples that might need updating across different scenarios." (L10)

### Inferences
- **Latency** (my arithmetic, from Table 4):
  - 3.62 s against 9.68 s is about 63% less time. Against 27.47 s it is about 87% less. Speed-ups are 2.7× and 7.6×.
  - EfficientRAG minus Direct-R is 1.15 s. That covers 2.73 iterations of retrieval plus Labeler/Filter plus a longer final context, an upper bound of roughly 0.42 s per iteration on their GPU.
  - The paper does not name that GPU, so none of this is a phone figure.
- **"Comparable" holds only partly** (my arithmetic, from Table 3):
  - Acc gaps to the best LLM-iterative baseline: HotpotQA −1.4 (57.86 vs 59.29), 2Wiki −1.75 (53.41 vs 55.16), MuSiQue −7.0 (20.00 vs 26.97).
  - EM gaps are larger: HotpotQA −6.2 (50.59 vs 56.76), MuSiQue −11.8 (16.44 vs 28.20).
  - So "comparable" holds on the GPT-3.5-judged Acc for HotpotQA and 2Wiki, but not for MuSiQue.
  - MuSiQue is the dataset built to force genuine composition. On it, EfficientRAG's recall (49.51 at ~6 chunks) is no better than plain Direct-R@10 (50.86).
- **Extractive-only consequences for Weave** (the paper does not state these; they follow from L52/L94):
  - The next-hop query can contain only tokens that already appear in the question or in labeled chunk spans.
  - So it cannot turn "지난 일요일" into "3/15 (일)". It cannot write a bridge such as "[그날 → 3/15 (일) 저녁]" unless that exact string is in the record text, and it cannot normalize "minji_k" to "민지".
  - Weave's date bridges would therefore have to come from the hop-1 record's **metadata timestamp** via a rule, then go to the metadata filter. The Filter would not produce them.
- **No proactive question writing.** The Filter labels tokens of an existing question, so composing a first question from a GPS place, boarding pass or chat partner is outside the architecture. A template or another model would be needed.
- **Compute.**
  - Two separate backbones: the Labeler/Tagger shares one and the Filter is another, so roughly 2 × 304M parameters. The paper gives no total.
  - The Labeler runs once per retrieved chunk ("annotates a sequence of tokens in this document", L52), so per-hop cost grows with top-k.
- **Korean.**
  - DeBERTa-v3-large is, to my knowledge, an English-pretrained checkpoint (**unverified this session**).
  - A Korean port would need a multilingual or Korean encoder, plus Korean token-label data synthesized by a Korean-capable teacher (the paper used Llama-3-70B-Instruct). That data would have to be synthetic personal-record chains, since real user records cannot be used.

### Gaps
- The text does not name the hardware for Table 4, and it reports no per-component latency for the Labeler and Filter.
- There is no on-device, Korean or personal-data evaluation; the ethics statement confirms no personal information was involved.
- Whether "304M parameters" includes the embedding matrix is unverified. My recollection is that the Hugging Face card describes 304M backbone parameters plus a separate large-vocabulary embedding layer, but I did not re-check it.

---

## Q2. MDR (ICLR 2021): results, how the query vector is updated, limits (hops, hop-ordered training data, beam cost), and related query-vector-update methods (Baleen, BeamDR, 2023–2026 work)

### Takeaway
MDR updates the query by **concatenating the question with the retrieved passage text and re-encoding it** with one shared RoBERTa-base encoder. There is no generation. On HotpotQA it reached R@2 65.9, against 38.3 for DrKIT, and matched the best published accuracy about 10× faster. It is fixed at 2 hops, collapses without hop-ordered training (R@2 17.6 when trained order-agnostic) and uses beam search. Oracle question decomposition did not beat it. The strongest 2025–2026 successor is GRITHopper-7B (EACL 2026). It extends the concatenate-and-re-encode idea to 4 hops and beats GPT-4o-driven decomposition at deeper hops on MuSiQue, but at 7B scale.

### Cited Findings
**MDR query update**
- "In order to reformulate the query representation to account for previous retrieval results at time step t, we simply concatenate the question and the retrieved passages as the inputs to g(·)." ([`work/mdr/src.txt` L51](https://arxiv.org/abs/2009.12756))
- "instead of using a bi-encoder architecture with separately parameterized encoders for queries and passages, we use a shared RoBERTa-base … encoder for both h(·) and g(·)." (L51)
- "Our method iteratively encodes the question and previously retrieved documents as a query vector and retrieves the next relevant documents using efficient MIPS methods." (L22)
- Inference: "Given a question, we use beam search to obtain top-k passage sequence candidates, where the candidates to beam search at each step are generated by MIPS using the query encoder at step t, and the beams are scored by the sum of inner products" (L60)
- Input lengths: "maximum query length at initial hop | 70" and "maximum query length at 2nd hop | 350" (raw.html Table 11)
- Relation to pseudo-relevance feedback: "our system is similar in spirit to pseudo-relevance feedback techniques …, where no additional user interaction is required at the query reformulation stage." (L243)

**MDR results**
- HotpotQA retrieval, columns R@2 | R@10 | R@20 (raw.html Table 1):
  - "MDR | 65.9 | 77.5 | 80.2"
  - "DrKIT | 38.3 | 67.2 | 71.0"
  - "TF-IDF + Linked | 17.3 | 50.0 | 62.7"
- Efficiency: "matching the best published accuracy on HotpotQA while being 10 times faster at inference time" (L4). Measured "with 16 CPU cores and batch size 1" using HNSW: "our method is about 10 times faster than current state-of-the-art systems while achieving a similar level of performance." (L216)
- Bridge-question errors: "This gives an estimated top-1 passage sequence accuracy of about 90%. Other remaining errors are due to the dense method's inability to capture the exact n-gram match between the question and passages. … a hybrid multi-hop retrieval method with both term and dense index might be used to further improve the performance on *bridge* questions." (L141)
- Against oracle (human) decomposition, 100 bridge questions, columns R@2 | R@10 | R@20 (raw.html Table 4):
  - "MDR | 54.9 | 63.7 | 70.6"
  - "Decomp (SubQ1;SubQ2) | 50.0 | 64.7 | 67.6"
  - "Decomp (Q;SubQ2) | 51.0 | 64.7 | 68.6"
  - Conclusion: "our analysis suggests that decomposition approaches might be sub-optimal in the context of dense retrieval with strong pretrained encoders." (L159)

**MDR limits**
- Hop count fixed: "Both datasets assume 2 hops, so we fix n=2 for all experiments." (L75)
- Hop order is needed, and HotpotQA lacks it: "Since HotpotQA does not provide the order of the passage sequences, as a heuristic, we consider the passage that includes the answer span as the final passage." (L75)
- "Respecting the ordering of passages in two hops is essential - training in an order-agnostic manner hardly works at all, and underperforms even the single-hop baseline." (L147)
- Ablation, columns R@2 | R@10 | R@20 (raw.html Table 3):
  - "Full Retrieval Model | 65.9 | 77.5 | 80.2"
  - "- w/o order | 17.6 | 55.6 | 62.3"
  - "- w/o shared encoder | 59.9 | 70.6 | 73.1"
  - "Single-hop | 25.2 | 45.4 | 52.1"
- Training needs a gold passage per step plus hard negatives: "each input query (which at each step consists of a question and previously retrieved passages) is paired with a positive passage and m negative passages … The positive passage is the gold annotated evidence at step t." (L57)
- The stop decision exists only as an appendix add-on: "we add a binary prediction head on top of the question encoder. Once the retriever finishes the 1-hop retrieval, it encodes concatenation of q and p1 and predicts whether to stop retrieval" (L369).
  - Mixing single-hop and multi-hop training costs HotpotQA answer recall. Columns AR@20 | AR@100: "multi-hop only | - | - | 83.4 | 89.4" vs "unified | 79.5 | 86.1 | 78.1 | 83.0" (raw.html Table 13).
- Venue: ICLR 2021 poster, https://iclr.cc/virtual/2021/poster/2806 (from `work/mdr/meta_ko.json`; not re-fetched this session).

**Baleen (NeurIPS 2021 Spotlight): condensed retrieval.** All quotes from the abstract at [arXiv 2101.00436](https://arxiv.org/abs/2101.00436) ("Comments: NeurIPS 2021 (Spotlight)"):
- "To tame the search space, we propose condensed retrieval, a pipeline that summarizes the retrieved passages after each hop into a single compact context."
- "To model complex queries, we introduce a focused late interaction retriever that allows different parts of the same query representation to match disparate relevant passages."
- "Lastly, to infer the hopping dependencies among unordered training passages, we devise latent hop ordering, a weak-supervision strategy in which the trained retriever itself selects the sequence of hops."
- "We evaluate Baleen on retrieval for two-hop question answering and many-hop claim verification, establishing state-of-the-art performance."

**BeamDR (NAACL 2021, pp. 4635–4641).** Quotes from the abstract at [arXiv 2104.05883](https://arxiv.org/abs/2104.05883); [ACL Anthology 2021.naacl-main.368](https://aclanthology.org/2021.naacl-main.368/):
- "we propose a new multi-step retrieval approach (BeamDR) that iteratively forms an evidence chain through beam search in dense representations."
- "When evaluated on multi-hop question answering, BeamDR is competitive to state-of-the-art systems, without using any semi-structured information."
- "Through query composition in dense space, BeamDR captures the implicit relationships between evidence in the reasoning chain."

**GRITHopper-7B (2025–2026).** Quotes from the abstract at [arXiv 2503.07519v2](https://arxiv.org/abs/2503.07519v2) ("Comments: Accepted at EACL 2026 Main Conference"; v2 22 Jan 2026) and the full text at [arXiv HTML v2](https://arxiv.org/html/2503.07519v2).

*Motivation and method*
- "Decomposition-based multi-hop retrieval methods rely on many autoregressive steps to break down complex queries, which breaks end-to-end differentiability and is computationally expensive."
- "GRITHopper combines generative and representational instruction tuning by integrating causal language modeling with dense retrieval training."
- "our encoder-only approach only requires a single forward pass per hop to compute the next dense vector."

*How it characterizes MDR and its successors*
- "MDR offers an efficient and scalable dense retrieval framework by concatenating the query with passages and encoding them into a single vector representation in one model call per iteration."
- "While MDR allows for efficient and scalable retrieval but has limitations in handling complex multi-hop queries that require more hops than 2 and generalizing to unseen datasets."
- "Other works have extended MDR, such as BeamDR by adding beam search and Ma et al. (2024) by extending MDR multi-hop problems longer than 2 hops."

*Open-retrieval MuSiQue results.* Hits@1 at hop 1 | 2 | 3 | 4 | Avg:
- "GRITHopper (ours) 94.25 76.13 55.45 32.10 76.42"
- "MDR 81.75 45.18 - - 63.47"
- "Beam Retriever 88.75 60.70 30.73 12.84 62.80"
- "GPT4o + GRITLM decomposition 81.96 48.53 13.39 1.98 51.81"
- "Qwen 2.5 32B + GRITLM decomposition 82.62 45.72 13.91 1.48 51.06"

*Why LLM decomposition loses specificity (Appendix G)*
- "The decomposed queries from GPT4 and Qwen have a lower Hit@1 rate but get closer to our model at Hits@5, showing that the sub-questions are not necessarily wrong but are not specific enough to retrieve them at Hits@1."
- "(1) A subquestion is asking for too much information (left side), in other words, the sub-question is still multi-hop or (2) underspecified (right side), there is missing information (eg. entities) in the sub-question."

*Latency*
- Per hop, Table 9, in seconds: "GRITHopper 0.13 0.19 0.31 0.52" and "BeamRetriever 0.25 0.27 0.46 0.66".
- End to end, Table 8, columns early stops | overshoots | avg hops | latency/hop (s): "GRITHopper (end-to-end) 347 25 2.41 0.29".
- Full MuSiQue query time, Table 10:
  - "GRITHopper 1× A100 80GB Single pass 6 min 42 s"
  - "GPT-4.0 (4-shot) API + GRITLM (1× A100) Retrieval + LLM API 1 h 24 min 18 s"
  - "Qwen-32B (4-shot) 2× A100 80GB Retrieval + LLM (vLLM + KV cache) 1 h 1 min 11 s"
  - Authors' caveat: "Note that these comparisons are not strictly fair: decomposition-based methods rely on external APIs or multiple GPUs, making the setup and latency less controllable."

*Stated limitations*
- "The computational cost of creating and maintaining dense representations for frequent updates remains for a 7B model significant."
- "its performance on tasks with noisier or less structured retrieval chains (e.g., conversational QA) remains untested"
- "the highest stopping accuracy (75%) is achieved at later checkpoints, whereas the model selected for reporting is chosen based on peak dense retrieval performance, resulting in a slightly lower stopping accuracy of 71.22%."

### Inferences
- **MDR's 2-hop limit is not what binds for Weave**, since Weave is "대개 2홉". These four constraints are:
  1. **Training data.** Weave would need *ordered* Korean chains of (question, hop-1 record, hop-2 record), and order-agnostic training collapses (R@2 17.6 vs 65.9). Baleen's "latent hop ordering" is the published remedy when order is unknown.
  2. **The embedder must be fine-tuned on concatenated inputs.** A general Korean embedding model is not trained to read "question + KakaoTalk message" as a query.
  3. **No visible rewritten question.** The hop-2 query is a vector, so the deck's "[그날 → 3/15 (일) 저녁]" would describe something the system does not literally produce. The deck would need a separate text step, or wording such as "질문과 찾은 기록을 함께 다시 읽어요".
  4. **No exact filter path.** Dates inside the hop-1 record ride inside the vector instead of becoming an exact filter. Weave's "dates → metadata filter" step has to be done separately, from the hop-1 record's metadata.
- **Beam cost** (from L60 and Table 11). With beam B after hop 1, hop 2 costs B more encoder forwards, each on up to ~350 tokens in MDR's setup, plus B ANN searches. On a phone, B = 1–3 keeps hop 2 within a few short encoder passes.
- **Lexical hybrid.** MDR's own error analysis points to failures on exact n-grams (L141). That argues for a lexical channel (BM25) next to dense retrieval for Korean names, store names in OCR text, and amounts.
- **GRITHopper** shows the vector-update approach scales beyond 2 hops and beats GPT-4o decomposition at hops 3–4 on MuSiQue (13.39/1.98 vs 55.45/32.10 Hits@1). But it is a 7B encoder, and its own limitations flag the cost of keeping embeddings fresh under frequent updates, which is exactly a phone receiving new messages all day.

### Gaps
- I found no Korean, personal-record or conversational evaluation for MDR, BeamDR, Baleen or GRITHopper. GRITHopper says conversational QA is "untested".
- I did not capture MDR's beam size in the main experiments or per-hop CPU latency in milliseconds (Figure 3 is a plot only).
- The hardware for GRITHopper Table 9 per-hop latency is not stated in the extracted text. Table 10 uses 1× A100.
- The full reference for "Ma et al. (2024)" (MDR for more than 2 hops) was not resolved. Baleen's condenser design, the FLIPR acronym and HoVer numbers were not verified beyond the abstract. BeamDR's numbers and exact query-composition formula were not verified beyond the abstract.
- I did not survey the PRF-style vector-update line (ANCE-PRF, ColBERT-PRF) or other 2023–2026 MDR variants beyond what GRITHopper cites.

---

## Q3. LaSER (SIGIR 2026) and similar latent-reasoning retrievers: latency vs. rewrite-then-retrieve, backbone sizes, results; does it carry a bridge fact across hops?

### Takeaway
LaSER has the embedder "think" with K = 3 soft latent tokens. These are distilled during training from an explicit-CoT view of the same backbone. On English BRIGHT it slightly beats a rewrite-then-retrieve pipeline at 0.6B (23.1 vs 22.4 nDCG@10) and at 8B (29.3 vs 28.1). It runs at about 0.3% of that pipeline's latency and about 1.7× a plain retriever (A100). **It does not carry a bridge fact across hops.** Its input is the query alone (plus latent tokens), with no retrieved document. So it can replace the per-hop "Reasoning Embedding" but not the bridge-filling rewrite.

### Cited Findings
**Problem and mechanism**
- "existing approaches typically adopt "rewrite-then-retrieve" pipelines to generate explicit Chain-of-Thought (CoT) rationales before retrieval. However, this incurs prohibitive latency." ([`work/laser/src.txt` L4](https://arxiv.org/abs/2603.01425))
- "During inference, LaSER operates exclusively in the **latent-view**. It utilizes the learned latent thinking tokens to encode queries, ensuring the latency matches standard dense retrievers while benefiting from internalized reasoning. Optionally, the model retains the flexibility to accept rewritten queries from external LLMs if available, further adapting to diverse deployment scenarios." (L112)
- **The input is the query only:** "given an input query q, the model first maps the discrete token sequence into dense embeddings" (L121); "The model operates autoregressively, where the input at step j includes the original query and all preceding latent tokens" (L132)
- "The representation of documents v_d are also obtained in the same way. … by limiting the reasoning horizon K (typically K<10), the method achieves inference latency comparable to standard dense retrievers" (L143)

**Backbones, hyperparameters and training data**
- "We conduct experiments using base version of Qwen3 series (0.6B, 4B, 8B) and LLaMA 3.2 series (1B, 3B, 8B). As LLaMA 3.2 does not offer an 8B variant, we utilize LLaMA 3.1-8B … All models are fine-tuned for 1 epoch using LoRA (r=64, α=32) on 4 A100 GPUs … The number of latent thinking steps K is set to 3 for both training and inference phases." (L261)
- "we utilize the synthetic dataset from ReasonEmb … for training, which includes 81k training examples across 12 domains. Each training query accompany with a reasoning path, which is generated by GPT-4o-mini … as a reasoner, serving as the explicit input in our explicit-view." (L225)
- Released checkpoint: [Alibaba-NLP/LaSER-Qwen3-0.6B](https://huggingface.co/Alibaba-NLP/LaSER-Qwen3-0.6B). Page metadata: "base_model:Qwen/Qwen3-0.6B".
- Venue: SIGIR 2026, DOI https://doi.org/10.1145/3805712.3809575 (recorded in `work/laser/meta_ko.json`; I did not re-verify the DOI this session).

**Latency**
- "we evaluate inference latency on a subset of 80 queries from the BRIGHT benchmark, utilizing a single NVIDIA A100 (80GB) GPU. … we employ vLLM … for the inference of external rewriter models in explicit reasoning pipelines, while the native Hugging Face Transformers implementation is used for all retriever backbones (including ours). A batch size of 8 is maintained … LaSER drastically reduces computational costs, incurring only 0.3% of the latency associated with the "rewrite-then-retrieve" pipeline while maintaining comparable retrieval effectiveness. Although LaSER introduces a modest latency overhead compared to the standard base retriever (approximately 1.7×) due to the autoregressive generation of latent thinking tokens, this overhead decreases as model scale increases." (L339)
- Figure 1 caption: "The "Rewrite-then-Retrieve" method uses a 0.6B retriever and a 3B rewriter." (L22)
- The baseline section instead says: "We utilize BGE-Reasoner-Rewriter-7B … to generate rewritten queries as input to the retriever (using the Fair Baseline model) during inference." (L249). **The paper itself is inconsistent here (3B vs 7B rewriter).**
- The rewriter prompt elicits long CoT: "Think step by step to reason and describe what information could be relevant and helpful to address the questions in detail." and "Draft an answer with as many thoughts as you have." (raw.html Table 1)

**Results: BRIGHT, average nDCG@10** (last cell; raw.html Table 3; [arXiv HTML](https://arxiv.org/html/2603.01425v1))
- "Qwen3-Embedding-0.6B | 0.6B | … | 14.4"
- "Fair Baseline (Qwen3-0.6B) | 0.6B | … | 18.3"
- "Rewrite-then-Retrieve (Qwen3-0.6B) † | 0.6B | … | 22.4"
- "GIRCSE (Qwen3-0.6B) | 0.6B | … | 19.1"
- "LaSER (Qwen3-0.6B) | 0.6B | … | 23.1"
- "Fair Baseline (Qwen3-8B) | 8B | … | 25.7"
- "Rewrite-then-Retrieve (Qwen3-8B) † | 8B | … | 28.1"
- "LaSER (Qwen3-8B) | 8B | … | 29.3"
- Text: "on both Qwen3-0.6B and Qwen3-8B backbones, our method outperforms explicit reasoning approaches based on query rewriting (surpassing them by 0.7 and 1.2 points, respectively)" (L288); "LaSER demonstrates superior effectiveness (23.10), even surpassing the computationally intensive rewrite pipeline (22.35)." (L327)
- Ablation, Qwen3-0.6B, BRIGHT nDCG@10 (raw.html Table 5): "LaSER (Qwen3-0.6B) | 23.10", "w/o Latent View | 19.93", "w/o Explicit View | 20.59", "Basic Contrastive Learn. | 18.25"

**Out of domain** (raw.html Table 4)
- BrowseComp-Plus, columns R@5 | R@100 | R@1000:
  - Off-the-shelf "Qwen3-Embedding-0.6B … 8.0 | 29.1 | 64.8"
  - "LaSER (Qwen3-0.6B) … 6.8 | 26.8 | 54.9"
  - "Fair Baseline (Qwen3-0.6B) … 3.5 | 21.3 | 46.9"
- FollowIR-Avg Score: Qwen3-Embedding-0.6B 13.8 vs LaSER (Qwen3-0.6B) 11.5.

**Interaction with explicit rewrites**
- "LaSER demonstrates a significantly larger performance boost from explicit rewrites compared to the Basic baseline across all model sizes (e.g. 3.4 v.s. 1.7 in Qwen3-4B)." (L360)

**Self-assessment and related methods**
- "our method represents only a preliminary step toward fully autonomous latent reasoning." (L366)
- GIRCSE, the contrastive-only latent-token method: "In certain settings (e.g., LLaMA3.2-3B), it yields performance degradations compared to the standard retriever baseline" (L330)
- From GRITHopper's limitations section ([arXiv HTML v2](https://arxiv.org/html/2503.07519v2)), prior decoder-based embedders "focused solely on single-hop retrieval for maximum 2-hop problems using only the question and no further context (e.g., GRITLM…)".

### Inferences
- **Bridge across hops: no.**
  - Nothing retrieved enters LaSER's encoding (L121, L132), so it cannot turn hop-1's "3/15 (일) 저녁" into hop 2's query. It reasons *within* one retrieval call. That matches the Weave split already in `질문다시쓰기_근거.md`: bridge filling is the rewrite step, and semantic links such as '이사 기념 저녁 = 집들이' are the embedder's job.
  - Feeding "hop-2 question + hop-1 record text" into LaSER (MDR-style) is possible in principle but untested. LaSER was trained on query-only inputs.
- **Why the 0.3% ratio overstates the gap to Weave's rewrite.** The baseline generated long CoT rationales (prompt: "as many thoughts as you have"), not a one-line fill like "[그날] 마신 화이트 와인은?". So 0.3% (about 333× faster, my arithmetic) overstates the gap to a short rewrite.
- **Indexing cost on device.** L143 says document vectors are "obtained in the same way". If that includes latent steps on the document side, on-device indexing cost would also rise by up to ~1.7× per record. This is unverified and worth checking in the released code.
- **Gains are domain-bound.** LaSER-0.6B beat its matched fair baseline everywhere. But it stayed below the off-the-shelf Qwen3-Embedding-0.6B on BrowseComp-Plus and FollowIR, so its gains sit mostly in BRIGHT-like domains covered by its 12-domain training data. There is no evidence either way for Korean personal records.

### Gaps
- Absolute latencies in milliseconds appear only in Figure 1 (an image), not in the text.
- It is unresolved which rewriter (3B or 7B) produced the latency comparison.
- LaSER has no multi-hop (bridge) evaluation and no Korean evaluation. I did not verify the language mix of the ReasonEmb training data or Qwen3-0.6B's Korean quality.

---

## Q4. Hybrid designs: is there evidence for combining a small rewriter with a vector-level fallback?

### Takeaway
I found **no paper that evaluates the exact combination** of a small generative or extractive rewriter with an MDR-style vector fallback. The pieces each have evidence:
- A latent-reasoning embedder gains more from explicit rewrites when they are available (LaSER: +3.4 vs +1.7).
- Decomposing only when retrieved evidence is insufficient works. Question-level routing by a small classifier added nothing over a constant policy (Hi-Q, App. D).
- Strong dense multi-hop retrievers match or beat explicit decomposition, because LLM sub-questions are often under-specified (MDR, GRITHopper, ReasonIR).
- Small models can drive interleaved retrieval (IRCoT with Flan-T5 0.7B–11B) or be RL-trained as rewriters.
- Small LLMs are unreliable at time-range extraction (LongMemEval). That argues for rule- or metadata-based date handling.

### Cited Findings
- **Latent embedder + optional rewrites:**
  - "Optionally, the model retains the flexibility to accept rewritten queries from external LLMs if available" (`work/laser/src.txt` L112)
  - "LaSER demonstrates a significantly larger performance boost from explicit rewrites compared to the Basic baseline across all model sizes (e.g. 3.4 v.s. 1.7 in Qwen3-4B)." (L360)
- **Decompose only on evidence failure.**
  - Hi-Q: "a query that single retrieval or a fixed graph already answers is never decomposed" ([`work/hiq/src.txt` L22](https://arxiv.org/abs/2608.30468))
  - Hi-Q ablation: removing dependency awareness drops the average to "47.1 EM / 56.0 F1, because dependent sub-queries can become under-specified when issued before prerequisite facts are resolved." (L245; the full model scores 57.9 EM per the same line)
- **Question-level routing fails** (Hi-Q App. D, shared Qwen3.6-27B reader on MuSiQue-full):
  - "Adaptive-RAG … predicts question complexity before retrieval and selects a global no-, single-, or multi-step strategy. … 959 of the 1,000 questions are routed to multi-step retrieval, 41 to single-step, and none to no-retrieval, and a control policy that always selects multi-step scores above Adaptive-RAG itself. The learned routing decision therefore contributes nothing over a constant policy. Whether a query is resolvable at its current granularity depends on the evidence actually returned, not on the apparent complexity of the original question." (L375)
  - Adaptive-RAG's router is itself a small model: "this selection process is operationalized with a classifier, which is a smaller LM trained to predict the complexity level of incoming queries" ([arXiv 2403.14403](https://arxiv.org/abs/2403.14403), NAACL 2024)
- **Dense multi-hop vs. explicit decomposition:**
  - MDR with oracle decomposition: "MDR | 54.9 | 63.7 | 70.6" vs "Decomp (SubQ1;SubQ2) | 50.0 | 64.7 | 67.6" (`work/mdr/raw.html` Table 4), and "decomposition approaches might be sub-optimal in the context of dense retrieval with strong pretrained encoders" (`work/mdr/src.txt` L159)
  - GRITHopper: GPT-4o decomposition reaches Hits@1 "13.39" at hop 3 and "1.98" at hop 4, against GRITHopper's "55.45" and "32.10" (MuSiQue). Decomposed sub-questions are "not specific enough to retrieve them at Hits@1" ([arXiv HTML v2](https://arxiv.org/html/2503.07519v2))
  - ReasonIR: "we evaluated a popular query decomposition method implemented by LangChain on BRIGHT and found that it reduces performance from 12.1 to 10.5 with Nomic and 20.4 to 17.3 with GRIT-7B when compared with directly retrieving with the original query … This indicates that **an information-rich long query is better than several decomposed short queries on BRIGHT**." ([`work/reasonir/src.txt` L74](https://arxiv.org/abs/2504.20595))
- **Small models as rewriters or step generators:**
  - IRCoT: "Our approach also works on much smaller Flan-T5 models (11B, 3B, and 0.7B) showing similar trends. In particular, we find QA using Flan-T5-XL (3B) with IRCoT even outperforms the 58X larger GPT3 with a one-step question-based retrieval." ([`work/ircot/src.txt` L34](https://aclanthology.org/2023.acl-long.557/))
  - Rewrite-Retrieve-Read (EMNLP 2023): "A small language model is adopted as a trainable rewriter to cater to the black-box LLM reader." and "The rewriter is trained using the feedback of the LLM reader by reinforcement learning." ([arXiv 2305.14283](https://arxiv.org/abs/2305.14283))
- **Dates via filter, and small LLMs mis-extracting them** (LongMemEval): "this simple design improves recall by an average of 11.3% when using rounds as the value and by 6.8% when using sessions as the value. … the effectiveness of this method depends on using a strong LLM for M_T to accurately infer time ranges from queries. Llama 8B, on the other hand, struggles to generate accurate time ranges, often hallucinating or missing temporal cues even with numerous in-context examples." ([`work/longmemeval/src.txt` L247](https://arxiv.org/abs/2410.10813))
- **EfficientRAG is itself a hybrid**: small classifiers build the queries, and one LLM call writes the final answer ("EfficientRAG | 1.00 | 2.73 | 3.62 | 65.55" in Table 4; `work/efficientrag/src.txt` L106).
- **Lexical + dense hybrid suggestion**: MDR L141 (quoted in Q2).

### Inferences
- A design the evidence supports piece by piece. The combination itself is untested.
  1. Run hop 1 on the original question with the reasoning embedder (LaSER-style or equivalent) plus a lexical channel.
  2. **Expand only if the retrieved evidence does not answer** (Hi-Q principle). Don't route on how complex the question looks.
  3. Build hop 2 with the cheapest component that works.
     - (i) If the bridge is a **date or time**, take it from the hop-1 record's metadata timestamp and send it to the filter. No generation is needed, and this sidesteps LongMemEval's small-LLM time-range errors.
     - (ii) If the bridge is a **span in the record** (store name in OCR, product name, person), use an extractive filter, EfficientRAG-style. The UI can then honestly show "[그날 → …]" / "[그 가게 → 바당식당]".
     - (iii) Only if (i) and (ii) fail (normalization or paraphrase needed, or proactive first-question authoring), use a one-line on-device sLLM fill.
  4. As a vector-level fallback, or alongside steps 2–3, encode "question + hop-1 record" MDR-style. This needs an embedder fine-tuned on such inputs. Per GRITHopper and MDR Table 4, this is often *as good as or better than* explicit sub-questions.
- The negative result on question-level routing (Hi-Q App. D) matters for Weave's planned "먼저 한 번 찾고, 답이 없을 때만 나눈다". It supports conditioning on retrieved evidence rather than training a separate complexity classifier.

### Gaps
- I found no study of the exact "small rewriter + vector fallback" combination, and none measuring how often an extractive filter alone suffices for personal-record bridges (dates vs. names vs. paraphrases).
- None of these hybrid results is on Korean data. The Hi-Q routing result uses a 27B reader on English MuSiQue.

---

## Q5. Cloud LLM rewriting baseline: latency, cost, privacy; Samsung Galaxy AI on-device vs. cloud; Apple Private Cloud Compute; implications for rewriting queries that contain personal message content

### Takeaway
- **Cost is not the binding constraint.** At October 2026 list prices, two short cloud rewrites for one 2-hop question cost a few hundredths of a cent (≈ $0.00015–0.00056, my arithmetic with assumed token counts; see Inferences).
- **Latency is about the same as a small on-device model.** Paper setups imply about 1.3–2.4 s of LLM time per call (GPT-4o-mini), before network round-trip. That is similar to a ~3B on-device model generating a one-line rewrite (≈1.7 s with Apple's published iPhone numbers).
- **Privacy is the binding constraint.** The hop-2 rewrite input contains the hop-1 record, e.g. someone's KakaoTalk message or receipt OCR. Samsung offers a "Process data only on device" master switch that turns off cloud processing for Galaxy AI. Samsung's own Knox documentation says cloud-processed features "may be used for model training".
- **The "private cloud" bar is set by Apple PCC and Google Private AI Compute:** stateless processing, no privileged access, non-targetability, and verifiability/attestation.

### Cited Findings
**Latency and cost measured in papers**
- Hi-Q Table 8. Caption: "Computational cost per question, macro-averaged over the three benchmarks. Costs cover reader (LLM) usage only; retrieval and embedding are excluded." ([`work/hiq/src.txt` L269](https://arxiv.org/abs/2608.30468)). Rows, columns Latency (s) | LLM Calls | Input toks | Output toks (raw.html Table 8):
  - "Hi-Q (full) | 13.5 | 5.7 | 12,343 | 558"
  - "Hi-Q (cost-matched) | 4.8 | 2.93 | 4,641 | 131"
  - "IRCoT | 6.4 | 2.92 | 43,701 | 74"
  - "Self-Ask | 8.0 | 6.36 | 4,591 | 98"
  - "Least-to-Most | 11.0 | 5.38 | 6,874 | 424"
  - "PropRAG | 23.1 | 1 | 1,411 | 88"
- Reader model: "All methods use GPT-4o-mini as the reader unless otherwise stated" (`work/hiq/src.txt` L173)
- **Price, with a date:** "GPT-4o-mini list prices ($0.15 and $0.60 per 1M input and output tokens as of August 2026)" (`work/hiq/src.txt` L266)
- **Gemini API pricing page** ("Last updated 2026-10-30 UTC"; [ai.google.dev pricing](https://ai.google.dev/gemini-api/docs/pricing)), paid tier per 1M tokens:
  - gemini-2.5-flash-lite: "Input price (text, image, video) Free of charge $0.10 (text / image / video) $0.30 (audio) Output price (including thinking tokens) Free of charge $0.40"
  - gemini-3.1-flash-lite: "Input price Free of charge $0.25 (text / image / video) $0.50 (audio) Output price (including thinking tokens) Free of charge $1.50"
  - gemini-3.5-flash-lite: "Input price Free of charge $0.30 (text / image / video / audio) Output price (including thinking tokens) Free of charge $2.50"
  - Data use: the free tier lists "Content used to improve our products"; the paid tier lists "Content not used to improve our products"
- GRITHopper, full MuSiQue: GPT-4 API decomposition pipeline "1 h 24 min 18 s" vs "6 min 42 s" for single-pass dense multi-hop. The authors note the comparison is "not strictly fair" ([arXiv HTML v2](https://arxiv.org/html/2503.07519v2), Table 10)
- EfficientRAG (local Llama-3-8B, not cloud): Iter-RetGen iter3 9.68 s and SelfAsk 27.47 s vs EfficientRAG 3.62 s (Table 4, see Q1)
- LaSER: "only 0.3% of the latency associated with the "rewrite-then-retrieve" pipeline" (`work/laser/src.txt` L339)
- **On-device generation reference (Apple, not Samsung)** ([Apple ML Research, 2024-06-10](https://machinelearning.apple.com/research/introducing-apple-foundation-models)):
  - "a ~3 billion parameter on-device language model"
  - "on iPhone 15 Pro we are able to reach time-to-first-token latency of about 0.6 millisecond per prompt token, and a generation rate of 30 tokens per second."

**Samsung Galaxy AI: on-device vs. cloud**
- Samsung US support, "Use features with Galaxy AI" (ANS10000753; no date shown; the device list includes S26 and Z Fold8, so it was updated in 2026) ([Samsung US support](https://www.samsung.com/us/support/answer/ANS10000753/)):
  - "Most translations are handled on the device itself." "Edit Suggestions within the Gallery are handled on-device." "Most other features require a network connection and will utilize the cloud in some way."
  - "Cloud-based functions include : Auto formatting, auto summarizing, auto corrections, and image editing."
  - "Yes, you can disable or only allow on-device processing for the AI features. There is also a "master switch" to disable all cloud-based processing for the Galaxy AI features. To find this, navigate to Settings , then tap Galaxy AI , and then tap the switch by Process data only on device."
- Samsung Newsroom India, "The Knox Journals…", datePublished 2024-05-15 ([Samsung Newsroom](https://news.samsung.com/in/the-knox-journals-stay-in-control-of-your-security-your-data-used-exactly-how-you-see-fit)):
  - "Many of our Galaxy AI features use on-device data processing which means sensitive information stays with you and you alone. For those features that do require processing in the cloud or external servers, we make sure your data is protected with strict policies."
  - "these settings let you decide how much you allow your data to enhance AI experiences and whether you want to allow online processing for full AI functionality. To access the settings, open Settings and select Advanced features, then Advanced intelligence. Here, you'll see the option to "Process data only on device.""
- Samsung Knox docs, "Data processing for Galaxy AI" ("Last updated September 4th, 2026") ([Knox docs](https://docs.samsungknox.com/admin/knox-platform-for-enterprise/knox-service-plugin/configure-advanced-policies/data-processing-for-galaxy-ai/)):
  - "Knox Service Plugin provides you with a way of restricting the features that are cloud-dependent"
  - "AI features that are processed on-device don't use your data for training machine learning models."
  - "Features that process data in the cloud may be used for model training."
  - Policy "Allow process data only on device": "To force AI features in the primary profile (DO) to be processed on the device, set to True."
- From the team's earlier note (**not re-fetched this session**) `리서치/삼성_현재기술_조사.md`:
  - L27 quotes Samsung Newsroom [S1]: "On Galaxy S25, the Personal Data Engine powers personalized AI features by safely analyzing your data on-device…"
  - L35 quotes [S4]: "Personal Data Engine is exclusive to Samsung native apps and is not applicable to third-party applications."

**Apple Private Cloud Compute (2024-06-10)** ([Apple Security Research](https://security.apple.com/blog/private-cloud-compute/))
- "Powerful AI hardware in the data center can fulfill a user's request with large, complex machine learning models — but it requires unencrypted access to the user's request and accompanying personal data."
- "When on-device computation with Apple devices such as iPhone and Mac is possible, the security and privacy advantages are clear" and "However, to process more sophisticated requests, Apple Intelligence needs to be able to enlist help from larger, more complex models in the cloud."
- Stateless computation: "Private Cloud Compute must use the personal user data that it receives exclusively for the purpose of fulfilling the user's request. This data must never be available to anyone other than the user, not even to Apple staff, not even during active processing. And this data must not be retained, including via logging or for debugging, after the response is returned to the user."
- No privileged runtime access: "Private Cloud Compute must not contain privileged interfaces that would enable Apple's site reliability staff to bypass PCC privacy guarantees, even when working to resolve an outage or other severe incident."
- Non-targetability: "An attacker should not be able to attempt to compromise personal data that belongs to specific, targeted Private Cloud Compute users without attempting a broad compromise of the entire PCC system."
- Verifiable transparency: "Security researchers need to be able to verify, with a high degree of confidence, that our privacy and security guarantees for Private Cloud Compute match our public promises."

**Google Private AI Compute (2025-11-11)** ([Google blog](https://blog.google/technology/ai/google-private-ai-compute/))
- "That's why we built Private AI Compute: to unlock the full speed and power of Gemini cloud models for AI experiences, while ensuring your personal data stays private to you and is not accessible to anyone else, not even Google."
- "Remote attestation and encryption are used to connect your device to the hardware-secured sealed cloud environment, allowing Gemini models to securely process your data within a specialized, protected space."
- "Using this technology, Magic Cue is getting even more helpful with more timely suggestions on the latest Pixel 10 phones."

### Inferences
- **Per-call cloud LLM time** (my arithmetic, Hi-Q Table 8): 13.5 / 5.7 ≈ 2.4 s (Hi-Q full), 6.4 / 2.92 ≈ 2.2 s (IRCoT), 8.0 / 6.36 ≈ 1.3 s (Self-Ask).
  - These calls also include reading or answering over large contexts, so a one-line rewrite should be faster.
  - No source includes the network round-trip from Korea, or the extra round-trip per hop that a cloud rewrite adds to a 2-hop query.
- **Cost** (my arithmetic, hypothetical token counts): a Weave-like 2-hop question with 2 rewrite calls of about 600 input and 40 output tokens each costs:
  - gemini-2.5-flash-lite: 1,200 × $0.10/1M + 80 × $0.40/1M ≈ **$0.00015**
  - GPT-4o-mini (Aug-2026 list): ≈ **$0.00023**
  - gemini-3.5-flash-lite: ≈ **$0.00056**
  - For scale, Hi-Q (full) at GPT-4o-mini prices is 12,343 × 0.15/1M + 558 × 0.60/1M ≈ **$0.0022 per question**.
- **On-device sLLM rewrite** (my arithmetic, Apple 3B on iPhone 15 Pro; hypothetical 600-token prompt and 40-token output): 600 × 0.6 ms ≈ 0.36 s prefill + 40 / 30 ≈ 1.33 s decode ≈ **1.7 s per rewrite**.
  - That is the same order as a cloud call, so cloud does not buy speed for a one-line rewrite.
  - Only the generation-free designs (b, c, d) get a hop well below ~1 s; GRITHopper's 0.13–0.19 s per hop on a GPU is the best published reference.
  - This is not a Galaxy measurement.
- **Privacy implications for Weave's rewrite input:**
  1. With "Process data only on device" ON, a cloud rewrite path is unavailable by the user's own choice, so Weave needs a fully on-device path anyway.
  2. Samsung's own wording ("may be used for model training") means "cloud" is not privacy-neutral unless a PCC-like guarantee is published.
  3. The hop-1 record often contains *third parties'* words (KakaoTalk messages from friends). Sending them to a server is a different consent situation from sending the user's own query. Legal analysis was not researched.
  4. Samsung's on-device Personal Data Engine is described as native-apps-only (team note), so KakaoTalk content is outside Samsung's existing on-device personal-data story. Weave's own on-device index is what covers it.
- **If cloud is kept at all,** it fits only as an opt-in fallback with data minimization. Send the question template plus the minimal extracted bridge span (e.g., "3/15 저녁") rather than full message text, and only when the user has not enabled on-device-only mode.

### Gaps
- I found no public Samsung statement on a PCC-style attested private cloud for Galaxy AI. This was not exhaustively searched; Galaxy AI cloud features that rely on Google may fall under Google's terms.
- I found no measured network round-trip from Korea to cloud LLM endpoints, and no Samsung-published tokens/s for Galaxy on-device language models.
- Korean legal analysis (PIPA, including third-party message content sent to a cloud LLM) and cloud data-residency terms were not researched.
- The Samsung US support page shows no date. The menu path differs between 2024 ("Settings > Advanced features > Advanced intelligence") and the current page ("Settings > Galaxy AI"), likely by One UI version.

---

## Q6. Which design fits an on-device, Korean, 2-hop personal-record assistant? (synthesis across b–e)

### Takeaway
No single alternative covers all three rewriting duties: split, bridge-fill, and proactive first question.
- (d) LaSER-style latent reasoning is a good **per-hop embedder** but carries no bridge.
- (c) MDR-style concatenation carries the bridge **without generation** but is invisible as text and needs ordered training chains.
- (b) EfficientRAG-style extraction carries the bridge **as visible text** but cannot normalize dates or relative expressions, and it needs synthetic Korean token labels.
- (e) Cloud LLM does everything but sends personal record content off-device.

The evidence favors a layered on-device design: dates from record metadata go to the filter, entity bridges are copied extractively, a one-line sLLM is used only when normalization is needed, and an MDR-style or latent embedder handles the rest. Cloud should be at most an opt-in, minimized fallback. All supporting numbers are English public benchmarks.

### Cited Findings
- (b) EfficientRAG:
  - 1 LLM call and 3.62 s vs 9.68 s / 27.47 s (Table 4)
  - MuSiQue Acc 20.00 vs 26.97 for SelfASK (Table 3)
  - Extractive Filter: "The Filter extracts words and concatenates them" (`work/efficientrag/src.txt` L94)
  - 2 × DeBERTa-v3-large, 304M (L106); teacher Llama-3-70B-Instruct (L109)
- (c) MDR:
  - "simply concatenate the question and the retrieved passages" (`work/mdr/src.txt` L51)
  - R@2 65.9 vs 38.3 for DrKIT (Table 1)
  - n = 2 fixed (L75); "w/o order" R@2 17.6 (Table 3)
  - GRITHopper: "a single forward pass per hop" and 0.13–0.19 s for hops 1–2 (Table 9) ([arXiv HTML v2](https://arxiv.org/html/2503.07519v2))
- (d) LaSER:
  - Query-only input (`work/laser/src.txt` L121, L132)
  - 23.1 vs 22.4 nDCG@10 at 0.6B (Table 3)
  - 0.3% of pipeline latency and ~1.7× a base retriever (L339)
- (e) Cloud:
  - Hi-Q 13.5 s and 5.7 calls per question; GPT-4o-mini $0.15 / $0.60 per 1M (`work/hiq/src.txt` L266, Table 8)
  - Samsung "master switch" for on-device only ([Samsung US support](https://www.samsung.com/us/support/answer/ANS10000753/))
  - "Features that process data in the cloud may be used for model training." ([Knox docs](https://docs.samsungknox.com/admin/knox-platform-for-enterprise/knox-service-plugin/configure-advanced-policies/data-processing-for-galaxy-ai/))
- Hybrid support: Hi-Q L22 and L375; LaSER L360; MDR L159; LongMemEval L247 (all quoted in Q4).

### Inferences
Comparison grid. Every cell is my judgement from the cited findings above.

| | (b) EfficientRAG-style token classifiers | (c) MDR-style concat + re-encode | (d) LaSER-style latent reasoning | (e) Cloud LLM |
|---|---|---|---|---|
| Text generation at query time | none (span copy) | none | none (3 soft tokens) | yes |
| Extra on-device model | 2 × ~304M encoders | none beyond a fine-tuned embedder | none beyond the embedder | none |
| Latency evidence (English, server GPU/CPU) | 3.62 s/question incl. 1 LLM answer (MuSiQue 200) | ~10× faster than 2020 SOTA systems; GRITHopper 0.13–0.19 s/hop | ~1.7× base encoder; 0.3% of a CoT-rewrite pipeline | ≈1.3–2.4 s per LLM call (derived) + network |
| Accuracy evidence | ≈ LLM-iterative on HotpotQA/2Wiki; −7 Acc on MuSiQue | beats oracle decomposition (MDR); beats GPT-4o decomposition at hops 3–4 (GRITHopper) | +0.7 / +1.2 nDCG@10 over rewrite pipeline (BRIGHT) | most flexible; LLM sub-questions often under-specified for dense retrieval |
| Carries hop-1 bridge into hop 2 | yes, as copied text | yes, inside the vector | **no** | yes, as text |
| Visible "[그날 → …]" text for UI | yes (copied words only) | no | no | yes |
| Normalizes dates / relative expressions | no | no (implicit only) | no | yes (small LLMs err on time ranges: LongMemEval) |
| Writes proactive first question from GPS/boarding pass/chat partner | no | partial (concatenate context strings) | no | yes |
| Training need | LLM-synthesized decomposition + token labels | hop-ordered chains (order essential) | CoT-annotated queries (GPT-4o-mini) | none (prompting) |
| Korean evidence | none | none | none | none found (not tested here) |
| Privacy | on device | on device | on device | record content leaves device; off if "Process data only on device" |

Fit judgement for Weave:
- **Per-hop retrieval:** a reasoning embedder, LaSER-style or similar, plus a lexical channel (MDR L141).
- **Bridge for dates:** take it from hop-1 record metadata and send it to the filter, with no model needed. LongMemEval shows small LLMs mis-extract time ranges.
- **Bridge for entities:** use an extractive span copy (EfficientRAG idea). It is cheap and keeps the UI's visible rewritten question honest.
- **Normalization or proactive first questions:** use a one-line on-device sLLM, only when needed. Its latency is the same order as a cloud call (~1.7 s on Apple's 3B reference).
- **Vector-level fallback:** encode "question + hop-1 record" MDR-style. This requires fine-tuning on Korean ordered chains, which would have to be synthetic.
- **Cloud:** only opt-in and minimized, never by default for message content.
- The deck's current wording ("다시 써요") stays accurate for this layered design. Calling the whole step "LLM rewriting" or "생성 없음" would not be accurate.

### Gaps
- None of the alternatives has been evaluated on Korean, personal, multi-source (chat + OCR + payments + calendar) records. All accuracy and latency figures above are English Wikipedia or StackExchange-style benchmarks on server hardware.
- There are no Galaxy-device measurements for any of these components.
- I found no study testing the proposed layered combination end to end.
