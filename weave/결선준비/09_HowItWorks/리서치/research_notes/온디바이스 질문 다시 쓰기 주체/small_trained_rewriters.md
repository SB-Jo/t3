# Can a small (≤4B) model trained only to rewrite or decompose queries match a large LLM for multi-hop retrieval? Evidence notes (as of 2026-11-02)

How to read these notes:
- **Benchmarks.** Every number comes from a public benchmark in the cited paper: English Wikipedia or web QA, English conversational search, or BRIGHT. The only exceptions are items in Q6 marked **Korean**.
- **Not Weave data.** None of the numbers were measured on Weave or on personal data (chats, OCR text from photos, notes, payments). None should be presented as Weave's performance.
- **Labels.** "Computed" means my own arithmetic on the quoted numbers. "Unverified" means I could not find the original text.
- **Versions.** arXiv versions are pinned because several papers changed their numbers between versions.
- **Local sources.** These are cited as `논문스터디/work/<key>/src.txt` plus a line number (L#).

## Q1. Rewrite-Retrieve-Read (Ma et al., EMNLP 2023): rewriter size, training, exact results

### Takeaway
The trainable rewriter in Rewrite-Retrieve-Read was **T5-large (770M)**. It was trained in two stages: first supervised fine-tuning on ChatGPT rewrites, keeping only rewrites that led the reader to a correct answer; then PPO with reward = EM + F1 + answer-hit. The reader (ChatGPT) and the retriever (Bing) were frozen. The T5 rewriter beat the few-shot ChatGPT rewriter by about 1.4–1.6 EM on HotpotQA and AmbigNQ and lost by 0.28 EM on PopQA. This is evidence for *parity* in **single-shot** rewriting, not for iterative multi-hop retrieval.

### Cited Findings
- **Rewriter size:** "The trainable model is initialized with the pre-trained T5-large (770M) Raffel et al. 2020, denoted as trainable rewriter" — [EMNLP 2023 PDF §3.2](https://aclanthology.org/2023.emnlp-main.322.pdf); same text in [arXiv 2305.14283 (ar5iv)](https://ar5iv.labs.arxiv.org/html/2305.14283)
- **Two stages:** "The rewriter is first trained on pseudo data to warm up (§3.2.1), then continually trained by reinforcement learning (§3.2.2)." — [EMNLP 2023 PDF](https://aclanthology.org/2023.emnlp-main.322.pdf)
- **SFT warm-up data:** "we prompt the LLM to rewrite the original questions x in the training set and collect the generated queries x̃ as pseudo labels. The collected samples are then filtered: Those that get correct predictions from the LLM reader are selected into the warm-up dataset" — [EMNLP 2023 PDF](https://aclanthology.org/2023.emnlp-main.322.pdf)
- **RL stage:**
  - Algorithm: "We adopt Proximal Policy Optimization (PPO)".
  - Reward: "The total reward is a weighted sum of EM, F1, and Hit", where Hit means "reward if the retrieved content hits the answer and penalize if misses the answer".
  - Source: [ar5iv 2305.14283](https://ar5iv.labs.arxiv.org/html/2305.14283)
- **Authors' caveat about the small rewriter:** "The rewriter model after warm-up shows modest performance, which depends on the pseudo data quality and rewriter capability. … The relatively small scale of the rewriter size is also a limitation of the performance after the warm-up." — [ar5iv 2305.14283](https://ar5iv.labs.arxiv.org/html/2305.14283)
- **Setup:**
  - Datasets: "open-domain QA (HotpoQA …, AmbigNQ …, PopQA …) and multiple choice QA (MMLU …)".
  - Readers: "ChatGPT (gpt-3.5-turbo) and Vicuna-13B".
  - For open-domain QA: "We use ChatGPT for both the reader and the frozen rewriter".
  - Retrieval: "With Bing API, the retrieval is performed in two approaches".
  - Source: [ar5iv 2305.14283](https://ar5iv.labs.arxiv.org/html/2305.14283)
- **Table 2, open-domain QA with the ChatGPT reader.** Values are identical in the EMNLP PDF and the ar5iv rendering. Source: [EMNLP 2023 PDF, Table 2](https://aclanthology.org/2023.emnlp-main.322.pdf)

  | Method (EM / F1) | HotpotQA | AmbigNQ | PopQA |
  |---|---|---|---|
  | Direct (no retrieval) | 32.36 / 43.05 | 42.10 / 53.05 | 41.94 / 44.61 |
  | Retrieve-then-read | 30.47 / 41.34 | 45.80 / 58.50 | 43.20 / 47.53 |
  | LLM rewriter (ChatGPT, few-shot) | 32.80 / 43.85 | 46.40 / 58.74 | 46.00 / 49.74 |
  | Trainable rewriter (T5-large) | 34.38 / 45.97 | 47.80 / 60.71 | 45.72 / 49.51 |

- **Authors' reading of Table 2:** "On HotpotQA, the standard retrieval hurts the reader. … This suggests that multi-hop questions are not suitable queries for the web search engine." — [ar5iv 2305.14283](https://ar5iv.labs.arxiv.org/html/2305.14283)
- **PopQA loss:**
  - "On PopQA, our trainable rewriter surpasses standard retrieval while being inferior to the LLM rewriter. This indicates that the distillation of query rewriting is sub-optimal."
  - On deciding when *not* to retrieve: "LLM rewriter knows better when the retrieval is needed for itself as a reader … the F1 score of the LLM rewriter is 71.9% and the T5 rewriter score is 67.1%."
  - Source: [ar5iv 2305.14283](https://ar5iv.labs.arxiv.org/html/2305.14283)
- **Table 3, MMLU EM** (Humanities / STEM / Other / Social).
  - With the Vicuna-13B reader:
    - Direct: 39.8/34.9/50.2/46.6
    - Retrieve-then-read: 40.2/39.8/55.2/50.6
    - LLM rewriter: 42.0/41.5/57.1/52.2
    - Trainable rewriter: 43.2/40.9/59.3/51.2
  - With the ChatGPT reader there is **no trainable-rewriter row**:
    - Direct: 75.6/58.8/69.0/71.6
    - Retrieve-then-read: 76.7/63.3/70.0/78.2
    - LLM rewriter: 77.0/63.5/72.6/76.4
  - Source: [EMNLP 2023 PDF, Table 3](https://aclanthology.org/2023.emnlp-main.322.pdf)
- **Table 4, retrieval analysis on AmbigNQ** (BM25 content selection):
  - Hit ratio: 76.4 (retrieve-then-read) → 77.5 (LLM rewriter) → 82.2 (trainable rewriter).
  - EM: 45.80 → 46.40 → 47.80.
  - "the improvement in the hit rate of the retriever is more significant than the improvement in the reader."
  - Source: [ar5iv 2305.14283](https://ar5iv.labs.arxiv.org/html/2305.14283)
- **Scope limitation stated by the authors:** "our motivation is to enhance the one-turn retriever-then-read framework with a trainable query rewriter". They contrast this with agents that "generates follow-up questions". They also write: "Adding a training process, the scalability to direct transfer is compromised". — [ar5iv 2305.14283, Limitations](https://ar5iv.labs.arxiv.org/html/2305.14283)

### Inferences
- **Margins are small.** Computed: trainable vs. LLM rewriter = +1.58 EM (HotpotQA), +1.40 EM (AmbigNQ), −0.28 EM (PopQA). No seeds or confidence intervals are reported. This supports "a sub-1B trained rewriter ≈ a ChatGPT rewriter for one-shot query rewriting", not "better".
- **The recipe transfers to Weave as a training plan.** The recipe is: SFT on teacher rewrites filtered by downstream success, then RL on a retrieval or reader reward. However:
  - RRR rewrites once, against a web engine, with a large reader.
  - Weave instead fills a placeholder after hop 1 and searches its own embedding index.
- **"When to rewrite" may need a separate decision.** The PopQA "None" result suggests small rewriters are weaker at deciding whether to retrieve at all than at writing the rewrite. Weave already gates rewriting on one-shot failure; that gate should probably stay a separate signal rather than a decision left to the small rewriter.

### Gaps
- RRR has no size ablation (T5-large only), no variance, no iterative or 2-hop rewriting, and no non-English data.
- RRR does not compare against GPT-4-class rewriters.

## Q2. Conversational query rewriting (CANARD, QReCC, TREC CAsT, TopiOCQA): small rewriters vs. LLM rewriters

### Takeaway
Conversational query rewriting is the closest public analog to filling "[그날 → 3/15]": resolving references and ellipsis from earlier context.
- **Surface similarity to human rewrites.** Small fine-tuned seq2seq models nearly match human rewrites: T5-base (220M) reaches 58.08 BLEU vs. human 59.92 on CANARD.
- **Retrieval quality.** They trail human rewrites: QReCC BM25 MRR is 33.67 for T5QR vs. 39.81 for human rewrites.
- **Prompted ChatGPT rewriters** beat both T5QR and human rewrites on QReCC and CAsT.
- **3B with retrieval-reward RL.** In 2025, 3B models trained this way (ConvSearch-R1) beat the ChatGPT-based rewriters: QReCC BM25 MRR@3 is 56.5 vs. 47.8–48.9. The cost is about 386 output tokens per rewrite, because the model reasons before rewriting.
- **Against:** on the TREC-Conv subset of the QReCC test set, ChatGPT rewrites did *worse* than T5QR. Domain shift matters.

### Cited Findings
- **CANARD (Elgohary et al., EMNLP 2019).** Source: [CANARD PDF](https://aclanthology.org/D19-1605.pdf)
  - Splits: test = "5,571 question-in-context and corresponding rewrite pairs", dev = 3,418, train = 31,538.
  - Table 3 BLEU (dev/test):

    | Method | Dev | Test |
    |---|---|---|
    | Copy | 33.84 | 36.25 |
    | Pronoun Sub | 47.72 | 47.44 |
    | Seq2Seq (bi-LSTM with attention + copy) | 51.37 | 49.67 |
    | Human Rewrites* | 59.92 | – |

  - "Seq2Seq improves up to four points over naive baselines but still well below human accuracy. Human accuracy (*) is computed from a small subset of the validation set."
- **Lin et al. 2020, T5 for conversational query rewriting** ([arXiv 2004.01909 via ar5iv](https://ar5iv.labs.arxiv.org/html/2004.01909)):
  - T5-base has "220M" parameters.
  - "in the CANARD test set, T5 beats the other neural S2S models with 58.08 BLEU, which is close to human performance, 59.92. Furthermore, on CAsT, T5 achieves the highest BLEU score (75.07), four points better than the second-best model (71.21)."
  - "T5 with a beam width of 10 achieves a BLEU score that is on par with human performance on the CANARD test set and reaches 76.22 on CAsT."
  - CAsT is zero-shot transfer: "we directly use the model trained on CANARD to perform CQR on the CAsT dataset."
- **QReCC (Anantha et al., NAACL 2021).** Source: [arXiv 2010.04898v3](https://arxiv.org/pdf/2010.04898v3)
  - Table 4, quality of the best rewriting model (ROUGE-1 R / USE / R@10):
    - Transformer++: "89.5% ± 0.4%" / "95.2% ± 0.2%" / "83.2% ± 0.3%"
    - Human*: "94.6% ± 0.2%" / "97.3% ± 0.1%" / "87.2% ± 0.1%"
    - AllenAI Coref: "67.1%" ROUGE-1 R
  - Table 5, passage retrieval (MRR / R@10 / R@100):
    - Original question: 0.0343 / 6.12 / 11.71
    - Transformer++ rewrite: 0.1586 / 26.52 / 41.51
    - Human rewrite: 0.1994 / 32.78 / 49.36
- **InfoCQR (Ye et al., Findings EMNLP 2023).** Source: [arXiv 2310.09716v2](https://arxiv.org/pdf/2310.09716v2)
  - Models:
    - Rewriting LLM: "ChatGPT (gpt-3.5-turbo)".
    - T5QR "fine-tunes the T5-base model".
  - QReCC test set, BM25 (MRR / MAP / R@10):
    - Original: 9.30 / 8.87 / 15.50
    - Human: 39.81 / 38.45 / 62.65
    - T5QR: 33.67 / 32.50 / 53.68
    - ChatGPT zero-shot RW(ZSL): 42.63 / 41.31 / 60.46
    - ChatGPT few-shot RW(FSL): 46.96 / 45.53 / 65.57
    - ChatGPT rewrite-then-edit ED(Self): 49.39 / 47.89 / 67.01
  - TREC-Conv subset (371 queries), BM25 MRR:
    - Human 27.34
    - T5QR 25.23
    - RW(FSL) 19.02
    - ED(Self) 17.43
    - Here the ChatGPT rewrites are below T5QR.
  - Distillation into T5-base: "we sample 10K training instances and employ RW(FSL) and ED(Self) to generate labels for fine-tuning the T5QR model … We find that distillation outperforms using human rewrites as labels on the QReCC test set. Notably, distillation with only 10K training instances can achieve superior results than directly utilizing human rewrites as search queries in terms of MRR and MAP. … However, for TREC-Conv, fine-tuning with human rewrites leads to better outcomes."
- **LLM4CS (Mao et al., Findings EMNLP 2023).** Source: [arXiv 2303.06573v2](https://arxiv.org/pdf/2303.06573v2)
  - "We use the OpenAI gpt3.5-turbo-16k as our LLM."
  - Table 2, ANCE dense retrieval, NDCG@3 on CAsT-19 / CAsT-20 / CAsT-21:
    - T5QR: 0.417 / 0.299 / 0.330
    - ConvGQR: 0.434 / 0.331 / 0.273
    - LLM4CS: 0.515 / 0.455 / 0.492
    - Human: 0.461 / 0.422 / 0.502
  - The headline LLM4CS result combines several outputs: "the RAR prompting method, the Mean aggregation method, and our tailored CoT".
  - Single-rewrite prompting (REW) alone: "0.380 vs. 0.350 on CAsT-20 and 0.465 vs. 0.385 on CAsT-21" vs. the best existing baselines.
- **ConvSearch-R1 (Zhu et al., 2025).** Source: [arXiv 2505.15776v2](https://arxiv.org/html/2505.15776v2)
  - Backbones: "We employ Llama3.2-3B and Qwen2.5-3B as the backbone models for our rewrite."
  - No human or LLM rewrite labels: "the first self-driven framework that completely eliminates dependency on external rewrite supervision".
  - Warm-up: "Only the top-ranked (rank-1) rewrites are retained and used to fine-tune the π_init".
  - Then "RL with rank-incentive reward shaping".
  - Output format: "<think> reasoning process here </think>\n<rewrite> rewrite here </rewrite>".
  - Table 1, MRR@3:

    "–" means the table reports no value (TopiOCQA has no human rewrites).

    | Method | QReCC, BM25 | TopiOCQA, ANCE | QReCC, ANCE |
    |---|---|---|---|
    | Human rewrite | 39.8 | – | 38.4 |
    | T5QR | 33.4 | 23.0 | 34.5 |
    | ConvGQR | 44.1 | 25.6 | 42.0 |
    | LLM4CS | 47.8 | 27.7 | 44.8 |
    | InfoCQR | 48.9 | – | 43.9 |
    | CHIQ-Fusion | 54.3 | 38.0 | 47.2 |
    | ADACQR | 55.1 | 38.5 | 45.8 |
    | Qwen2.5-3B, untrained | 27.3 | 19.2 | 29.3 |
    | ConvSearch-R1, Qwen2.5-3B | 56.5 | 51.4 | 49.7 |
    | ConvSearch-R1, Llama3.2-3B | 55.9 | 50.5 | 50.2 |

  - Abstract: "achieving over 10% improvement on the challenging TopiOCQA dataset while using smaller 3B parameter models without any external supervision."
  - Table 9, CAsT-19 with ANCE, MRR@3 / NDCG@3:
    - Human 74.0 / 46.1
    - T5QR 70.1 / 41.7
    - LLM4CS 70.4 / 46.8
    - CHIQ-Fusion 73.3 / 50.5
    - ConvSearch-R1 76.6 / 54.0
  - Scaling: "even when using a relatively small 0.5B parameter model under dense (ANCE) retrieval, our approach still significantly surpasses the SOTA baseline". The values are shown only in a figure.
  - Table 10, latency under vLLM:
    - ConvSearch-R1 (3B) averages **386** output tokens per sample on TopiOCQA and **387** on QReCC, at 0.049 s and 0.053 s per sample.
    - RETPO (7B): 108 / 107 tokens.
    - Qwen2.5-3B (CoT): 127 / 131 tokens.
    - DS-R1-Distill-Qwen-7B: 435 / 418 tokens.
  - Authors' caveat: "ConvSearch-R1 incorporates a reasoning-based paradigm, leading to longer output sequences and potentially higher inference cost."
- **Unresolved discrepancy.** LLM4CS reports CAsT-19 NDCG@3 = 0.515 in its own paper ([LLM4CS](https://arxiv.org/pdf/2303.06573v2)) but 46.8 in ConvSearch-R1's Table 9 ([ConvSearch-R1](https://arxiv.org/html/2505.15776v2)). The two papers probably used different LLM4CS configurations.

### Inferences
- **For a small rewrite-only model.** On the public English task closest to Weave's placeholder fill (rewrite a context-dependent question into a standalone one), a 3B model trained against the *target retriever* beats prompted ChatGPT rewriters. Supervised imitation of human rewrites (T5QR) is not enough, because human rewrites are not retrieval-optimal (InfoCQR).
- **Against.** The ChatGPT rewriter fell below T5QR on the TREC-Conv subset, and distillation helped on QReCC but not on TREC-Conv. Gains are domain-specific. Weave's domain (Korean personal records, OCR text, dates) is out of distribution for all of these.
- **Output length conflicts with Weave's budget.** ConvSearch-R1's reasoning outputs (about 386 tokens) are more than 10× Weave's 10–30-token rewrites. Whether the RL gains survive with a rewrite-only output (no think block) is untested. The authors offer only the latency comparison above.

### Gaps
- No conversational rewriting benchmark tests normalization of a relative or exact date into a filter value (e.g., "그날" → "3/15 (일) 저녁"). CANARD and QReCC cover entity coreference and ellipsis.
- No on-device or phone latency figures exist. ConvSearch-R1's latency is measured on GPUs with vLLM.
- No Korean conversational rewriting benchmark was found (see Q6).

## Q3. Small models trained with RL for search or query generation (2025–2026)

### Takeaway
- **3B works, but less well than 7B.** Every major RL search paper trains 3B models, and 3B agents do beat one-shot RAG with the same small model on multi-hop QA. The authors themselves state that gains shrink at smaller scale.
- **Best 3B results by mid-2026.** In one shared comparison (Plan Before Search, Table 1), the best 3B agent averages about 0.37 EM on HotpotQA/2Wiki/MuSiQue/Bamboogle, vs. 0.152 for naive RAG with the same 3B model.
- **At 1.5B, low-budget RL suffers "retrieval collapse".** The model learns to answer without searching. Expert seeding fixes it (DAVID-GRPO).
- **Rewrite-only RL models at 1.5–3B match GPT-4o-class query generation** on single-hop or reasoning-heavy retrieval (DeepRetrieval at 3B, TongSearch-QR at 1.5B). Orion's 1.2B iterative searcher beats retrievers up to 200–400× larger, but is not compared against GPT-4o query writing.
- **A small agent is not automatically a good query generator for another reader.** In s3's diagnostic, documents found by a 3B Search-R1 and passed to a frozen 7B reader did *worse* than plain one-shot E5 retrieval.

### Cited Findings

**Search-R1 (Jin et al., 2025)**, source: [arXiv 2503.09516v5](https://arxiv.org/html/2503.09516v5)
- **Sizes:**
  - "We conduct experiments using two types of models: Qwen-2.5-3B (Base/Instruct) and Qwen-2.5-7B (Base/Instruct)".
  - Appendix C adds 14B.
- **Training:**
  - "we merge the training sets of NQ and HotpotQA"
  - "Training is performed on a single node with 8 H100 GPUs."
  - Retrieval: "E5 … as the retriever", 3 passages.
- **Headline gain, which is stated inconsistently:**
  - The abstract says "Search-R1 improves performance by 41% (Qwen2.5-7B) and 20% (Qwen2.5-3B) over various RAG baselines under the same setting".
  - Section 4.4 says "We achieve 24% and 20% average relative improvement with Qwen2.5-7B and Qwen2.5-3B, respectively."
  - Computed from Table 2: 7B-base 0.431 vs. RAG 0.304 = +41.8%; vs. rejection sampling 0.348 = +23.9%; 3B-instruct 0.325 vs. RAG 0.270 = +20.4%. The abstract therefore compares against RAG and the body against the best baseline.
- **Table 2, 3B rows** (EM; HotpotQA / 2wiki / Musique / Bamboogle / 7-dataset average):
  - RAG: 0.255 / 0.226 / 0.047 / 0.080 / 0.270
  - Search-R1-base: 0.284 / 0.273 / 0.049 / 0.088 / 0.303
  - Search-R1-instruct: 0.324 / 0.319 / 0.103 / 0.264 / 0.325
- **Table 2, 7B row for comparison:** Search-R1-base 0.433 / 0.382 / 0.196 / 0.432 / 0.431.
- **Authors' caveats:**
  - "(4) Larger models are better on learning how to do search. Search-R1 on 7B model shows much larger “performance gap” compared with 3B model".
  - "GRPO leads to reward collapse after training for many steps, whereas PPO remains stable."
  - Failure case, Table 16: "Search-R1 failed to write the right queries to decompose a complex problem at the beginning. The model answer the question without obtaining enough evidence."
  - Failure case, Table 11: "Search-R1 sometimes fail to decompose the complex problem and can be mislead by irrelevent searched passages." (Typos are in the original.)

**Empirical study of RL search agents (Jin et al., 2025)**, source: [arXiv 2505.15117v1](https://arxiv.org/html/2505.15117v1)
- **Scale study:** "we train Qwen2.5 models of varying sizes (3B, 7B, 14B, 32B) on the NQ and HotpotQA training datasets using the GRPO algorithm … evaluate on the out-of-distribution Bamboogle dataset."
- **Results:**
  - "the training reward consistently improves with increasing LLM size, indicating that larger models are better able to learn effective reasoning and search engine usage."
  - "While test performance also improves with model size, the rate of improvement diminishes. This suggests that the search agent task, unlike pure language modeling, relies less on parametric knowledge stored in large LLMs, and more on effective external information acquisition through retrieval."
- **Search engine quality during training matters:** "Training with a non-informative search engine (e.g., random noise) leads the agent to avoid retrieval altogether, while a weak engine (e.g., BM25 [33]) results in frequent but less efficient search calls."

**DeepRetrieval (Jiang et al., 2025)**: RL on retrieval metrics, query generation only. Source: [arXiv 2503.00223v3](https://arxiv.org/html/2503.00223v3)
- Abstract: "trains LLMs for query generation through trial and error without supervised data (reference query). Using retrieval metrics as rewards …"
- Literature search: "65.07% (vs. previous SOTA 24.68%) recall for publication search and 63.18% (vs. previous SOTA 32.11%) recall for trial search".
- "With only 3B parameters, it outperforms industry-leading models like GPT-4o and Claude-3.5-Sonnet on 11/13 datasets."
- Its evidence-seeking retrieval uses single-hop NQ, TriviaQA and SQuAD ("evidence-seeking retrieval across common question-answering datasets (Kwiatkowski et al., 2019; Joshi et al., 2017; Rajpurkar et al., 2016)"). It is not a multi-hop benchmark.
- Compute: "For 3B models, all the tasks are run on two NVIDIA A100 80GB PCIe".

**s3 (Jiang et al., 2025)**: decoupled searcher, frozen generator. This is the closest architectural analog to Weave's rewrite-only model. Source: [arXiv 2505.14146v2](https://arxiv.org/html/2505.14146v2)
- **Sizes and training:**
  - "we use Qwen2.5-7B-Instruct … as the base searcher LLM to train, and use Qwen2.5-14B-Instruct … as the frozen generator". The searcher is 7B, not ≤4B.
  - Reward: "trains the searcher using a Gain Beyond RAG reward: the improvement in generation accuracy over naive RAG".
  - Data: "s3 requires only 2.4k training samples to outperform baselines trained on over 70x more data".
- **Table 4, training cost** on five A100s with batch size 120:
  - Search-R1: 1.8 min per step × about 2,100 steps = 3,780 min
  - DeepRetrieval (BM25): 1.3 min per step × about 1,600 steps = 2,080 min
  - s3: 5.7 min per step × about 20 steps = 114 min
- **Diagnostic on small agents as searchers.** The setting is described as "we extract the documents retrieved during a model’s reasoning trajectory and feed them to a frozen generator". With a frozen Qwen2.5-7B-Instruct generator, Table 1 reports generation accuracy (HotpotQA / 2wiki / Musique / 6-dataset average):
  - RAG with E5: 46.6 / 40.1 / 13.0 / 48.5
  - **Search-R1-3B searcher: 41.5 / 33.2 / 12.1 / 43.6**, below naive RAG on every multi-hop column
  - Search-R1-7B searcher: 58.6 / 50.8 / 27.6 / 54.0
  - s3 (7B searcher): 59.0 / 51.6 / 23.9 / 56.1
- **Authors' caveat:** "Our framework assumes the availability of a capable frozen generator LLM. … For lower-capacity or instruction-weak generators, the gains from better retrieval may not fully translate into better outputs."

**R1-Searcher (Song et al., 2025)**, source: [arXiv 2503.05592v2](https://arxiv.org/html/2503.05592v2)
- Sizes are 7B and 8B only: "based on Llama-3.1-8B-Instruct and Qwen-2.5-7B-Base".
- Results: "surpasses the strong baseline with GPT-4o-mini (i.e., ReARTeR) by up to 48.22% on HotpotQA and 21.72% on 2Wiki when using Qwen-2.5-7B-Base"; "an 11.4% performance improvement on Bamboogle compared to the Search-o1 with 32B parameters".
- No ≤4B result.

**ReSearch (Chen et al., 2025)**
- "We train ReSearch on Qwen2.5-7B(-Instruct) and Qwen2.5-32B(-Instruct) models" — [arXiv 2503.19470v3](https://arxiv.org/abs/2503.19470)
- 3B reproductions exist elsewhere: AutoRefine "reproduce[s] ReSearch using the authors’ publicly available code", with ReSearch-Base (3B) average 0.319 — [AutoRefine](https://arxiv.org/html/2505.11277v5)

**ZeroSearch (Sun et al., 2025)**, source: [arXiv 2505.04588v3](https://arxiv.org/html/2505.04588v3)
- **Sizes:** "Qwen-2.5-7B (Base/Instruct) and Qwen-2.5-3B (Base/Instruct) …, as well as LLaMA-3.2-3B (Base/Instruct)".
- **Setup:**
  - The simulated search engine is a 14B model: "The fine-tuned Qwen-2.5-14B-Instruct model serves as the default simulated search engine".
  - Evaluation uses Google: "During evaluation, all methods use SerpAPI as the search engine".
- **Compute:** "we deploy the simulation server on 4 H20 GPUs and conduct RL training on another 4 H20 GPUs."
- **Table 3, Qwen-2.5-3B** (EM ×100; HotpotQA / 2Wiki / MuSiQue / Bamboogle / 7-dataset average):
  - RAG: 24.20 / 23.20 / 8.20 / 15.20 / 25.09
  - Search-R1-base: 29.20 / 32.00 / 11.20 / 12.50 / 32.81
  - ZeroSearch-base: 33.80 / 34.60 / 13.00 / 13.89 / 34.47
- **Table 3, LLaMA-3.2-3B averages:** RAG 25.11; Search-R1-base 34.21; ZeroSearch-base 36.07.
- **Caveat:** "Deploying the simulated search LLM requires access to GPU servers."

**StepSearch (Wang et al., 2025)**, source: [arXiv 2505.15107v2](https://arxiv.org/html/2505.15107v2)
- **Abstract:** "achieving 11.2% and 4.2% absolute improvements for 3B and 7B models over various search with RL baselines using only 19k training data".
- **Training data:** "a novel MuSiQue-based pipeline, contributing 60k filtered sub-question search keywords"; "Leverage GPT-4o. to enrich decomposed MuSiQue questions with coherent subquestion–answer pairs, then derive N search queries per step".
- **Compute:** "Training is conducted across two nodes with 16 H800 GPUs."
- **Table 1, 3B** (EM; HotpotQA / 2Wiki / MuSiQue / Bamboogle):
  - RAG: 0.251 / 0.221 / 0.051 / 0.076
  - Search-R1-instruct: 0.304 / 0.293 / 0.120 / 0.240
  - StepSearch-instruct: 0.345 / 0.320 / 0.174 / 0.344
  - StepSearch-base: 0.329 / 0.339 / 0.181 / 0.328
- **Limitations:** "we have tested only at relatively modest parameter scales; scaling to larger models (e.g., 14 B, 32 B) may exacerbate issues such as reward collapse … StepSearch currently only uses 19k training data from MuSiQue for training."

**AutoRefine (Shi et al., 2025)**, source: [arXiv 2505.11277v5](https://arxiv.org/html/2505.11277v5)
- **Model and compute:** Qwen2.5-3B only. "trained on 8 NVIDIA A100-80GB GPUs with full-parameter fine-tuning … trained for 200 steps".
- **Table 1, Qwen2.5-3B** (HotpotQA / 2Wiki / Musique / Bamboogle / 7-dataset average):
  - Naive RAG: 0.255 / 0.226 / 0.047 / 0.080 / 0.270
  - Search-R1-Base: 0.297 / 0.274 / 0.066 / 0.128 / 0.312
  - AutoRefine-Base: 0.405 / 0.393 / 0.157 / 0.344 / 0.405
- **Limitations:**
  - "This work evaluates model performance solely on exact match accuracy or F1 score".
  - "The retrieval component uses a fixed Wikipedia snapshot".

**ExpandSearch (2025)**: 3B query expansion that depends on a large "squeezer". Source: [arXiv 2510.10009v1](https://arxiv.org/html/2510.10009v1)
- "even a small-scale 3B LLM can demonstrate a strong capability of query expansion and achieve state-of-the-art accuracy on the multi-hop QA benchmarks … an average improvement of 4.4% compared to state-of-the-art baselines".
- The 3B agent leans on a separate squeezer that reads the retrieved documents:
  - "Replacing the training-time squeezer (LLaMA-4-17b) with LLaMA-3.1-8b during inference maintains comparable performance".

**Plan Before Search (2026-05)**: decompose into ordered sub-questions before searching, at 3B–14B. Source: [arXiv 2605.28354v1](https://arxiv.org/html/2605.28354v1)
- **Fragile training:** "across three model families spanning 3B to 14B parameters, we find that an identical reward signal induces qualitatively different RL failure modes".
- **Failure modes:** "Models with low initial entropy lack sufficient exploration room … some models train stably at first but collapse abruptly … Models that lack the refine sub-skill also fail".
- **Positive result:** "some models, exemplified by Qwen2.5-3B-Base, can autonomously acquire the plan through pure RL".
- **Table 1, all 3B, EM** (HotpotQA / 2Wiki / MuSiQue / Bamboogle / multi-hop average):
  - Naive RAG: 0.255 / 0.226 / 0.047 / 0.080 / 0.152
  - Search-R1-Instruct: 0.331 / 0.310 / 0.124 / 0.232 / 0.249
  - AutoRefine-Base: 0.405 / 0.393 / 0.157 / 0.344 / 0.325
  - InForage (2026): 0.409 / 0.428 / 0.172 / 0.360 / 0.342
  - **PL-Search-3B-Base: 0.434 / 0.429 / 0.212 / 0.403 / 0.370**
- The caption confirms the setup: "All retrieval-augmented baselines use 3B-parameter LLMs for fair comparison."

**DAVID-GRPO (2026-01)**: 1.5B on commodity GPUs. Source: [arXiv 2601.21699v5](https://arxiv.org/abs/2601.21699)
- **Failure mode at small scale:** "Most sampled trajectories then retrieve none of the required evidence, so the outcome reward gives the policy little to learn from and small agents settle for answering without retrieval, a failure we call retrieval collapse."
- **Result:** "DAVID-GRPO trained on four RTX 3090 GPUs with 144 rollouts per step brings Qwen2.5-1.5B to 22.6 average EM against 11.9 for the best baseline under the same budget … unlike the baselines that stop after at most one search, learns to retrieve across turns."
- **Baselines:** "Every prior low-budget agent we train undergoes retrieval collapse and converges to zero or one search per question" — [HTML](https://arxiv.org/html/2601.21699v5)

**Orion (2025-11)**: 350M–1.2B search models. Source: [arXiv 2511.07581v1](https://arxiv.org/abs/2511.07581)
- "our 1.2B model achieves 77.6% success on SciFact (vs. 72.6% for prior retrievers), 25.2% on BRIGHT (vs. 22.1%), 63.2% on NFCorpus (vs. 57.8%), and remains competitive on FEVER, HotpotQA, and MSMarco. It outperforms retrievers up to 200-400x larger on five of six benchmarks."

**TongSearch-QR (2025)**: RL query rewriter at 1.5B and 7B. Source: [arXiv 2506.11603v2](https://arxiv.org/html/2506.11603v2)
- BRIGHT is reasoning-intensive and single-hop.
- **Table 1, BM25 retriever, average nDCG@10:**
  - Original query: 14.5
  - GPT-4o as query reasoner: 26.5
  - o1-preview: 30.2
  - **TongSearch-QR-1.5B: 24.6**
  - TongSearch-QR-7B: 27.9
- **Table 1, ReasonIR retriever:** GPT-4 29.9; **TongSearch-QR-1.5B 29.3**; 7B 31.9.

**FrugalRAG (2025)**, source: [arXiv 2507.07634v3](https://arxiv.org/abs/2507.07634)
- "we train an SLM with supervised finetuning on a full-exploration policy that generates broad sub-queries. Then, we apply RL to adaptively prune search depth"; "cutting retrieval cost nearly in half".
- **Inconsistent data claim:** the arXiv listing abstract says "10x more data … only approximately 1,000 examples", while the HTML body abstract says "100× more data … only 1,000 examples" ([HTML](https://arxiv.org/html/2507.07634v3)).
- The size of the SLM is **unverified**. I did not locate it, and the answer generator in its main table is Qwen2.5-7B-Instruct.

**Prompted (not trained) small models in iterative retrieval, for context:**
- IRCoT: "Our approach also works on much smaller Flan-T5 models (11B, 3B, and 0.7B) showing similar trends. In particular, we find QA using Flan-T5-XL (3B) with IRCoT even outperforms the 58X larger GPT3 with a one-step question-based retrieval." — [local ircot/src.txt L34](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/ircot/src.txt)
- LaSER's latency baseline: "The “Rewrite-then-Retrieve” method uses a 0.6B retriever and a 3B rewriter." — [local laser/src.txt L22](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/laser/src.txt)

**Baseline numbers vary across papers.**
- Search-R1-instruct 3B on HotpotQA is reported as:
  - 0.324 in Search-R1 v5 ([link](https://arxiv.org/html/2503.09516v5))
  - 0.331 in AutoRefine and Plan Before Search, which take numbers from an earlier Search-R1 version ([link](https://arxiv.org/html/2505.11277v5))
  - 0.304 in StepSearch's reproduction ([link](https://arxiv.org/html/2505.15107v2))
- Compare methods only within one table.

### Inferences
- **For a small rewrite-only model.**
  - Rewrite-only RL at 1.5–3B comes close to or matches GPT-4o-class query generation when the reward is the target retriever's own metric (DeepRetrieval: "11/13 datasets"; TongSearch-QR-1.5B 24.6 vs. GPT-4o 26.5 on BRIGHT; ConvSearch-R1 in Q2).
  - Weave has its own embedding model, so the same "retrieval-rank reward" design is available to it.
- **Against: small full agents.** These carry known risks:
  - lower ceilings (MuSiQue ≤ 0.21 EM at 3B, Plan Before Search Table 1);
  - collapse into answering without search (DAVID-GRPO, Search-R1 failure cases);
  - training that is fragile and model-family-specific (Plan Before Search, GRPO reward collapse).
- **Weave's narrow task removes some of these risks, untested.** Weave's rewriter does not answer and does not decide when to stop. It writes ≤2 short sub-questions and fills one slot. That plausibly avoids the "answer without retrieval" collapse, but no paper tests this exact narrow role at ≤3B on multi-hop retrieval (inference).
- **Train the rewriter against Weave's own retriever.** s3's diagnostic (the 3B Search-R1 searcher below one-shot E5 retrieval) warns against taking an off-the-shelf small search agent and using its queries with a different reader or retriever.
- **Compute is modest.** Reported budgets range from 2× A100 (DeepRetrieval 3B), 4× RTX 3090 (DAVID-GRPO 1.5B) and 114 GPU-minutes on 5× A100 (s3) up to 8× H100 (Search-R1) and 16× H800 (StepSearch). Training a ≤4B rewriter does not require a frontier-scale budget.

### Gaps
- None of these papers compares a ≤4B trained multi-hop *rewriter or decomposer* against a GPT-4-class rewriter **in the same multi-hop harness**. The direct large-vs-small comparisons are:
  - single-hop or reasoning-heavy retrieval (DeepRetrieval, TongSearch-QR, Orion);
  - conversational rewriting (ConvSearch-R1, Q2);
  - teacher vs. student agent distillation (Q4).
- No paper reports on-device (phone NPU) latency or quantized 4-bit accuracy for these rewriters.
- Training compute for R1-Searcher and ConvSearch-R1 was not located in the text I extracted.
- FrugalRAG's policy model size is unverified.

## Q4. Distilling decomposition or rewriting into small students: what fraction of teacher quality?

### Takeaway
- **Decomposition distills well; answering does not.** Distilling *decomposition* (or rewriting) holds up much better than distilling *solving*:
  - A 13B student decomposer keeps about 96–103% of a GPT-3.5 decomposer's end-task score (Divide-or-Conquer).
  - T5-base rewriters distilled from ChatGPT beat human-rewrite training on QReCC.
- **Students ≤3B keep less on multi-hop.** A 3B agent student keeps about 63–88% of a 32B teacher agent depending on the dataset (computed). A 774M GPT-2 with a learned sub-question generator reaches about 85% of a fine-tuned 6B model on GSM8K (computed).
- **Hardest cases fall off fastest.** The 3-hop MuSiQue and the hand-made Bamboogle drop most.

### Cited Findings
- **Shridhar et al. 2023, Socratic CoT.** Source: [arXiv 2212.00193v2](https://arxiv.org/pdf/2212.00193v2)
  - Setup: "a combination of two small distilled models: a problem decomposer and a subproblem solver"; datasets "GSM8K, StrategyQA, and SVAMP"; "boosts the performance of smaller models over 70% compared to the baselines"; "a much smaller model (GPT-2 large) can outperform a 10X larger model (GPT-3 6B)".
  - Table 2, GSM8K accuracy (%):
    - GPT-2 Large (774M) row reads "4.62 14.10 - 12.85 17.89 21.08 (↑33%) 13.25".
    - GPT-3 (6B) row reads "21.00", and its "6B results are taken from Cobbe et al. (2021)".
  - With the *learned* question-generation model: "When the subquestions are learned by the QG model (Iterative SocCoT), the accuracy of the student model decreases slightly but still improves over the step-by-step annotation without subquestions (17.89 vs. 14.10)."
  - The "as well as GPT-3 6B" claim relies on sub-questions generated by the LLM from ground-truth steps: "the ground-truth step-by-step annotation can be leveraged to prompt an LLM to generate subquestions … giving a performance boost of up to 38% when the LLM-generated subquestions are used at inference time." I mapped 21.08 to that "SocGT" column from the caption order; the mapping is my reading of the table.
  - Computed: 17.89 / 21.00 ≈ 85% of the fine-tuned GPT-3 6B score.
  - The tasks are math and StrategyQA, not retrieval.
- **Divide-or-Conquer (Wu et al., 2024).** Source: [arXiv 2402.15000v3](https://arxiv.org/html/2402.15000v3)
  - Students are 7B and 13B, not ≤4B: "a teacher model, GPT-3.5-turbo, and two student models, Vicuna-13B … and Mistral-7B".
  - Claim: "we can distill the problem decomposition phase and at the same time achieve good generalization across tasks, datasets, and models. However, it is harder to distill the problem solving capability without losing performance".
  - Table 1 (GSM8K EM / DROP F1 / Bamboogle accuracy):
    - GPT decomposer + GPT solver: 65.13 / 55.73 / 54.4
    - Distilled Vicuna-13B decomposer (S_D-T) + GPT solver: 67.02 / 55.19 / 52.0
    - GPT decomposer + distilled solver (S_E-T): 48.98 / 13.37 / 31.2
  - Computed: the distilled decomposer keeps 102.9% / 99.0% / 95.6% of the teacher pipeline.
- **Agent Distillation (Kang et al., 2025).** Source: [arXiv 2505.17612v2](https://arxiv.org/html/2505.17612v2)
  - Setup:
    - Teacher: "The teacher model is Qwen2.5-32B-Instruct".
    - Students: "four sizes: 0.5B, 1.5B, 3B, and 7B".
    - Data and training: "approximately 2,000 trajectories for distillation", "LoRA (rank 64)", "four NVIDIA A100 80GB GPUs".
    - Scoring: "llm-as-a-judge … using gpt-4o-mini for factual reasoning".
  - Table 2, accuracy (HotpotQA / MuSiQue / Bamboogle / 2Wiki):
    - Teacher 32B agent (prompting): 56.4 / 25.2 / 58.4 / 49.8
    - 3B distilled agent with first-thought prefix + self-consistent action generation: 49.4 / 15.8 / 38.4 / 41.0
    - 1.5B, same configuration: 45.6 / 9.2 / 33.6 / 33.6
    - 0.5B, same configuration: 33.4 / 5.6 / 24.0 / 31.2
  - Computed fraction of the teacher:
    - 3B: 88% / 63% / 66% / 82%
    - 1.5B: 81% / 37% / 58% / 67%
    - 0.5B: 59% / 22% / 41% / 63%
  - Abstract: "sLMs as small as 0.5B, 1.5B, 3B parameters can achieve performance competitive with next-tier larger 1.5B, 3B, 7B models fine-tuned using CoT distillation".
- **Distilled rewriters:**
  - InfoCQR (T5-base from ChatGPT labels, 10K instances) beat training on human rewrites on QReCC but not on TREC-Conv. Quotes are in Q2. — [arXiv 2310.09716v2](https://arxiv.org/pdf/2310.09716v2)
  - RRR's warm-up is likewise distillation from ChatGPT into T5-large, and the authors call it "sub-optimal" on PopQA (Q1). — [ar5iv 2305.14283](https://ar5iv.labs.arxiv.org/html/2305.14283)
- **EfficientRAG**: small non-generative students trained on LLM-synthesized decomposition labels.
  - "EfficientRAG Labeler and Filter are fine-tuned based on DeBERTa-v3-large … with 24 layers and 304M parameters" — [local efficientrag/src.txt L106](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/efficientrag/src.txt)
  - "We constructed the training data … with Llama-3-70B-Instruct … trained our model on 4× Nvidia A100 GPUs for about 10 GPU-hours" — [local L109](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/efficientrag/src.txt)
  - "three times faster than LLM-based baselines while maintaining a similar number of iterations" — [local L133](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/efficientrag/src.txt)
- **Teacher-labelled data, then RL, for small rewriters:**
  - TongSearch-QR uses rewritten queries from "a large reasoning model, e.g., QwQ-32B or DeepSeek-R1" as training data (V1-R1, V1-QwQ), then RL; the 1.5B model reaches 24.6 vs. GPT-4o's 26.5 on BRIGHT with BM25 — [arXiv 2506.11603v2](https://arxiv.org/html/2506.11603v2)
  - Plan Before Search reports that 3B-seed self-bootstrapped data "even outperform strong-model distillation in our experiments" — [arXiv 2605.28354v1](https://arxiv.org/html/2605.28354v1)

### Inferences
- **Fits Weave's design.** The pattern "decomposer and rewriter small, solver large" (Divide-or-Conquer) matches Weave: a small on-device rewriter plus a separate retriever, with answers composed downstream. However, the strongest decomposer-distillation evidence uses 7–13B students. Below 3B the evidence comes from full-agent distillation, where retention drops sharply on 3-hop MuSiQue (63% at 3B, 37% at 1.5B; computed).
- **Weave's targets are mostly 2-hop.** HotpotQA and 2Wiki, both 2-hop, keep 82–88% at 3B. This is the closest proxy, but it is still English Wikipedia (inference).

### Gaps
- No study distills *only* a bridge-placeholder rewriter (sub-question with a slot, then fill) into a ≤4B student and measures its retrieval recall against the teacher.
- No distillation study uses Korean.

## Q5. Placeholder-style decomposition formats usable as training data (Break/QDMR "#1", MuSiQue, Hi-Q q_left/q_right)

### Takeaway
- **Formats are available and documented:**
  - QDMR uses "#1" step references.
  - MuSiQue decompositions use "#1 >> relation".
  - Hi-Q's q_left/q_right is natural-language binary splitting.
- **Older small models learned them only partly.** A 2020 LSTM CopyNet hit 0.157 exact match on QDMR. MuSiQue's BART-large decomposer left a 9.4-point answer F1 gap to gold decompositions.
- **Modern 3B evidence is positive but indirect and fragile.** StepSearch trains 3B models on MuSiQue sub-question data. Plan Before Search shows a 3B model can learn "decompose first" via RL, but other model families fail.
- **Hi-Q's binary split has no small-model evidence.** Hi-Q is GPT-4o-mini prompting with no fine-tuning.

### Cited Findings
- **Break / QDMR (Wolfson et al., TACL 2020).** Source: [arXiv 2001.11770v1](https://arxiv.org/pdf/2001.11770v1)
  - Format examples from Table 8: "[team with Baltimore Fight Song, year did #1 win the Superbowl]" and "[state bordering ohio, the smallest #1]".
  - Dataset: "the Break dataset, containing over 83K pairs of questions and their QDMRs".
  - Parsers: "SEQ2SEQ: A sequence-to-sequence neural model with a 5-layer LSTM encoder"; "COPYNET: SEQ2SEQ with an added copy mechanism".
  - Table 9, QDMR exact match: COPY 0.001, RULEBASED 0.002, SEQ2SEQ 0.081, S2SDYNAMIC 0.116, COPYNET 0.154, COPYNET on test 0.157.
  - Error analysis: "For standard QDMR, 24% of the sampled predictions were an exact match, with an additional 30% being fully decomposed and semantically equivalent … For high-level examples (from RC datasets) … Only 8% of the predictions were an exact match, with an additional 46% being semantically equivalent to the gold. The remaining 46% were of erroneous predictions".
- **MuSiQue (Trivedi et al., TACL 2022).**
  - Decomposition format, from a sample of the validation split on a Hugging Face mirror:
    - "Who is the spouse of the Green performer?" → "Green >> performer" ⇒ Steve Hillage; "#1 >> spouse" ⇒ Miquette Giraudy.
    - "Who founded the company that distributed the film UHF?" → "UHF >> distributed by"; "#1 >> founded by".
    - Source: [HF datasets-server, dgslibisey/MuSiQue (a mirror, not the official release)](https://datasets-server.huggingface.co/rows?dataset=dgslibisey/MuSiQue&config=default&split=validation&offset=0&length=4)
  - Decomposer model: "The decomposer is trained with gold decompositions, and is implemented with BART-large." — [ar5iv 2108.00573](https://ar5iv.labs.arxiv.org/html/2108.00573)
  - Decomposition quality as a bottleneck: "We train our EX(SA) model using ground-truth decompositions. On ♫-Ans, (An, Sp) improve by (9.4, 7.3) pts … This shows that although improving question decomposition will be helpful, it’s insufficient to reach human parity on the dataset." — [ar5iv 2108.00573](https://ar5iv.labs.arxiv.org/html/2108.00573)
  - Scores fall with hop count: "Our best model, EX(SA), scores 57.9, 47.9, and 28.1 answer F1 on 2, 3, and 4-hop questions" — [ar5iv 2108.00573](https://ar5iv.labs.arxiv.org/html/2108.00573)
- **Hi-Q (local text).**
  - The split: "proposes exactly two sub-queries: q_left, which resolves the bridge fact, and q_right, which uses that bridge to approach the parent query’s answer" — [local hiq/src.txt L143](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/hiq/src.txt)
  - The dependency constraint: "a dependency constraint q_left ≺ q_right, meaning the prerequisite branch must be resolved before the dependent branch" — [local L115](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/hiq/src.txt)
  - Models: "All methods use GPT-4o-mini as the reader unless otherwise stated; we additionally evaluate on Llama-3.3-70B and Qwen3-30B-A3B" — [local L173](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/hiq/src.txt)
  - With Qwen3-30B-A3B, a mixture-of-experts model with about 3B active parameters but 30B total, Hi-Q gets "58.3 EM / 68.9 F1" — [local L399](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/hiq/src.txt)
  - No fine-tuning: "without pre-built knowledge graphs or task-specific fine-tuning" — [local L37](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/hiq/src.txt)
  - Cost: "a measured mean of 5.7 calls per question" — [local L287](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/hiq/src.txt)
- **EfficientRAG's next-hop query without generation:** "The Filter extracts words and concatenates them to formulate the next-hop query." — [local efficientrag/src.txt L94](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/efficientrag/src.txt)
- **MuSiQue sub-questions as small-model RL data:**
  - StepSearch: "a novel MuSiQue-based pipeline, contributing 60k filtered sub-question search keywords"; trains Qwen2.5-3B and 7B (results in Q3) — [arXiv 2505.15107v2](https://arxiv.org/html/2505.15107v2)
  - Plan Before Search: "decomposes a question into ordered sub-questions before any retrieval is performed, so that each search step can be anchored to a pre-designed sub-question instead of drifting under the influence of partially relevant documents retrieved earlier" — [arXiv 2605.28354v1](https://arxiv.org/abs/2605.28354)
- **Caution for date placeholders sent to a metadata filter.** This applies to Weave step 2.
  - LongMemEval found that time-range extraction needs a strong model: "Llama 8B, on the other hand, struggles to generate accurate time ranges, often hallucinating or missing temporal cues even with numerous in-context examples." — [local longmemeval/src.txt L247](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/longmemeval/src.txt)
  - "in many of the cases where the question does not have any temporal reference … the model often mistakenly extracts a time range, which erroneously prunes out the search space, leading to a low memory recall. By contrast, GPT-4o is able to refuse to generate a time range" — [local L517](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/논문스터디/work/longmemeval/src.txt)
  - These are prompted, not trained, models.

### Inferences
- **Usable data.** MuSiQue's "#1 >> relation" chains (2–4 hops) and QDMR's "#1" steps can be converted into Weave's "[그날] …" slot format. For "first sub-question, then fill the slot", MuSiQue is the best fit, because each hop's answer is given and can serve as the fill target (inference).
- **Two failure modes need dedicated training data:**
  - a slot is filled with a value that was never retrieved (cf. Hi-Q's report of LLMs filling bridges from memory, already noted in [질문다시쓰기_근거.md](/home/jaeung/samsung/t3/weave/결선준비/09_HowItWorks/리서치/질문다시쓰기_근거.md));
  - a date filter is created when the question has none (LongMemEval).
- **Robustness to "no date".** Include "no date / no bridge found" negatives in training, and keep the deterministic fallback "retry without the filter" (inference).

### Gaps
- I did not find a published accuracy number for modern T5- or BART-class QDMR parsers. Later QDMR parsers exist but were not verified here.
- No paper reports how reliably a ≤4B model emits a *well-formed* placeholder and fills it from a retrieved record. Format-following error rates are unreported.

## Q6. Korean evidence: query rewriting or decomposition with small models

### Takeaway
I found **no published evidence on Korean query rewriting or decomposition with ≤4B models**.
- **Closest Korean rewriting result.** HyperCLOVA's in-house "query modification" task for AI speakers (Korean ellipsis and reference resolution) reports only **13B and 39B** models. BLEU rises sharply with prompt tuning: 13B zero-shot goes from 36.15 to 58.04.
- **Korean multi-hop QA work** (KoBLEX, DaR, the KoChainRAG thesis) uses large LLMs (Qwen3-32B, Gemma3-27B, GPT-4o) or does not report model sizes or numbers in the visible text.

### Cited Findings
- **HyperCLOVA (Kim et al., EMNLP 2021).** Source: [arXiv 2109.04650](https://arxiv.org/pdf/2109.04650)
  - Task definition: "Query modification task is a query modification task for AI speaker users. … the goal of the task is to convert the multi-turn query to a single-turn query, which can then be understood by a single-turn AI speaker. There are 1,326 test instances in total."
  - Table 5, BLEU on the in-house query modification task:

    | Model | Shots | Without p-tuning | With p-tuning |
    |---|---|---|---|
    | 13B | zero-shot | 36.15 | 58.04 |
    | 13B | 3-shot | 45.64 | 68.65 |
    | 39B | zero-shot | 47.72 | 73.80 |
    | 39B | 3-shot | 65.76 | 71.19 |

  - Korean examples, verbatim from Table 11:
    - "사용자: 아이유노래틀어줘 … 스피커: 노래를재생합니다. … 사용자: 몇살이야 … 사용자의최종의도: 아이유몇살이야"
    - "사용자: 비행기는누가만들었어 … 스피커: 라이트형제요. … 사용자: 동생이름뭐야 … 사용자의최종의도: 라이트형제동생이름뭐야?"
  - Smaller HyperCLOVA sizes (137M–6.9B) appear in Table 3 only for other tasks (NSMC, KorQuAD, translation, YNAT, KLUE-STS), not for query modification.
- **KoBLEX (2025)**, Korean legal multi-hop QA. Source: [arXiv 2509.01324](https://arxiv.org/abs/2509.01324)
  - "KoBLEX includes 226 scenario-based QA instances"
  - "compared to standard retrieval with GPT-4o, ParSeR achieves +37.91 higher F1 and +30.81 higher LF-Eval."
- **Decompose-and-Refine (DaR, 2026-05)**, source: [arXiv 2605.24454](https://arxiv.org/abs/2605.24454)
  - Method: "progressively decomposes a complex legal question into atomic sub-questions and generates statute-aligned parametric queries for each sub-question".
  - Models are large: "We evaluate DaR on KoBLEX, a Korean multi-hop LQA benchmark grounded in statutory law, using Qwen3-32B and Gemma3-27B."
- **KoChainRAG master's thesis (Sogang University, 2025.8).** Source: [NANET record](https://dl.nanet.go.kr/detail/KDMT12025000056737)
  - Title: "KoChainRAG: 질문 분해와 구조적 추론을 활용한 한국어 멀티홉 질의응답 시스템 개발".
  - Method: "복잡한 질문을 단일 홉 단위로 분해하고 체인 형태로 연결하여 순차적으로 처리하는".
  - Data: the table of contents lists "엑소브레인 멀티홉 QA 데이터셋".
  - Model names, sizes and numbers were not visible; read through a WebFetch summary, so treat as **unverified** beyond the title and abstract snippet.
- **Searches that returned nothing relevant:**
  - arXiv API title searches for Korean AND (rewriting OR reformulation OR decomposition);
  - abstract search for "query rewriting" AND Korean;
  - web searches in Korean and English for small-model Korean query rewriting or decomposition.
  - The searches returned tokenization, dialogue-benchmark and legal-QA papers only. — [arXiv API query](https://export.arxiv.org/api/query?search_query=ti:Korean%20AND%20(ti:rewriting%20OR%20ti:reformulation%20OR%20ti:decomposition)&max_results=10)

### Inferences
- **Every number in Q1–Q5 is English.** Korean adds:
  - particle and ellipsis-heavy turns (the HyperCLOVA examples drop subjects and objects entirely);
  - spacing variation (the HyperCLOVA outputs are unspaced);
  - mixed date formats in personal records.
- **Prompting alone looks weak at mid-scale.** The large BLEU jump from p-tuning at 13B (36.15 → 58.04 zero-shot) suggests prompting a Korean model for this task is weak even at 13B, and that task-specific training matters. This is the only Korean data point, and it is not ≤4B (inference).
- **Weave would need its own Korean training and evaluation data.** Options include translating or adapting CANARD, QReCC or MuSiQue decompositions, or synthesizing data with a teacher LLM, as InfoCQR, RRR and StepSearch did in English. Any claim that a ≤4B model rewrites Korean personal-record queries as well as a large LLM is currently unsupported by published evidence (inference).

### Gaps
- No Korean benchmark exists for conversational query rewriting or bridge-slot decomposition, so no ≤4B Korean result exists.
- Korean on-device models (e.g., EXAONE or HyperCLOVA X small variants) were not checked for rewriting evaluations. No sources were found in this pass.
- No evidence covers Korean date and relative-time normalization ("지난 주말", "3/15 (일)") by small models.
- No published evaluation covers personal-data retrieval in any language (chats, OCR'd photos, notes, payments) with small rewriters. None of the numbers above may be presented as Weave's performance.
