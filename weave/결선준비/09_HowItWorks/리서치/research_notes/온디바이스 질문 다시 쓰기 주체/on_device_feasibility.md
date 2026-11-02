# Can a rewrite-only LLM (≤4B) run on 2025–2026 Galaxy flagships? Measured latency, memory, availability (state as of 2026-11-02)

Conventions: all pages were fetched on 2026-11-02 unless noted. "Quote" = text copied from the fetched page (HTML tags stripped, whitespace joined). Table values from Qualcomm's `perf.yaml` files are copied and rounded to 0.1. Anything not confirmed from a primary page is marked UNVERIFIED. Phone numbers only; desktop/server rows that appear on the same pages are deliberately left out.

## Q1. Measured on-device LLM speed (prefill tok/s, decode tok/s, TTFT) for ~0.5–4B models

### Takeaway
On Galaxy S25 (Snapdragon 8 Elite for Galaxy) and Galaxy S26 (Snapdragon 8 Elite Gen 5 for Galaxy), Qualcomm's and Google's own 2026 measurements show the following for 4-bit 0.6–4B models:
- Prefill: ≈490–7,200 tok/s on the NPU, depending on model, runtime and compiled context; ≈3,800 tok/s on the GPU for Gemma 4 E2B in LiteRT-LM.
- Decode: ≈15–133 tok/s.
- For a 500-in/25-out rewrite, prefill takes ≈0.08–1.0 s and decode ≈0.2–1.7 s across the W4A16/Q4_0 rows in the table below. Decode is the larger share for any model ≥1.7B on the fastest stacks.

Coverage gaps:
- No LLM tokens/s has been published for Exynos 2500/2600. That matters because the Galaxy S26/S26+ use Exynos 2600 in at least some markets. Samsung's only figure is a "113%" generative-AI claim.
- Google publishes Gemini Nano speeds only for Pixels: 510 tok/s prefix and 11 tok/s decode (nano-v2, Pixel 9 Pro), and 940 tok/s prefix (nano-v3, Pixel 10 Pro).
- Vendor marketing figures such as "Up to 220 tokens per second" (Snapdragon 8 Elite Gen 5) are far above Qualcomm's own per-model measurements (~28 tok/s for a 3B model). They should not be used for budgeting.

### Cited Findings

**A. Qualcomm AI Hub (Genie / GenieX runtimes), measured on Galaxy S25 and S26: the most complete 2026 dataset**
- **Device → chip mapping.**
  - The Galaxy S25 row in AI Hub's device table reads "Samsung Galaxy S25: chipset: qualcomm-snapdragon-8-elite-for-galaxy … os: ostype: Android version: '15'".
  - The Galaxy S26 rows read "Samsung Galaxy S26: chipset: qualcomm-snapdragon-8-elite-gen5-for-galaxy … version: '16'" and "Samsung Galaxy S26 Ultra: chipset: qualcomm-snapdragon-8-elite-gen5-for-galaxy".
  - The chipset entry reads "marketing_name: Snapdragon® 8 Elite Gen 5 For Galaxy Mobile reference_device: Samsung Galaxy S26".
  - Source: [devices_and_chipsets.yaml](https://raw.githubusercontent.com/quic/ai-hub-models/main/src/qai_hub_models/devices_and_chipsets.yaml).
- **Which physical phone ran the job.** Jobs run on a pool of phones from the same family, not necessarily the named model: "# Mobile chipsets. S22-S26 override reference_device_name so metadata comes # from the specific device even though Hub jobs schedule on the family pool." ([device.py](https://raw.githubusercontent.com/quic/ai-hub-models/main/src/qai_hub_models/scorecard/device.py))
- **How the metrics are defined** ([AI Hub Qwen3-4B page](https://aihub.qualcomm.com/models/qwen3_4b)):
  - TTFT: "Time To First Token is the time it takes to generate the first response token. This is expressed as a range because it varies based on the length of the prompt. The lower bound is for a short prompt (up to 128 tokens, i.e., one iteration of the prompt processor) and the upper bound is for a prompt using the full context length (4096 tokens)."
  - Response rate: "Rate of response generation after the first response token. Measured on a short prompt with a long response (with thinking); may slow down when using longer context lengths."
- **Quantization recipe:** "The model is quantized to w4a16 (4-bit weights and 16-bit activations) and part of the model is quantized to w8a16 (8-bit weights and 16-bit activations) making it suitable for on-device deployment." ([Llama-v3.2-3B README](https://raw.githubusercontent.com/quic/ai-hub-models/main/src/qai_hub_models/models/llama_v3_2_3b_instruct/README.md))
- **Measurement age.** The numbers come from per-model `perf.yaml` files on GitHub main.
  - The latest commit touching them (2026-10-21) is a format change: "Serialize perf.yaml as the ModelPerf proto (#4897)".
  - The latest data refresh before that, for the Llama-3.2-3B, Qwen3-4B and Qwen3-1.7B files, is "[Automated] Update Data from Prod Scorecard (#4910)" on 2026-10-20.
  - The Gemma-4-E2B file's previous commit is dated 2026-10-06.
  - Source: GitHub commits API for `src/qai_hub_models/models/<model>/perf.yaml`.
  - Newer GenieX rows carry "geniex: v0.9.1" and "qairt: '2.50'".
- **Verbatim examples** ([qwen3_4b/perf.yaml](https://raw.githubusercontent.com/quic/ai-hub-models/main/src/qai_hub_models/models/qwen3_4b/perf.yaml)):
  - Genie runtime, 4096 context: "component: Qwen3-4B device: Samsung Galaxy S25 llm_metrics: - context_length: 4096 desired_compute_unit: npu prefill_tokens_per_second: 553.7098388671875 time_to_first_token_range_milliseconds: max: 2081.44 min: 65.045 tokens_per_second: 26.132177352905273 precision: PRECISION_W4A16 runtime: RUNTIME_GENIE".
  - The GenieX-QAIRT block for the same phone at 1024 context: "- context_length: 1024 desired_compute_unit: npu prefill_tokens_per_second: 1754.884199 time_to_first_token_range_milliseconds: max: 583.5142857142856 min: 72.9392857142857 tokens_per_second: 22.27587".
- **Extracted rows for ≤4B models**, all 4-bit. TTFT is the range from a 128-token prompt to a full-context prompt. Per-model sources are `https://raw.githubusercontent.com/quic/ai-hub-models/main/src/qai_hub_models/models/<id>/perf.yaml` with id = qwen3_0_6b, qwen3_1_7b, qwen3_4b, qwen3_4b_instruct_2507, llama_v3_2_1b_instruct, llama_v3_2_3b_instruct, llama_v3_2_3b_instruct_ssd, gemma_4_e2b_it, gemma_4_e4b_it, qwen3_5_0_8b, qwen3_5_2b, phi_4_mini_instruct.

| Model | Precision / runtime / unit | Phone | ctx | Prefill tok/s | Decode tok/s | TTFT range ms |
|---|---|---|---|---|---|---|
| Qwen3-0.6B | W4A16 / GenieX-QAIRT / NPU | S25 | 1024 | 5230.1 | 79.9 | 24.5–195.8 |
| Qwen3-0.6B | W4A16 / GenieX-QAIRT / NPU | S26 | 1024 | 5985.6 | 88.8 | 21.4–171.1 |
| Qwen3-0.6B | W4A16 / Genie / NPU | S25 | 4096 | 2262.4 | 125.0 | 15.9–509.4 |
| Qwen3-0.6B | W4A16 / Genie / NPU | S26 | 4096 | 2681.0 | 132.8 | 13.5–430.6 |
| Qwen3-1.7B | W4A16 / GenieX-QAIRT / NPU | S25 | 1024 | 3000.9 | 39.8 | 42.7–341.2 |
| Qwen3-1.7B | W4A16 / GenieX-QAIRT / NPU | S26 | 1024 | 3288.5 | 42.4 | 38.9–311.4 |
| Qwen3-1.7B | W4A16 / Genie / NPU | S25 | 4096 | 1222.5 | 56.7 | 29.4–942.3 |
| Qwen3-1.7B | W4A16 / Genie / NPU | S26 | 4096 | 1245.3 | 58.3 | 28.9–926.1 |
| Qwen3-4B | W4A16 / GenieX-QAIRT / NPU | S25 | 1024 | 1754.9 | 22.3 | 72.9–583.5 |
| Qwen3-4B | W4A16 / GenieX-QAIRT / NPU | S26 | 1024 | 1768.6 | 21.8 | 72.4–579.0 |
| Qwen3-4B | W4A16 / Genie / NPU | S25 | 4096 | 553.7 | 26.1 | 65.0–2081.4 |
| Qwen3-4B | W4A16 / Genie / NPU | S26 | 4096 | 672.9 | 28.6 | 53.5–1712.7 |
| Qwen3-4B-Instruct-2507 | W4A16 / GenieX-QAIRT / NPU | S25 | 1024 | 1730.6 | 20.6 | 74.0–591.7 |
| Qwen3-4B-Instruct-2507 | W4A16 / GenieX-QAIRT / NPU | S26 | 1024 | 1764.2 | 20.9 | 72.6–580.4 |
| Llama-3.2-1B-Instruct | W4A16 / Genie / NPU | S25 | 4096 | 1782.5 | 67.2 | 31.5–1006.9 |
| Llama-3.2-1B-Instruct | W4A16 / Genie / NPU | S26 | 4096 | 1626.0 | 65.2 | 34.5–1103.6 |
| Llama-3.2-3B-Instruct | W4A16 / Genie / NPU | S25 | 4096 | 727.8 | 26.5 | 77.0–2463.4 |
| Llama-3.2-3B-Instruct | W4A16 / Genie / NPU | S26 | 4096 | 775.8 | 28.2 | 72.2–2311.3 |
| Llama-3.2-3B-Instruct | W4 (weight-only) / Genie / NPU | S25 | 4096 | 396.4 | 14.3 | 141.3–4521.9 |
| Llama-3.2-3B-Instruct-SSD | W4A16 / Genie / NPU | S26 | 4096 | 970.9 | 55.2 | 57.7–1846.0 |
| Gemma-4-E2B-it | Q4_0 / GenieX-llama.cpp / NPU | S25 | 512 | 1686.1 | 28.9 | 76.1–304.4 |
| Gemma-4-E2B-it | Q4_0 / GenieX-llama.cpp / NPU | S26 | 512 | 1894.4 | 33.7 | 68.1–272.5 |
| Gemma-4-E2B-it | Q4_0 / GenieX-llama.cpp / GPU | S26 | 512 | 455.7 | 31.8 | 281.7–1126.8 |
| Gemma-4-E2B-it | Q4_0 / GenieX-llama.cpp / CPU | S26 | 512 | 242.4 | 31.7 | 528.4–2113.4 |
| Gemma-4-E4B-it | Q4_0 / GenieX-llama.cpp / NPU | S26 | 512 | 1115.8 | 17.6 | 115.6–462.2 |
| Qwen3.5-0.8B | Q4_0 / GenieX-llama.cpp / NPU | S26 | 512 | 1170.5 | 45.7 | 109.5–438.2 |
| Qwen3.5-0.8B | Q4_0 / GenieX-llama.cpp / GPU | S26 | 512 | 1218.5 | 62.0 | 105.7–422.9 |
| Qwen3.5-2B | Q4_0 / GenieX-llama.cpp / NPU | S26 | 512 | 909.7 | 30.4 | 140.9–563.5 |
| Phi-4-mini-instruct | Q4_0 / GenieX-llama.cpp / NPU | S26 | 512 | 1379.5 | 23.2 | 93.2–372.9 |

- **Larger compiled context lowers decode speed** (same file, Qwen3-4B, GenieX-QAIRT, Galaxy S25):
  - Decode by context: "tokens_per_second: 23.395323" at 512, "22.27587" at 1024, "20.700786" at 2048, "20.515618" at 3072, "17.535443" at 4096.
  - Prefill by context: 2101.6 tok/s at 512 and 1263.4 tok/s at 4096.
- **Self speculative decoding.** The Llama-3.2-3B-Instruct-SSD variant "uses Self Speculative Decoding (SSD), inference acceleration solution that achieves on-target speed up with guaranteed output accuracy identical to the base model" ([README](https://raw.githubusercontent.com/quic/ai-hub-models/main/src/qai_hub_models/models/llama_v3_2_3b_instruct_ssd/README.md)). On the S26 this roughly doubles decode, from 28.2 to 55.2 tok/s.
- **Data caveat (my check of the files).** In every ≤4B `perf.yaml` above, each "Samsung Galaxy S25" row has exactly the same values as the matching "Dragonwing Q-8750" row. For example, both Llama-3.2-3B W4A16 Genie rows read prefill 727.8020629882812, decode 26.502702713012695 and TTFT 76.98–2463.36. So the S25 values were probably measured once and reported under both names. Whether a retail S25 ran that measurement is not stated. The S26 rows have no such twin.

**B. Google LiteRT-LM (CPU/GPU) on Galaxy phones, Google-published, 2025–2026**
- **Benchmark conditions** ([litert-community/gemma-4-E2B-it-litert-lm card](https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm)): "All benchmarks were taken using 1024 prefill tokens and 256 decode tokens with a context length of 2048 tokens via LiteRT-LM. The model can support up to 32k context length. The inference on CPU is accelerated via the LiteRT XNNPACK delegate with 4 threads. Time-to-first-token does not include load time. Benchmarks were run with caches enabled and initialized. During the first run, the latency and memory usage may differ. Model size is the size of the file on disk."
- **Gemma 4 E2B on Galaxy S26 Ultra**, verbatim rows from the same card (the S26 Ultra uses Snapdragon 8 Elite Gen 5 for Galaxy per the AI Hub device table above):
  - "| S26 Ultra | CPU | 557 | 46.9 | 1.8 | 2583 | 1733 |"
  - "| S26 Ultra | GPU | 3,808 | 52.1 | 0.3 | 2583 | 676 |"
  - Columns: Prefill tok/s | Decode tok/s | TTFT s | Model size MB | CPU Memory MB.
- **Gemma 4 E2B on S26 Ultra with speculative decoding (MTP).** The card says "The number of input and output tokens varied across prompts."
  - Baseline: "| S26 Ultra | GPU | Baseline | No | 51.5 | 791 |".
  - Rewrite task: "| S26 Ultra | GPU | Rewrite tone | Yes | 87.4 | 762 |".
  - CPU rewrite task: "| S26 Ultra | CPU | Rewrite tone | Yes | 47.1 | 1408 |".
  - Columns: decode tok/s | CPU memory MB.
- **Gemma 4 E2B on iPhone 17 Pro**, a non-Samsung reference from the same card:
  - "| iPhone 17 Pro | CPU | 532 | 25.0 | 1.9 | 2583 | 607 |"
  - "| iPhone 17 Pro | GPU | 2,878 | 56.5 | 0.3 | 2583 | 1450 |"
  - The iPhone 17 Pro's chip is not stated on the card.
- **Gemma 4 E4B on Galaxy S26 Ultra** ([litert-community/gemma-4-E4B-it-litert-lm](https://huggingface.co/litert-community/gemma-4-E4B-it-litert-lm)):
  - "| S26 Ultra | CPU | 195 | 17.7 | 5.3 | 3654 | 3283 |"
  - "| S26 Ultra | GPU | 1,293 | 22.1 | 0.8 | 3654 | 710 |"
  - With MTP: "| S26 Ultra | GPU | Rewrite tone | Yes | 47.5 | 999 |".
- **LiteRT-LM overview table** ([ai.google.dev/edge/litert-lm/overview](https://ai.google.dev/edge/litert-lm/overview), "Last updated 2026-10-06 UTC"). Columns: CPU prefill/decode, GPU prefill/decode, tok/s.
  - Gemma3-1B (1005 MB), "Samsung S24 Ultra": CPU 177/33, GPU 1191/24.
  - Qwen2.5-1.5B (1598 MB), "Samsung S25 Ultra": CPU 298/34, GPU 1668/31.
  - Gemma-3n-E2B (2965 MB), "Samsung S24 Ultra": CPU 111/16, GPU 816/16.
  - Gemma-3n-E4B (4235 MB), "Samsung S24 Ultra": CPU 74/9, GPU 548/9.
  - phi-4-mini (3906 MB), "Samsung S24 Ultra": CPU 67/7, GPU 314/10.
  - Qwen2.5-0.5B (521 MB), "Samsung S24 Ultra": CPU 251/30.
  - FunctionGemma (289 MB), "Samsung S25 Ultra": CPU 2238/154.
  - Qwen3-0.6B (586 MB), "Vivo X300 Pro": CPU 165/9, GPU 580/21.
- **Qwen2.5-1.5B-Instruct details** ([litert-community/Qwen2.5-1.5B-Instruct](https://huggingface.co/litert-community/Qwen2.5-1.5B-Instruct)):
  - Device: "Note that all benchmark stats are from a Samsung S25 Ultra and multiple prefill signatures enabled."
  - dynamic_int8, ctx 1280: CPU prefill 297.58, decode "34.25 tk/s", TTFT "3.71 s". GPU prefill "1667.75 tk/s", decode "30.88 tk/s", TTFT "3.63 s".
  - The GPU TTFT of 3.63 s does not match 1667.75 tok/s for any plausible prompt length. The card does not explain it.
- **Qwen3-0.6B, community-contributed measurements** ([litert-community/Qwen3-0.6B](https://huggingface.co/litert-community/Qwen3-0.6B)). Not Google-measured: "These results are not affiliated with, sponsored by, endorsed by, or verified by Samsung, vivo, Qualcomm, MediaTek, Google, MLCommons, or Hugging Face."
  - Galaxy S26 rows (1,024 prefill and 256 decode tokens, 2,048-token KV cache, LiteRT-LM 0.19.0; the card's surrounding text cites measurements dated 2026-10-30): "| Galaxy S26 (SM-S942Q, Android 16) | GPU (OpenCL) | 3,442 / 81.4 | 2,384 / 71.4 |" and "| Galaxy S26 | CPU (XNNPACK) | 231 / 21.9 | 217 / 21.7 |".
  - Galaxy SM-S937U1 rows (mixed INT4, 256/256 tokens, ctx 2048): "| Samsung SM-S937U1 | GPU OpenCL | 1844.95 | 69.38 | 0.150 | 585 MB |" and "| Samsung SM-S937U1 | CPU | 576.59 | 12.90 | 0.520 | 2895 MB |".
  - The card gives no marketing name for SM-S937U1.
- **Gemma 4 E2B speed in Google blogs.** The device is the S26 Ultra; the date is 2026-05-19.
  - Decode: "When running Gemma 4 E2B without MTP enabled, LiteRT-LM achieves an impressive 52 tokens/sec decode speed via the GPU backend on Android (OpenCL)."
  - MTP: "unlocking up to 2.2x decoding speedup … Numbers reported are collected on Samsung S26 Ultra using the GPU backend."
  - Source: [Blazing-fast on-device GenAI with LiteRT-LM](https://developers.googleblog.com/blazing-fast-on-device-genai-with-litert-lm/).
  - Earlier, 2026-04-02: "LiteRT-LM leverages cutting-edge GPU optimizations to process 4,000 input tokens across 2 distinct skills in under 3 seconds". The device is not named in that sentence ([Gemma 4 at the edge](https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/)).
- **MediaPipe LLM Inference is legacy.** The Gemma 4 E2B card says of the MediaPipe route: "However, this route is currently in maintenance mode."

**C. NPU numbers via LiteRT on non-Galaxy phones with Galaxy-class chips (Google blogs)**
- **Snapdragon 8 Elite Gen 5 NPU, FastVLM-0.5B** (a 0.5B vision-language model with image input), measured on the Xiaomi 17 Pro Max:
  - Model setup: "The model is optimized with int8 weight quantization and int16 activatio[n]".
  - Speed: "Running on the Snapdragon 8 Elite Gen 5 NPU, our FastVLM integration delivers time-to-first-token (TTFT) in just 0.12 second on high-resolution images (1024x1024). It achieves over 11,000 tokens/sec for prefill and over 100 tokens/sec for decode."
  - Source: [Unlocking Peak Performance on Qualcomm NPU with LiteRT](https://developers.googleblog.com/en/unlocking-peak-performance-on-qualcomm-npu-with-litert/), 2025-11-24.
- **MediaTek Dimensity 9500 NPU, Gemma 3n E2B** (Vivo X300 Pro):
  - Speed: "the Gemma 3n E2B model achieves over 1600 tokens/sec for prefill and 28 tokens/sec for decode (with 4K context) on the NPU."
  - Relative speedup: "Gemma models are accelerated by up to 12x compared to CPU, and 10x compared to GPU".
  - Source: [MediaTek NPU and LiteRT](https://developers.googleblog.com/en/mediatek-npu-and-litert-powering-the-next-generation-of-on-device-ai/), 2025-12-08.
  - MediaTek chips are not used in Galaxy S flagships; this is a reference point only.
- **MediaTek MT6993 NPU, Qwen3-0.6B** (vivo V2502A): "| vivo V2502A | NPU | 1472 | 36 | - | - |". The card calls it a "previously published MediaTek MT6993 NPU reference result" ([litert-community/Qwen3-0.6B](https://huggingface.co/litert-community/Qwen3-0.6B)).

**D. Gemini Nano (AICore): Google publishes Pixel numbers only**
- **Pixel 9 Pro, nano-v2:** "this is a quick reference of how the APIs perform on a Pixel 9 Pro: | Prefix Speed (input processing rate) | Decode Speed (output generation rate) | ;; Text-to-text | 510 tokens/second | 11 tokens/second |" ([Android Developers Blog](https://android-developers.googleblog.com/2025/05/on-device-gen-ai-apis-ml-kit-gemini-nano.html), 2025-05-20).
- **Prefix speeds by model and phone** ([Android Developers Blog](https://android-developers.googleblog.com/2025/08/the-latest-gemini-nano-with-on-device-ml-kit-genai-apis.html), 2025-08-22):
  - "Gemini nano-v2 on Pixel 9 Pro": "510 tokens/second".
  - "Gemini nano-v2* on Pixel 10 Pro": "610 tokens/second".
  - "Gemini nano-v3 on Pixel 10 Pro": "940 tokens/second".
  - No decode speed is given for nano-v3.
- **Gemini Nano 4 claims** ([AICore Developer Preview blog](https://android-developers.googleblog.com/2026/04/AI-Core-Developer-Preview.html), 2026-04-02):
  - "The new model is up to 4x faster than previous versions and uses up to 60% less battery." The baseline for "4x" is not stated.
  - "E2B: Optimized for maximum speed (3x faster than the E4B model!) and lower latency."
- **Galaxy-specific Gemini Nano speed: none found.**

**E. ExecuTorch / Meta (CPU only, 2024; OnePlus 12 = Snapdragon 8 Gen 3)**
- **Conditions** ([ExecuTorch Llama README](https://raw.githubusercontent.com/pytorch/executorch/main/examples/models/llama/README.md)): "Llama 3.2 1B and 3B performance was measured on Android OnePlus 12 device. The performance measurement is expressed in terms of tokens per second using an adb binary-based approach with prompt length of 64. It is measured with KleidiAI library."
- **Results.** Columns: Decode tok/s | TTFT s | Prefill tok/s | PTE MiB | RSS MiB.
  - "|1B SpinQuant | 50.2 (2.6x) | 0.3 (-76.9%) | 260.5 (4.3x) | 1,083 (-54.1%) | 1,921 (-39.7%) |"
  - "|1B QAT+LoRA | 45.8 (2.4x) | 0.3 (-76.0%) | 252.0 (4.2x) | 1,127 (-52.2%) | 2,255 (-29.2%) |"
  - "|3B SpinQuant | 19.7 (2.6x) | 0.7 (-76.4%) | 89.7 (4.2x) | 2,435 (-60.3%) | 3,726 (-49.8%) |"
  - "|3B QAT+LoRA | 18.5 (2.4x) | 0.7 (-76.1%) | 88.8 (4.2x) | 2,529 (-58.7%) | 4,060 (-45.3%) |"
- **Date and Galaxy coverage.** Meta's blog is dated "October 24, 2024": "we've also verified similar relative performance on Samsung S24+ for 1B and 3B and Samsung S22 for 1B" ([Meta AI blog](https://ai.meta.com/blog/meta-llama-quantized-lightweight-models/)). No absolute Galaxy numbers are given.

**F. Apple on-device foundation model (reference, ~3B)**
- **2024, iPhone 15 Pro:** "on iPhone 15 Pro we are able to reach time-to-first-token latency of about 0.6 millisecond per prompt token, and a generation rate of 30 tokens per second. Notably, this performance is attained before employing token speculation techniques" ([Apple ML Research](https://machinelearning.apple.com/research/introducing-apple-foundation-models), 2024-06-10).
- **2025 update:** no tokens/s is published. It reports architecture changes instead: "reducing the KV cache memory usage by 37.5% and significantly improving the time-to-first-token" ([Apple ML Research, 2025 updates](https://machinelearning.apple.com/research/apple-foundation-models-2025-updates)).
- **2026:** no official Apple throughput figure was found on machinelearning.apple.com. Secondary blogs about a WWDC 2026 "AFM 3" disagree with each other (UNVERIFIED; not used).

**G. Which chip is in which Galaxy (needed to map numbers to phones)**
- **Galaxy S25:** "The Galaxy S25 series is powered by the Snapdragon ® 8 Elite for Galaxy ." ([Samsung Newsroom](https://news.samsung.com/global/samsung-galaxy-s25-series-sets-the-standard-of-ai-phone-as-a-true-ai-companion), 2025-01-23; via research subagent).
- **Galaxy S26 series** ([Samsung Newsroom](https://news.samsung.com/global/samsung-unveils-galaxy-s26-series-the-most-intuitive-galaxy-ai-phone-yet), 2026-02-26; verified):
  - "On Galaxy S26 Ultra, a customized mobile processor — Snapdragon® 8 Elite Gen 5 Mobile Platform for Galaxy".
  - Spec-table footnote: "Exynos 2600 * Type of AP may vary by device and market."
- **Galaxy S26 by model** ([Samsung Colombia support page](https://www.samsung.com/co/support/mobile-devices/specifications-and-features-of-the-s26-ultra-s26-and-s26/), undated; verified): "Galaxy S26 Ultra: Snapdragon® 8 Elite Gen 5 (3 nm) Galaxy S26: Exynos 2600 (2nm) Galaxy S26+: Exynos 2600 (2nm) Galaxy S26 FE: Exynos 2500 (3 nm)".
- **Korea split: UNVERIFIED.**
  - Pre-launch Korean press (e.g., [MTN, 2025-10-21](https://news.mtn.co.kr/news-detail/2025102106301967238)) reported Exynos 2600 for Korea/Europe units. These are secondary reports and were not read in full.
  - No Samsung Korea spec page was checked.
- **Galaxy Z Flip7 = Exynos 2500: UNVERIFIED.** No official Samsung quote was found; it appears only in secondary spec roundups.

**H. Chip-vendor claims (marketing, not measurements; conditions mostly unstated)**
- **Qualcomm Snapdragon 8 Elite Gen 5:**
  - "Up to 220 tokens per second for LLMs and LMMs" ([qualcomm.com mobile-ai](https://www.qualcomm.com/artificial-intelligence/mobile-ai), structured data, undated; verified in page source). Model and precision are not stated.
  - The [product page](https://www.qualcomm.com/smartphones/products/8-series/snapdragon-8-elite-gen-5) says "37% faster Hexagon NPU" (via research subagent; not re-verified because the page is JS-rendered).
  - Conflict: Qualcomm's own AI Hub shows 28.2 tok/s for Llama-3.2-3B W4A16 on the same chip. The 220 figure must not be used in a budget.
- **Qualcomm Snapdragon 8 Elite:** "45% AI performance improvement and 45% better performance per watt" ([product page](https://www.qualcomm.com/products/mobile/snapdragon/smartphones/snapdragon-8-series-mobile-platforms/snapdragon-8-elite-mobile-platform); via research subagent; JS-rendered, not re-verified). A "70+ tokens/s" claim appears only in secondary reports: UNVERIFIED.
- **Samsung Exynos 2500:** "59 trillion operations per second (TOPS), the Exynos 2500 brings on-device AI that represents a 39% improvement over its predecessor.¹" ([Samsung Semiconductor](https://semiconductor.samsung.com/processor/mobile-processor/exynos-2500/); verified).
- **Samsung Exynos 2600:** "a powerful NPU that improves generative AI performance by 113% compared to its predecessor.³" ([Samsung Semiconductor](https://semiconductor.samsung.com/processor/mobile-processor/exynos-2600/); verified). No tokens/s figure is given.
  - A pre-launch Korean press claim, from Samsung internal testing, that the Exynos 2600 NPU is "6배 이상" the A19 Pro: UNVERIFIED.
- **Galaxy S26 Ultra NPU:** in the paragraph introducing the Snapdragon chip, Samsung writes "A 39% improvement in NPU performance powers always-on Galaxy AI features" ([Newsroom](https://news.samsung.com/global/samsung-unveils-galaxy-s26-series-the-most-intuitive-galaxy-ai-phone-yet), 2026-02-26; verified).
- **MediaTek Dimensity 9400:** "80% faster LLM prompt performance*" and "> 50 tokens MLLM generation performance*" ([product page](https://www.mediatek.com/products/smartphones/dimensity-9400)).
- **MediaTek Dimensity 9500:** "Over 2x faster token generation speed" ([product page](https://www.mediatek.com/products/smartphones/dimensity-9500)).
  - Both via research subagent; not re-verified because the pages are JS-rendered. These chips are not used in Galaxy S/Z flagships.
- **Google Tensor G5:** "Gemini Nano runs 2.6x faster and 2x more efficiently for use cases like Pixel Screenshots and Recorder" ([Google blog](https://blog.google/products/pixel/tensor-g5-pixel-10/), 2025-08-20; via research subagent).
- **Google Tensor G4:** a "45 tokens/second" figure appears only in Android Authority: UNVERIFIED.
- **Apple:**
  - A18 Pro: "The new 16-core Neural Engine is faster and more efficient than the previous generation" (Apple Newsroom, 2024-09).
  - A19 Pro: "Neural Accelerators built into each GPU core" (Apple Newsroom, 2025-09).
  - Both quotes are via research subagent; the exact newsroom URLs were not captured (UNVERIFIED link). Neither gives an LLM tok/s figure.

**I. Independent and academic phone measurements (2024–2026)**
- **llama.cpp Hexagon (HTP) backend** ([docs](https://github.com/ggml-org/llama.cpp/blob/master/docs/backend/snapdragon/README.md), undated; via research subagent):
  - Llama-3.2-1B-Instruct Q4_0: "pp128 169.42 ± 1.75" t/s and "tg64 51.54 ± 1.13" t/s.
  - The log shows "Hexagon Arch version v79". Reading v79 as Snapdragon 8 Elite is an inference: UNVERIFIED.
  - Prefill here is about 10x lower than Qualcomm's own Genie numbers for the same model.
- **HeteroInfer** ([arXiv 2501.14794](https://arxiv.org/abs/2501.14794), v2 2025-10-04; Snapdragon 8 Gen 3 unless noted; via research subagent):
  - "Hetero-tensor achieves 1092 tokens/s during the prefill phase with a sequence length of 256 on InternLM-1.8B".
  - "Hetero-tensor reaches up to 14.01 tokens/s on Llama-8B, 29.9 tokens/s on Llama-3B and 51.12 token/s on InternLM-1.8B".
  - "On Snapdragon 8 Elite, Hetero-tensor achieves about 10.5% higher prefill performance than on Snapdragon 8 Gen 3".
- **llm.npu** ([arXiv 2407.05858](https://arxiv.org/abs/2407.05858), 2024; Snapdragon 8 Gen 3 / 8 Gen 2): "the first system that achieves > 1000 tokens/sec of prefill speed on COTS mobile devices for billion-sized LLMs" (via research subagent).
- **"When NPUs Are Not Always Faster"** ([arXiv 2605.27435](https://arxiv.org/abs/2605.27435), submitted 2026-05-22; Snapdragon 8 Gen 3; abstract verified): "CPUs outperform NPUs in the compute-intensive Prefill stage (up to 1.6x), while NPUs provide only limited acceleration in the memory-bound Decode stage (1.05-1.2x)."
  - This contradicts the NPU prefill gains reported by Qualcomm, llm.npu and HeteroInfer. The paper's model and framework were not captured.
- **"Phase Matters"** ([arXiv 2606.27906](https://arxiv.org/abs/2606.27906), submitted 2026-06-26; SM8750 = Snapdragon 8 Elite; FastVLM-0.5B, a vision-language model with image input):
  - Abstract (verified): "NPU execution is highly phase-dependent, delivering 1.64x speedup for prefill but only 1.18x for decode".
  - Body (via research subagent): "NPU delivers 1.64 × prefill throughput (197.43 vs. 120.64 tok/s) and 1.18 × decode throughput (113.06 vs. 95.49 tok/s)", with "64-tok prompt + 336 × 336 image, 128-tok output".
- **"LLM Inference at the Edge … Under Sustained Load"** ([arXiv 2603.23640](https://arxiv.org/abs/2603.23640), v1 2026-03-24). Setup: Qwen 2.5 1.5B at 4 bits; Galaxy S24 Ultra running "MLC-LLM 0.1.0" on GPU; iPhone 16 Pro (A18 Pro) running MLX.
  - Body (via research subagent): the iPhone "settles into a Hot-state plateau near 23.7 tok/s, while the S24 Ultra degrades ∼15% over 20 iterations into a Snapdragon governor-regulated plateau near 10 tok/s".
  - Conflict: the abstract (verified) instead says "the S24 Ultra suffers a hard OS-enforced GPU frequency floor that terminates inference entirely". This may be a version difference; unresolved.
- **HybridInfer** ([arXiv 2609.30270](https://arxiv.org/abs/2609.30270); arXiv shows "Submitted on 14 Jul 2026"; Galaxy S25+, 3B 4-bit on the GPU):
  - "sustained on-device generation repeatedly destabilized the GPU inference runtime, with the application crashing or silently wedging after a small number of consecutive on-device queries" (via research subagent).
  - Abstract (verified): "The failure lies in the current toolchain (OpenCL kernel compilation and long-prompt prefill on the mobile GPU), recurs even when the device is cool, and is worst for long generations."
- **MobileAIBench** ([arXiv 2406.10290](https://arxiv.org/abs/2406.10290), 2024; iPhone 14): "TinyLlama 1B 1.60 277.24 3.12 28.14" with columns "TTFT(s) ITPS(t/s) OET(s) OTPS(t/s)" (via research subagent). This is an older device and a reference only.
- **MLC-LLM:**
  - The 2023 Android blog (Galaxy S23, Snapdragon 8 Gen 2) gives no tok/s in its text.
  - The only MLC phone number found is the S24 Ultra plateau in 2603.23640 above.
- **Qualcomm's llama.cpp OpenCL (Adreno) blogs** (Nov 2024, Feb 2025): numbers could not be extracted because the pages are JavaScript-rendered. NOT FOUND.

### Inferences
- **Decode, not prefill, sets the latency.** On the S25/S26 NPU, a 500-token prefill costs about 0.08–0.3 s for 0.6–4B models with the GenieX/QAIRT runtime at ctx 1024. Generating 25 tokens costs about 0.28–1.2 s. For 1.7–4B models, decode is about 75–80% of per-call time (see Q5).
- **The runtime matters as much as the chip.** For Qwen3-4B on the same S25:
  - Genie (ctx 4096): 553.7 prefill and 26.1 decode tok/s.
  - GenieX-QAIRT (ctx 1024): 1754.9 prefill and 22.3 decode tok/s.
  - The S25 → S26 gain for the same model and runtime is small. For Qwen3-4B QAIRT ctx 1024 it is 1754.9 → 1768.6 prefill and 22.3 → 21.8 decode.
- **Compile with the smallest context that fits.** The prompt (≤600 tokens) plus output (≤30) fits in a 1024 context. Every larger compiled context in the Qwen3-4B data lowers decode, down to 17.5 tok/s at 4096.
- **GPU and NPU are both viable on the S26.** LiteRT-LM's GPU path for Gemma 4 E2B (3,808 / 52.1 tok/s) beats AI Hub's llama.cpp-GPU path for the same model (455.7 / 31.8). Stack choice can swing results by several times.
- **Gemini Nano's only published decode rate is the slowest number here.** Pixel 9 Pro, nano-v2: 11 tok/s. Galaxy-specific speeds and nano-v3/v4 decode rates are unpublished, so a Gemini-Nano-based budget for Galaxy cannot be sourced today.

### Gaps
- No primary-source LLM tokens/s for Exynos 2500 / 2600.
  - AI Hub is Qualcomm-only, and LiteRT-LM's tables have no Exynos row.
  - Samsung gives only a "113%" generative-AI uplift claim for the Exynos 2600 and "59 TOPS" for the Exynos 2500.
  - This matters because Samsung Colombia lists the Galaxy S26/S26+ as Exynos 2600 (Q1-G). The Korean-market split is not verified.
- No independent short-prompt (≤600-token) phone measurement exists for 2025–2026 Galaxy devices; the academic papers use the Snapdragon 8 Gen 3 or vision-language models.
- Qualcomm's llama.cpp OpenCL blog numbers could not be extracted.
- No Gemini Nano decode speed for nano-v3/v4, and none on any Galaxy.
- AI Hub's S25 rows duplicate the "Dragonwing Q-8750" rows. It is unclear whether a retail S25 produced them.
- LiteRT-LM's Galaxy S26 Ultra rows have no NPU entry. Google's LiteRT NPU figures are for FastVLM on a Xiaomi phone and Gemma 3n on a Vivo phone.

## Q2. Memory footprint (4-bit), quantization, battery/thermal behavior for short generations

### Takeaway
Measured resident memory for 4-bit models on CPU paths:
- Llama-3.2-1B: ≈1.9–2.2 GiB (1,921–2,255 MiB RSS; ExecuTorch, 2024).
- Llama-3.2-3B: ≈3.6–4.0 GiB (3,726–4,060 MiB).
- Gemma 4 E4B on the S26 Ultra: ≈3.3 GB (CPU backend).

Gemma 4 E2B in LiteRT-LM is the outlier because its embeddings are memory-mapped. Its CPU-side RSS on the S26 Ultra is 676 MB on the GPU path and 1,733 MB on the CPU path; GPU-side memory is not reported. The KV cache for a ≤600-token prompt is small, under 0.1 GB. Thermal effects are documented only for sustained or repeated long runs, not for single 25-token outputs.

### Cited Findings
- **Gemma 4 E2B, LiteRT-LM** ([card](https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm)):
  - Quantization: "LiteRT-LM uses a state of the art Gemma-4 mobile quantization scheme that uses a mixture of 2bit, 4bit and 8 bit weights. This means that for text only use cases the weight footprint in memory can be as low as 0.8 GB while the runtime uses memory mapping to support the 1.12GB of embedding parameters."
  - S26 Ultra: model file 2583 MB. "CPU Memory (MB)" is 1733 with the CPU backend and 676 with the GPU backend.
  - How memory is measured: "CPU memory was measured using, `rusage::ru_maxrss` on Android". GPU-side memory is not reported for Android.
- **Gemma 4 E2B, Google blogs:**
  - "Run Gemma 4 E2B using <1.5GB memory on some devices thanks to LiteRT's support for 2-bit and 4-bit weights along with memory-mapped per-layer embeddings" ([blog](https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/), 2026-04-02).
  - "LiteRT-LM successfully runs the ~2.58GB Gemma 4 E2B model with a physical memory footprint of just 607MB on Apple mobile CPUs utilizing XNNPACK's weight caching mechanism" ([blog](https://developers.googleblog.com/blazing-fast-on-device-genai-with-litert-lm/), 2026-05-19).
- **Gemma 4 E4B** ([card](https://huggingface.co/litert-community/gemma-4-E4B-it-litert-lm)):
  - Composition: "The model file size is 3.66 GB, which includes a text decoder with 2.24 GB of weights and 0.67 GB of embedding parameters."
  - S26 Ultra CPU memory: 3283 MB with the CPU backend, 710 MB with the GPU backend.
- **Qwen2.5-1.5B dynamic_int8 on the S25 Ultra** ([card](https://huggingface.co/litert-community/Qwen2.5-1.5B-Instruct)):
  - Model 1598 MB.
  - CPU backend peak RSS: 1997 MB at ctx 1280, 2216 MB at ctx 4096.
  - GPU backend: peak RSS 1846 MB plus "GPU Memory (RSS in MB)" 1505.
  - fp32 baseline: 6182 MB model, 6254 MB RSS.
- **Qwen3-0.6B LiteRT files** ([card](https://huggingface.co/litert-community/Qwen3-0.6B)):
  - "dynamic INT8 weights, float KV | 4096 | 586 MB"
  - "TorchAO mixed INT4, float KV | 2048 | 474.61 MiB"
  - "dynamic INT4 (block-32) weights … | 4096 | 328 MiB"
  - Peak private footprint on SM-S937U1 GPU: 585 MB at ctx 2048, 2940 MB at ctx 4096 (community measurement). The compiled context length changes the footprint a lot.
- **ExecuTorch Llama 3.2 on OnePlus 12, CPU, 2024** ([README](https://raw.githubusercontent.com/pytorch/executorch/main/examples/models/llama/README.md)):
  - 1B: SpinQuant 1,083 MiB file / 1,921 MiB RSS; BF16 2,358 / 3,185.
  - 3B: SpinQuant 2,435 / 3,726; QAT+LoRA 2,529 / 4,060; BF16 6,129 / 7,419.
  - Scheme: "We quantize all linear layers in all transformer blocks to a 4-bit groupwise scheme (with a group size of 32) for weights and 8-bit per-token dynamic quantization for activations … We employ an 8-bit per channel quantization for embedding."
  - Meta's summary: "an average reduction of 56% in model size and a 41% average reduction in memory usage compared to the original BF16 format" ([Meta](https://ai.meta.com/blog/meta-llama-quantized-lightweight-models/), 2024-10-24).
- **Apple ~3B on-device model:**
  - 2024: "a mixed 2-bit and 4-bit configuration strategy — averaging 3.7 bits-per-weight … the model can be compressed to 3.5 bits-per-weight without significant quality loss" ([2024](https://machinelearning.apple.com/research/introducing-apple-foundation-models)).
  - 2025: "We compressed the on-device model to 2 bits per weight (bpw) using Quantization-Aware-Training (QAT)" and "we quantized the embedding table to 4 bits per weight … The KV cache was quantized to 8 bits per weight" ([2025](https://machinelearning.apple.com/research/apple-foundation-models-2025-updates)).
- **Model shapes for KV-cache math** (Hugging Face `config.json`):
  - Qwen3-4B: "num_hidden_layers": 36, "num_key_value_heads": 8, "head_dim": 128.
  - Qwen3-1.7B and Qwen3-0.6B: "num_hidden_layers": 28, "num_key_value_heads": 8, "head_dim": 128.
  - Sources: [Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B/raw/main/config.json), [Qwen3-1.7B](https://huggingface.co/Qwen/Qwen3-1.7B/raw/main/config.json), [Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B/raw/main/config.json).
- **Thermal and run-to-run variance on Galaxy** (community measurement, [Qwen3-0.6B card](https://huggingface.co/litert-community/Qwen3-0.6B)):
  - "The phones lower their CPU clocks within the first of the three CPU runs (this file's first run prefilled at 365 tok/s on the Galaxy S26 and 111 tok/s on the Pixel 8a), so the CPU cells are not sustained rates."
  - "Results depend on device SKU, OS build, thermal state, battery mode, backend, model quantization, runtime version, and benchmark settings."
- **Gemini Nano battery and quota** ([ML Kit GenAI overview](https://developers.google.com/ml-kit/genai), updated 2026-10-29):
  - "AICore enforces an inference quota per app. Making too many GenAI API requests in a short period will result in an ErrorCode.BUSY response."
  - "ErrorCode.PER_APP_BATTERY_USE_QUOTA_EXCEEDED can be returned if an app exceeds a long-duration quota (for example, a daily quota)."
  - Gemini Nano 4 "uses up to 60% less battery" than previous versions ([2026-04-02](https://android-developers.googleblog.com/2026/04/AI-Core-Developer-Preview.html)).
- **Cold start and compilation** (these costs come on top of TTFT):
  - LiteRT: "Time-to-first-token does not include load time."
  - MediaTek NPU JIT: "on-device compilation for such a large model can take over a minute, making AOT the more practical choice for production" ([MediaTek NPU and LiteRT](https://developers.googleblog.com/en/mediatek-npu-and-litert-powering-the-next-generation-of-on-device-ai/)). This refers to Gemma 3 270M.
  - Gemini Nano: "warmup() . This loads Gemini Nano into memory and initializes runtime components" ([ML Kit get-started](https://developers.google.com/ml-kit/genai/prompt/android/get-started); verified).

- **Energy per token, CPU, 2024 devices** ([arXiv 2410.03613](https://arxiv.org/abs/2410.03613), "Understanding Large Language Models in Your Pockets: Performance Study on COTS Mobile Devices", v5 2026-02-09; llama.cpp; via research subagent):
  - "For CPU-based inference with a 64 -token prompt and 128 -token generation on modern high-tier mobile devices, power consumption is approximately 20 mAh per round."
  - "prefill energy consumption drops to its lowest point at 0.031 mAh per token"
  - "decode energy remains nearly unchanged at approximately 0.12mAh/token"
  - GPU decode: "reducing energy consumption to 0.058mAh/token, a 59.75% decrease."
  - Throttling: "During subsequent stages of the inference, both prime and performance cores on Snapdragon 8 Gen 3 experience a rapid reduction in frequency." This was measured over "20 continuous inference tests on four devices with warm up".
  - The model behind the mAh figures was not captured.
- **Thermal, NPU vs CPU, Snapdragon 8 Elite** ([arXiv 2606.27906](https://arxiv.org/abs/2606.27906), FastVLM-0.5B; via research subagent):
  - "Under deliberate thermal stress (15 minutes of continuous VLM inference), CPU paths reach 82 ∘ C and trigger governor-driven clock reduction, while NPU paths stabilize at 66 ∘ C"
  - The slowdown is "inflating CPU latency by 1.3–2.1 × under sustained load—invisible in short-burst benchmarks".
  - The abstract (verified) reports "10.47 degrees C lower steady-state temperature" for NPU execution.
- **Start-up cost on the same SoC** (2606.27906, via research subagent):
  - NPU executor init is 536.0 ms versus 83.6 ms on CPU: "Executor init (S2): first-token overhead with model loaded and QNN context cache intact".
  - NPU-only cold start is 26,820 ms versus 2,080 ms warm.
- **Sustained-load decline on phones** ([arXiv 2603.23640](https://arxiv.org/abs/2603.23640), Qwen2.5-1.5B 4-bit, fixed 258-token prompt, 20 iterations; abstract verified):
  - "thermal management supersedes peak compute as the primary constraint: the iPhone 16 Pro loses nearly half its throughput within two iterations, and the S24 Ultra suffers a hard OS-enforced GPU frequency floor that terminates inference entirely."
  - This workload is long-form generation, unlike Weave's 25-token outputs.
- **GPU-runtime instability on a Galaxy S25+** ([arXiv 2609.30270](https://arxiv.org/abs/2609.30270), abstract verified): the failure "recurs even when the device is cool, and is worst for long generations".
- **NPU offload can cost more energy** ([arXiv 2605.27435](https://arxiv.org/abs/2605.27435), Snapdragon 8 Gen 3; via research subagent): "increasing NPU offloading leads to higher energy consumption (up to 51%)."
- **Battery drain and output length** ([MobileAIBench, arXiv 2406.10290](https://arxiv.org/abs/2406.10290), iPhone 14; via research subagent): "Battery Drain Rate (BDR) increases with both model size and the number of output tokens generated."
- **Short generations specifically:** no source measured throttling or battery cost for ~25-token generations (NOT FOUND, per research subagent). All throttling evidence comes from sustained or back-to-back long runs.

### Inferences
- **Rule of thumb, weights only.** 4-bit ≈ 0.5 byte per parameter, so about 0.5 GB for 1B, 1.5 GB for 3B and 2.0 GB for 4B. Measured process memory runs about 1.5–2x the weight bytes on CPU paths. Examples: Llama-3.2-1B SpinQuant 1,921 MiB RSS for a 1,083 MiB file; 3B 3,726 MiB for 2,435 MiB.
- **KV cache at Weave's prompt sizes** (my arithmetic, fp16 K and V):
  - Qwen3-4B: 36 × 8 × 128 × 2 × 2 B = 147,456 B/token, so about 88 MB for 600 tokens.
  - Qwen3-1.7B and 0.6B: 28 × 8 × 128 × 2 × 2 B = 114,688 B/token, about 69 MB for 600 tokens.
  - Both are negligible next to the weights. The larger driver is the compiled or allocated context length (the 585 MB vs 2940 MB Qwen3-0.6B example), so ctx should be kept at about 1024.
- **Thermal throttling is unlikely to dominate.** One hop is about 0.5–1.5 s of accelerator time, and a question is about 2 hops. Every throttling result found comes from sustained loads:
  - 20 back-to-back runs (2410.03613, 2603.23640);
  - 15 minutes of continuous inference (2606.27906);
  - repeated 1024+256-token CPU benchmarks (Qwen3-0.6B card).
  2606.27906 itself calls the effect "invisible in short-burst benchmarks". The NPU ran 16 °C cooler than the CPU under stress in that study, which favors NPU/GPU paths. This is an inference; no short-burst measurement exists.
- **Energy per hop, CPU worst case** (my arithmetic from 2410.03613's 2024 CPU figures; model unspecified): 500 × 0.031 mAh + 25 × 0.12 mAh = 15.5 + 3.0 ≈ 18.5 mAh per hop on CPU. NPU/GPU paths should be well below this, but no Galaxy NPU energy figure was found. Treat this only as an upper-bound order of magnitude.
- **Keep the model warm.** On the Snapdragon 8 Elite, NPU executor init adds about 0.54 s to first-token latency, and an NPU cold start reached about 26.8 s (2606.27906, FastVLM). A rewrite model should be loaded once per session, not per hop.
- **Memory pressure is the practical risk.** A separately bundled 3–4B model adds about 2–4 GB of resident memory alongside the embedding model and the app. That makes app-process kills or reloads (cold-start cost) more likely. The 1–2B class or a system-shared model (Gemini Nano) avoids most of this.

### Gaps
- No Samsung or Qualcomm-published energy-per-token or thermal data for ≤4B LLMs on the S25/S26.
- The AI Hub `perf.yaml` files have no LLM memory figures.
- Gemini Nano's memory footprint and quota values are unpublished.

## Q3. What on-device model can a Galaxy feature actually use? (Gemini Nano / AICore / ML Kit GenAI, Samsung Gauss, shipping its own model)

### Takeaway
A regular third-party app on Galaxy can use Gemini Nano's custom-prompt API ("direct model access", formerly the Prompt API, still in beta) only on the Galaxy S26 series, Z Fold7, Z TriFold and Z Flip8 / Fold8 / Fold8 Ultra. It must be the top foreground app, it is subject to per-app quotas, and it cannot supply its own LoRA. The Galaxy S25 gets only the fixed task APIs: Summarization, Proofreading and Rewriting, which list Korean, plus Image Description. Korean support for custom prompts is not documented. Google's own guidance for customized needs is to bundle an open model via LiteRT-LM. Samsung says it has an on-device Gauss2 "Compact" model, but no source confirms which shipping feature runs it, and no third-party access exists.

### Cited Findings
- **Status and naming:**
  - "With ML Kit's direct model access (com.google.mlkit:genai-prompt), you can send custom natural language requests on-device to the Gemini Nano foundation model through the GenerativeModel class."
  - "This API is offered in beta, and is not subject to any SLA or deprecation policy."
  - Source: [ML Kit Prompt / direct model access](https://developers.google.com/ml-kit/genai/prompt/android), updated 2026-10-27. Artifact string: "com.google.mlkit:genai-prompt:1.0.0-beta4" (per research subagent).
- **Galaxy devices for custom prompts** ([ML Kit GenAI overview](https://developers.google.com/ml-kit/genai), "Last updated 2026-10-29 UTC"; verified by direct fetch). The list opens "Direct model access and agentic workflows are supported on the following devices:". Samsung rows:
  - nano-v2: "Samsung: Galaxy Z Fold7, Galaxy Z TriFold".
  - nano-v3: "Samsung: Galaxy S26, Galaxy S26+, Galaxy S26 Ultra".
  - nano-v4: "Samsung: Galaxy Z Flip8, Galaxy Z Fold8, Galaxy Z Fold8 Ultra".
- **Galaxy devices for the fixed task APIs:**
  - Scope: "The Image Description, Summarization, Proofreading, and Rewriting APIs are available on the following devices".
  - Samsung row: "Samsung: Galaxy S25, Galaxy S25+, Galaxy S25 Ultra, Galaxy S26, Galaxy S26+, Galaxy S26 Ultra, Galaxy Z Flip8, Galaxy Z Fold8, Galaxy Z Fold8 Ultra, Galaxy Z Fold7, Galaxy Z TriFold".
  - So the Galaxy S25 is not on the custom-prompt list, and the Galaxy S24 is on neither list.
- **Limits** (same overview page):
  - Rate: "AICore enforces an inference quota per app. Making too many GenAI API requests in a short period will result in an ErrorCode.BUSY response."
  - Battery: "ErrorCode.PER_APP_BATTERY_USE_QUOTA_EXCEEDED can be returned if an app exceeds a long-duration quota (for example, a daily quota)."
  - Foreground only: "GenAI API inference is permitted only when the app is the top foreground application. Using the API when the app is not in the foreground, including using a foreground service, will result in an ErrorCode.BACKGROUND_USE_BLOCKED response."
- **Context limit** ([get-started page](https://developers.google.com/ml-kit/genai/prompt/android/get-started), 2026-10-27; verified): "under 4000 tokens, or approximately 3000 English words)" and "Use cases that require long output (more than 4K tokens) should be avoided."
- **Other constraints:**
  - The same get-started page says the API is not supported on devices with an "unlocked bootloader" (verified).
  - It also says "warmup() . This loads Gemini Nano into memory and initializes runtime components" (verified).
  - From the [AICore Developer Preview page](https://developers.google.com/ml-kit/genai/aicore-dev-preview), via research subagent: "Note: The option to bypass quota limits is only available on Pixel devices."
- **Korean support:**
  - Summarization: "The GenAI Summarization API supports English, Japanese, and Korean".
  - Proofreading: "Proofreading is supported for the following languages: English, Japanese, French, German, Italian, Spanish, and Korean".
  - Rewriting: "The GenAI Rewriting API supports the following languages: English, Japanese, French, German, Italian, Spanish, and Korean".
  - Proofreading and Rewriting: "Input should be less than 256 tokens."
  - Direct model access (Prompt API): no Korean statement found on any of its pages.
  - All quoted by research subagent from the per-API ML Kit pages, updated 2026-10-28.
- **Production Korean use exists.** Kakao Mobility used the Prompt API "to process users' delivery orders written in natural language" ([Android Developers Blog](https://android-developers.googleblog.com/2025/10/kakao-mobility-uses-gemini-nano-on.html), 2025-10). They also needed a fallback: "To maximize the feature's reach and provide a robust fallback, the team also implemented a cloud-based path using Gemini Flash."
- **No custom LoRA or fine-tuning:**
  - "The text and image task APIs use task-specific feature types and fine-tuned LoRA adapters on top of the shared base model."
  - "Each task-specific API has fixed LoRA fine-tuning and a built-in prompt".
  - Google points custom needs elsewhere: "For highly customized or niche use cases, you can also use LiteRT-LM to bring your own fine-tuned small language model to Android." ([I/O '26 blog](https://android-developers.googleblog.com/2026/05/android-ai-intelligence-system.html), 2026-05-26)
  - The first two quotes are from the Prompt API page via research subagent. No developer-supplied LoRA path for Gemini Nano was found.
- **Gemma 4 is now the Gemini Nano base:**
  - "On supported Android devices, Gemma 4 is available through Android AI Core as Gemini Nano, which is the recommended path for production applications." ([Gemma 4 E2B LiteRT card](https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm))
  - "Developers can also access and deploy Android's built-in and optimized Gemma 4 model system-wide via Android AICore." ([2026-04-02](https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/))
  - "code you write today for Gemma 4 will automatically work on Gemini Nano 4-enabled devices that will be available later this year" ([2026-04-02](https://android-developers.googleblog.com/2026/04/AI-Core-Developer-Preview.html)).
- **Google's fallback position:** "On supported Android devices you can use Gemini Nano through ML Kit. For markets where Gemini Nano is not supported or if you have use cases that require deeper customization, we now unlock the full potential of open-weight models." ([2025-12-08](https://developers.googleblog.com/en/mediatek-npu-and-litert-powering-the-next-generation-of-on-device-ai/))
- **AICore isolation:** "Gemini Nano runs in Android's AICore system service, which leverages device hardware to enable low inference latency" and "Restricted Package Binding: AICore is isolated from most other packages, with limited exceptions for specific system packages." ([developer.android.com/ai/gemini-nano](https://developer.android.com/ai/gemini-nano), 2026-10-29, via research subagent)
- **Samsung Gauss:**
  - 2023: "Samsung Gauss Language, a generative language model, enhances work efficiency by facilitating tasks such as composing emails, summarizing documents and translating content." ([Newsroom](https://news.samsung.com/global/samsung-ai-forum-2023-day-2-discussing-technological-trends-and-the-future-of-generative-ai), 2023-11-08)
  - Gauss2: "The Compact model is a small-sized model specifically designed to work efficiently, even in limited computing environments. It delivers optimized performance for on-device usage". Samsung "plan[s] to integrate it into products" ([Newsroom](https://news.samsung.com/global/samsung-electronics-hosts-samsung-developer-conference-korea-2024-unveils-its-improved-gen-ai-model), SDC24 Korea, 2024-11-21).
  - Correction to the brief: Gauss2 was announced at SDC24 Korea in November 2024, not in October.
  - Languages: "Samsung Gauss2 supports 9 to 14 languages as well as various programming languages, depending on the model."
  - No source found naming a shipping Galaxy feature that runs Gauss on-device.
- **Gemini Nano on Galaxy since the S24:** "The S24 series will also use Gemini Nano, an on-device LLM delivered as part of the Android 14 operating system" ([Newsroom](https://news.samsung.com/global/samsung-and-google-cloud-join-forces-to-bring-generative-ai-to-samsung-galaxy-s24-series), 2024-01-18).
- **Which Galaxy AI features run on-device** ([Samsung US support](https://www.samsung.com/us/support/answer/ANS10000753/), undated):
  - "On-device functions include: Translation, time and weather Ambient wallpapers, and Google Messages (Magic Compose, message suggestions, and rewrite suggestions)."
  - "Cloud-based functions include: Auto formatting, auto summarizing, auto corrections, and image editing."
  - Switch: "Settings, then tap Galaxy AI, and then tap the switch by Process data only on device".
  - Keyboard features on the [UK S24 page](https://www.samsung.com/uk/support/mobile-devices/how-to-use-the-galaxy-ai-features-on-the-s24-series/) (table cells joined by research subagent):
    - "Chat translation | Keyboard | ✓ | ✓ | X" (Offline ✓).
    - "Style and grammar* | Keyboard | ✓ | ✓ | ✓", footnoted "*You may have to turn on the Process data only on device setting to use the Style and grammar keyboard feature."
  - These two pages conflict on whether auto-corrections are cloud-only.
- **Galaxy S25 and S26 on-device statements:**
  - S25 Personal Data Engine: "safely analyzing your data on-device" ([2025-01-23](https://news.samsung.com/global/samsung-galaxy-s25-series-sets-the-standard-of-ai-phone-as-a-true-ai-companion)).
  - S26 ([2026-02-26](https://news.samsung.com/global/samsung-unveils-galaxy-s26-series-the-most-intuitive-galaxy-ai-phone-yet)): "For on-device Galaxy AI, Personal Data Engine (PDE) enables context-aware, personalized AI experiences."
  - S26 NPU: "A 39% improvement in NPU performance powers always-on Galaxy AI features".
  - S26 processor row: "Snapdragon® 8 Elite Gen 5 for Galaxy, Exynos 2600".
- **Paths for shipping your own model:**
  - Exynos: "Exynos AI Studio is a toolchain that generates AI models developed by customers into a form that can run on Exynos mobile processors" and "Samsung is collaborating with Meta to support its Exynos back-end for the ExecuTorch framework" ([Samsung Semiconductor](https://semiconductor.samsung.com/technologies/processor/on-device-ai/), undated, via research subagent).
  - Snapdragon: "Android: Snapdragon® 8 Elite Gen 5, Snapdragon® 8 Elite (e.g. Samsung Galaxy Series)" ([AI Hub LLM-on-Genie tutorial](https://raw.githubusercontent.com/quic/ai-hub-apps/main/tutorials/llm_on_genie/README.md), via research subagent).
  - A Google LiteRT page titled "Samsung NPU (Exynos AI LiteCore) with LiteRT" exists (https://developers.google.com/edge/litert/next/samsung). Only its title was seen; contents UNVERIFIED.

### Inferences
- **For Weave as an app on today's Galaxy fleet,** Gemini Nano custom prompts cover only S26-class and newer foldables. The S25 is excluded, and the S24 is absent from both ML Kit lists, although Samsung's own S24 features use Gemini Nano. Korean quality and support are undocumented for custom prompts, and quotas plus BUSY retries add latency variance.
- **Bundling a 0.6–4B open model is the path Google itself recommends for customization.** Options are LiteRT-LM on GPU/CPU (NPU on Android) or Qualcomm Genie/QAIRT on Snapdragon. It is also the only way to fine-tune or LoRA a rewrite-specific model. This works on S25 and S26 with sourced numbers (Q1). The cost is app size and resident memory (Q2).
- **A Samsung system feature (e.g., inside Samsung Keyboard) could ship its own model.** Samsung Keyboard's Chat translation already works offline, so some on-device model ships inside it, though whose model is not stated. Samsung also markets Gauss2 Compact for on-device use. Two facts are not documented anywhere public:
  - Which model the keyboard actually uses.
  - Whether a Samsung system app gets AICore privileges ("limited exceptions for specific system packages").
- **The S26's split SoC (Snapdragon vs Exynos 2600 by market) matters for Korea.** A Snapdragon-only NPU build (Genie/QAIRT) would not cover Exynos units. LiteRT-LM GPU/CPU, or LiteRT's Samsung NPU path, would be needed. Which S26 SKUs use which chip in Korea is not established in these notes.

### Gaps
- Korean support for Gemini Nano direct model access: not documented.
- Actual quota numbers (per-minute or daily): not published.
- Which Galaxy AI feature runs which model (Gauss vs Gemini Nano): not published.
- Whether third parties can use Samsung's on-device models: no statement either way.
- Gauss updates after November 2024: none found.
- Which S26 SKUs use Exynos 2600 in the Korean market: not verified from a Samsung Korea page.
  - Samsung Colombia lists S26/S26+ as Exynos 2600 and the S26 Ultra as Snapdragon (Q1-G).
  - The global newsroom says "Type of AP may vary by device and market."
  - Gemini Nano itself appears to cover Exynos 2600 units. The ML Kit speech-recognition chipset list includes "Samsung Exynos: Exynos 2600" alongside "Qualcomm Snapdragon: SM8750, SM8845, SM8850, …" (via research subagent), and the S26 series is listed without SKU distinction.
  - The AI Hub and Genie/QAIRT numbers in Q1 apply only to Snapdragon units.

## Q4. Korean-capable small open models (≤4B): sizes, licenses, Korean benchmark claims

### Takeaway
Three Korean-capable ≤4B model families are both Apache-2.0 and measured on Galaxy hardware: Qwen3 0.6/1.7/4B, Qwen3.5 0.8/2B and Gemma 4 E2B/E4B. All have Qualcomm AI Hub (S25/S26) or LiteRT-LM (S26 Ultra) numbers. Qwen3 is the only one of the three with official Korean scores, from its tech report. Gemma 4 is also what AICore exposes as Gemini Nano, per Google's LiteRT card ("Gemma 4 is available through Android AI Core as Gemini Nano").

The Korea-built models have the strongest vendor-reported Korean scores at ≤2.4B, but their licences restrict commercial or on-device use:
- EXAONE 3.5 2.4B and 4.0 1.2B: non-commercial (NC) licences.
- Kanana-2 1.3B/3B (July 2026): a separate licence is required for "Offering or (re)selling to third parties … embedded in on-device domains."
- HyperCLOVA X SEED: a licence request is required above 10M MAU or for competing products.

The exception is Kanana 1.5 2.1B, which is Apache-2.0. Llama 3.2 does not officially support Korean. None of the Korea-built models has a published phone measurement.

### Cited Findings
**Overview.** Parameter counts and dates are from the model cards; "API" means Hugging Face API metadata. Korean scores are vendor-reported and use different harnesses, so they are not directly comparable across rows.

| Model | Params | Released | Licence → commercial / on-device use | Context | Korean evidence | Phone numbers in Q1? |
|---|---|---|---|---|---|---|
| EXAONE 3.5 2.4B-Instruct | 2.14B non-emb | 2024-12-09 | EXAONE 1.1-NC → prohibited | 32,768 | KoMT-Bench 7.24, LogicKor 8.51 (LG) | No (official GGUF/AWQ only) |
| EXAONE 4.0 1.2B | 1.07B non-emb (1.28B) | 2025-07-15 | EXAONE 1.2-NC → prohibited | 65,536 | KMMLU-Pro 37.5, KMMLU-Redux 40.4 (non-reasoning; LG) | No |
| Kanana-Nano-2.1B-Instruct | ≈2.09B (API) | 2025-02-27 | CC-BY-NC-4.0 → prohibited | not stated | KoMT-Bench 5.857, LogicKor 7.964, KMMLU 38.51 (Kakao) | No |
| Kanana-1.5-2.1B-Instruct-2505 | ≈2.32B (API) | 2025-05-23 | Apache-2.0 → allowed | 32K native | KoMT-Bench 6.54, KMMLU (0-shot CoT) 32.93 (Kakao) | No |
| Kanana-2-1.3B / 3B-Instruct | ≈1.29B / ≈3.51B (API) | 2026-07-27 | Kanana Open License → separate licence for on-device embedding offered to third parties | 32,768 | KoMT-Bench 6.54 / 6.92; KMMLU-CoT 42.79 / 43.32 (Kakao) | No |
| HyperCLOVA X SEED Text 0.5B / 1.5B | 0.57B / 1.5B | 2025-04-22 | SEED licence → request a licence if >10M MAU or competing | 4K / 16k | KMMLU 0.3815 / 0.3933; HAE-RAE 0.5619 / 0.5674 (Naver) | No |
| HyperCLOVA X SEED Vision 3B | 3.2B LLM + 0.43B vision | 2025-04-22 | same | 16k | KMMLU 0.4422 (Naver) | No |
| Qwen3 0.6B / 1.7B / 4B | 0.6 / 1.7 / 4.0B (0.44 / 1.4 / 3.6B non-emb) | 2025-04-29 (blog) | Apache-2.0 → allowed | 32,768 | Korean average 26.9 / 33.7 / 42.0 non-thinking; 30.5 / 49.2 / 63.9 thinking (Qwen) | Yes (AI Hub S25/S26) |
| Qwen3-4B-Instruct-2507 | 4.0B | 2025-08 (API) | Apache-2.0 | 262,144 | no Korean-specific score | Yes (AI Hub) |
| Qwen3.5 0.8B / 2B | ≈0.87B / ≈2.27B (API) | 2026-02-28 (API) | Apache-2.0 | 262,144 | "201 languages", Korean not named; KoMT-Bench 5.21 for 2B per Kakao | Yes (AI Hub llama.cpp) |
| Gemma 3 1B / 4B | ≈1.0B / ≈4.3B | 2025-03-10 | Gemma Terms of Use | 32K / 128K | none from Google; LG reports KMMLU-Pro 9.7 for 1B | LiteRT S24 Ultra (1B) |
| Gemma 3n E2B / E4B | "effective" 2B / 4B | 2025-06-26 | Gemma Terms of Use | 32K | none | LiteRT S24 Ultra |
| Gemma 4 E2B / E4B | 2.3B eff (5.1B with embeddings) / 4.5B eff (8B) | 2026-03-31 | Apache-2.0 → allowed | 128K | MMMLU 67.4% / 76.6% (multilingual, not Korean-only) | Yes (LiteRT S26 Ultra; AI Hub S25/S26) |
| Llama 3.2 1B / 3B | 1.23B / 3.21B | 2024-09-25 | Llama 3.2 Community License (700M-MAU clause) | 128k | Korean not officially supported; LG reports KoMT-Bench 3.16 for 3B | Yes (AI Hub; ExecuTorch) |

**LG EXAONE**
- **EXAONE 4.0 1.2B** ([card](https://huggingface.co/LGAI-EXAONE/EXAONE-4.0-1.2B); verified by direct fetch):
  - Positioning: "a small-size 1.2B model designed for on-device applications".
  - "1.2B Non-Reasoning Mode" table, columns EXAONE 4.0 1.2B | Qwen 3 0.6B | Gemma 3 1B | Qwen 3 1.7B | SmolLM 3 3B:
    - "KMMLU-Pro | 37.5 | 24.6 | 9.7 | 29.5 | 27.6"
    - "KMMLU-Redux | 40.4 | 22.8 | 19.4 | 29.8 | 26.4"
    - "Ko-LongBench | 69.8 | 16.4 | N/A | 57.1 | 15.7"
    - "IFEval | 74.7 | 54.5 | 80.2 | 68.2 | 76.7"
  - Reasoning mode: "KMMLU-Pro | 42.7 | 24.6 | 21.6 | 38.3 | 30.5".
  - Release (GitHub): "2025.07.15 : We release EXAONE 4.0, a hybrid reasoning model with enhanced usability including 32B and 1.2B." (via research subagent)
- **EXAONE 3.5 2.4B** ([card](https://huggingface.co/LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct); via research subagent):
  - Specs: "Number of Parameters (without embeddings): 2.14B"; "Context Length: 32,768 tokens"; "optimized for deployment on small or resource-constrained devices".
  - Columns end "… KoMT-Bench | LogicKor":
    - "EXAONE 3.5 2.4B | 7.81 | 33.0 | 48.2 | 37.1 | 73.6 | 7.24 | 8.51"
    - "Qwen 2.5 3B | … | 5.68 | 5.21"
    - "Llama 3.2 3B | … | 3.16 | 2.86"
- **Licence** (EXAONE 1.1-NC / 1.2-NC §3.1; via research subagent): "The Licensee is expressly prohibited from using the Model, Derivatives, or Output for any commercial purposes, including but not limited to, developing or deploying products, services, or applications that generate revenue, whether directly or indirectly. Any commercial exploitation of the Model or its derivatives requires a separate commercial license agreement with the Licensor."
- **Builds:**
  - Official GGUF Q4_K_M files: EXAONE-4.0-1.2B 812,437,792 B; EXAONE-3.5-2.4B 1,644,918,272 B (HF API; via research subagent).
  - No Qualcomm AI Hub or litert-community EXAONE build was found.
- **EXAONE Deep 2.4B (2025-03-18)** is a reasoning model under the same NC licence. It is not suited to 25-token outputs.
- **No newer ≤4B EXAONE** was released after July 2025. Later releases are 32B or larger, including "K-EXAONE" (via research subagent).

**Kakao Kanana**
- **Kanana-2 1.3B** ([card](https://huggingface.co/kakaocorp/kanana-2-1.3b-instruct); verified):
  - Positioning: "Kanana-2-1.3B-Instruct — instruction-tuned 1.3B model for on-device deployment".
  - Tokenizer: "Kanana-2 tokenizer: Improves Korean tokenization efficiency by over 30% compared to the previous generation."
  - Results, columns kanana-2-3b-instruct | kanana-2-1.3b-instruct | Qwen3.5-2B | Qwen3-1.7B:
    - "KoMT-Bench† | judge | 6.92 | 6.54 | 5.21 | 5.29"
    - "KMMLU-CoT | acc | 43.32 | 42.79 | 41.75 | 37.84"
    - "HAERAE-Bench (v1.0)-CoT | acc | 43.75 | 44.89 | 27.84 | 27.84"
  - Release: "2026/07/27: 🤗 Released kanana-2-3b, kanana-2-1.3b HF model weights." (via research subagent)
- **Kanana-2 licence, "kanana-open-license"** ([LICENSE](https://huggingface.co/kakaocorp/kanana-2-1.3b-instruct/blob/main/LICENSE); verified):
  - §4.1: "If you wish to engage in any of the following activities using Kanana Materials or any Derivative Works, you must obtain a separate commercial license expressly granted by KAKAO: … (iii) Offering or (re)selling to third parties Kanana Materials or any Derivative Works embedded in on-device domains."
  - §4.2: "you may use Kanana Materials or any Derivative Works for the development and operation of your own services without obtaining a commercial license from KAKAO."
- **Kanana 1.5 2.1B** ([card](https://huggingface.co/kakaocorp/kanana-1.5-2.1b-instruct-2505)):
  - Licence: "license: apache-2.0" (verified).
  - Columns MT-Bench | KoMT-Bench | IFEval | … | KMMLU (0-shot, CoT) | …: "Kanana-1.5-2.1B* | 7.01 | 6.54 | 68.61 | 68.90 | 65.08 | 81.43 | 60.62 | 53.87 | 32.93 | 53.70" (via research subagent).
  - Context: "up to 32K tokens length natively".
- **Kanana-Nano-2.1B** ([card](https://huggingface.co/kakaocorp/kanana-nano-2.1b-instruct); via research subagent):
  - Licence: "license: cc-by-nc-4.0".
  - Columns "MT-Bench | LogicKor | KoMT-Bench | WildBench | IFEval":
    - "Kanana-Nano-2.1b | 6.400 | 7.964 | 5.857 | 25.41 | 0.720"
    - "EXAONE-3.5-2.4b | 7.919 | 8.941 | 7.223 | 41.68 | 0.790"
- **Kakao's on-device positioning** ([press release](https://www.kakaocorp.com/page/detail/12089), 2026-07-28; via research subagent): "스마트폰 등과 같은 디바이스에서 구동할 수 있는 경량 언어모델(SLM) 4종을 오픈소스로 공개했다고 밝혔다".
  - Conflict: the release says the licence allows "상업적 활용까지", but §4.1(iii) requires a separate licence for on-device embedding offered to third parties.
- **No official GGUF, LiteRT or AI Hub builds** were found for Kanana.

**Naver HyperCLOVA X SEED** ([0.5B](https://huggingface.co/naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-0.5B), [1.5B](https://huggingface.co/naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-1.5B), [Vision 3B](https://huggingface.co/naver-hyperclovax/HyperCLOVAX-SEED-Vision-Instruct-3B))
- **0.5B** (via research subagent):
  - Specs: "Parameters: 0.57 B (total); 0.45 B (excluding token embeddings, tied embeddings)"; "Maximum Context Length: 4 K tokens"; "suitable for deployment in resource‑constrained environments such as edge devices".
  - Columns "KMMLU (5-shot, acc) | HAE-RAE (5-shot, acc) | CLiCK (5-shot, acc) | KoBEST (5-shot, acc)":
    - "| HyperCLOVAX-SEED-Text-Instruct-0.5B | 0.3815 | 0.5619 | 0.4446 | 0.6299 |"
    - "| QWEN2.5-0.5B-instruct | 0.2968 | 0.3428 | 0.3805 | 0.5025 |"
- **1.5B** (via research subagent): "HyperCLOVAX-SEED-Text-Instruct-1.5B | 0.3933 | 0.5674 | 0.4947 | 0.6490" vs "Qwen2.5-1.5B-instruct | 0.3696 | 0.5160 | 0.4772 | 0.5968" and "gemma-3-1b-it | 0.3075 | 0.3648 | 0.3724 | 0.5869". Context 16k.
- **Licence §4** ([LICENSE](https://huggingface.co/naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-0.5B/blob/main/LICENSE); verified): "If (i) as of the Model Release Date, the monthly active users of the products or services made available by or for Licensee, or Licensee's Affiliates, is greater than 10 million monthly active users in the preceding calendar month, or (ii) the Licensee or its Affiliate distributes or makes available any product or service, which is substantially similar to or directly competes with any product and service provided by NAVER, then the Licensee must request a license from NAVER."
- **No ≤4B SEED newer than April 2025.** Later releases are Think-14B, Think-32B and Omni-8B (via research subagent).

**Qwen3 / Qwen3.5 (Alibaba)**
- **Korean is explicitly covered.**
  - Qwen3 blog lists "Other Japanese, Korean, Georgian, Basque, …" ([qwenlm.github.io/blog/qwen3](https://qwenlm.github.io/blog/qwen3/); verified).
  - Tech report: "Qwen3 expands multilingual support from 29 to 119 languages and dialects" ([arXiv 2505.09388](https://arxiv.org/html/2505.09388v1); verified).
- **Official Korean scores** ("Table 30: Benchmark scores for language: Korean (ko)"; columns MLogiQA, INCLUDE, MMMLU, MT-AIME24, PolyMath, Average; verified):
  - Non-thinking mode: "Qwen3-4B 46.2 74.0 59.9 13.3 16.6 42.0", "Qwen3-1.7B 48.8 58.0 46.0 6.7 9.0 33.7", "Qwen3-0.6B 40.0 52.0 36.9 0.0 5.5 26.9".
  - Thinking mode: "Qwen3-4B 66.2 74.0 68.8 70.0 40.6 63.9".
  - Comparator (non-thinking): "GPT-4o-2024-1120 63.7 80.0 80.5 13.3 12.9 50.1".
- **Specs** (cards; via research subagent): Qwen3-4B "Number of Parameters: 4.0B", "Number of Paramaters (Non-Embedding): 3.6B"; licence "apache-2.0".
- **Qwen3.5 0.8B / 2B** (cards; via research subagent): "license: apache-2.0", "Causal Language Model with Vision Encoder", "Expanded support to 201 languages and dialects". Korean is not named.

**Google Gemma**
- **Gemma 4 E2B/E4B** ([card](https://huggingface.co/google/gemma-4-E2B-it); verified):
  - "license: apache-2.0" with "license_link: https://ai.google.dev/gemma/docs/gemma_4_license".
  - "| Total Parameters | 2.3B effective <br> (5.1B with embeddings) | 4.5B effective <br> (8B with embeddings) |"
  - "Multilingual – Out-of-the-box support for 35+ languages, pre-trained on 140+ languages."
  - Release per Google's releases page: "March 31, 2026" (via research subagent).
  - Multilingual benchmark: "| MMMLU | 88.4% | 86.3% | 83.4% | 76.6% | 67.4% | 70.7% |". Columns are 31B | 26B A4B | 12B | E4B | E2B | Gemma 3 27B (via research subagent).
- **Gemma 3** ([Google model card](https://ai.google.dev/gemma/docs/core/model_card_3); via research subagent): "Total input context of 128K tokens for the 4B, 12B, and 27B sizes, and 32K tokens for the 1B and 270M sizes."
  - Sources disagree on whether the 1B is multilingual. [Hugging Face's launch blog](https://github.com/huggingface/blog/blob/main/gemma3.md) says "English (1B) +140 languages (4B, 12B, 27B)"; Google's card says "The training dataset includes content in over 140 languages."
  - Gemma 3 and 3n use the [Gemma Terms of Use](https://ai.google.dev/gemma/terms).

**Meta Llama 3.2** ([model card](https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/MODEL_CARD.md); via research subagent)
- Languages: "English, German, French, Italian, Portuguese, Hindi, Spanish, and Thai are officially supported." Korean is not listed.
- Out of scope: "Use in languages beyond those explicitly referenced as supported in this model card."
- Licence: "If, on the Llama 3.2 version release date, the monthly active users … is greater than 700 million monthly active users in the preceding calendar month, you must request a license from Meta".

**Conflicting vendor numbers** (per research subagent)
- EXAONE 3.5 2.4B: KoMT-Bench and LogicKor are 7.24 and 8.51 on LG's card, but 7.223 and 8.941 in Kakao's table.
- Llama 3.2 3B: LG reports 3.16 and 2.86; Kakao reports 3.967 and 4.452.
- Kanana-Nano KoMT-Bench: 5.857 on its own card vs 5.90 on the Kanana 1.5 card.

### Inferences
- **The best published fit for Weave's task is Qwen3-1.7B or Qwen3-4B in non-thinking mode.** Weave's task is short Korean instruction following (split a question, then rewrite it with a clue). On that basis:
  - Licence is clean.
  - Korean is explicitly supported, with official Korean scores.
  - S25/S26 NPU latencies are measured (Q1, Q5).
  - LoRA fine-tuning is allowed.
  - Gemma 4 E2B is the strongest alternative: same Apache licence, fastest measured GPU path on the S26 Ultra, and the same family as Gemini Nano 4. However, it has no Korean-specific scores.
- **Korean-specialised small models score higher on Korean chat benchmarks but are hard to ship in a Samsung product as-is.**
  - Kakao's tables give these KoMT-Bench scores:
    - EXAONE 3.5 2.4B: 7.223 (Kanana-Nano card).
    - Kanana-2-1.3B: 6.54 (Kanana-2 card).
    - Qwen3-1.7B: 5.29 (Kanana-2 card).
  - The two Kakao tables may differ in judge and settings, so these rankings are indicative only.
  - EXAONE and Kanana-Nano are NC-licensed. Kanana-2's §4.1(iii) on-device clause would likely require a Kakao licence for any model embedded in devices offered to third parties.
  - Kanana 1.5 2.1B (Apache-2.0) is the only Korea-built ≤4B model with an unrestricted licence. It has no phone measurements, but its size class (~2B) puts it between Qwen3-1.7B and Gemma 4 E2B in the Q1 tables (inference).
- **Benchmark relevance.** KMMLU and HAE-RAE are knowledge benchmarks and say little about query rewriting. KoMT-Bench, LogicKor and IFEval are closer proxies. A Weave-specific Korean rewrite evaluation (or a small LoRA fine-tune) would be needed either way.
- **Tokenizer efficiency changes the effective prompt length.** Kanana-2 claims ">30%" better Korean tokenization than its previous generation, so the same ~500-token Korean prompt costs different prefill time per model. Prefill is the minor term (Q5).

### Gaps
- No same-harness, independent Korean benchmark covers all candidates; every Korean score above is vendor-reported.
- No public Korean query-decomposition or rewrite benchmark for ≤4B models was found.
- No phone measurements (AI Hub, LiteRT, ExecuTorch) exist for EXAONE, Kanana or HyperCLOVA X SEED.
- Korean is not named among Gemma 4's "35+" out-of-the-box languages or among Qwen3.5's "201 languages" (NOT FOUND). It is only implied by the 140+ pre-training languages and by Kakao's third-party Qwen3.5-2B scores.
- Whether Samsung's user scale triggers the SEED (10M MAU) or Llama (700M MAU) clauses was not assessed.

## Q5. Per-hop latency estimate (prefill ~500 tokens + decode ~25 tokens) and 2-hop total

### Takeaway
Using only the sourced throughputs above, these are the per-hop (and 2-hop) model compute times on Snapdragon Galaxy S25/S26, using the best measured stack for each model:
- **0.6–2B models: ≈0.4–0.8 s per hop (≈0.7–1.6 s for 2 hops).** This covers Qwen3-0.6B/1.7B on the QAIRT NPU, Llama-3.2-1B on the Genie NPU, and Gemma 4 E2B on the LiteRT-LM GPU (0.61 s).
- **2–4B models on other stacks: ≈1.0–1.9 s per hop.** Examples: Qwen3-4B on the QAIRT NPU at 1.41–1.48 s, Llama-3.2-3B on Genie at 1.53–1.63 s, and Gemma 4 E4B on the llama.cpp NPU at up to 1.87 s.
- **CPU-only paths:**
  - On 2025–26 Galaxy phones: 1.4 s (Gemma 4 E2B, S26 Ultra) to 4.0 s (Gemma 4 E4B).
  - On 2024 hardware with ExecuTorch: 2.4–6.8 s.
- **Gemini Nano:** at Google's only published rate (Pixel 9 Pro, nano-v2), one hop is ≈3.25 s.
- **Exynos 2600 units:** no sourced number.

### Cited Findings
- **Formula:** per hop = 500 / prefill (tok/s) + 25 / decode (tok/s); 2 hops = 2 × per hop. Every input number is quoted in Q1, with the source and conditions listed there.
- **Galaxy S26 (Snapdragon 8 Elite Gen 5 for Galaxy)**, Qualcomm AI Hub NPU, 4-bit:

| Model / runtime / ctx | Prefill | Decode | 500/prefill | 25/decode | Per hop | 2 hops |
|---|---|---|---|---|---|---|
| Qwen3-0.6B W4A16 GenieX-QAIRT 1024 | 5985.6 | 88.8 | 0.084 s | 0.282 s | **0.37 s** | 0.73 s |
| Qwen3-1.7B W4A16 GenieX-QAIRT 1024 | 3288.5 | 42.4 | 0.152 s | 0.590 s | **0.74 s** | 1.48 s |
| Qwen3-4B W4A16 GenieX-QAIRT 1024 | 1768.6 | 21.8 | 0.283 s | 1.147 s | **1.43 s** | 2.86 s |
| Qwen3-4B-Instruct-2507 W4A16 GenieX-QAIRT 1024 | 1764.2 | 20.9 | 0.283 s | 1.196 s | **1.48 s** | 2.96 s |
| Llama-3.2-1B W4A16 Genie 4096 | 1626.0 | 65.2 | 0.308 s | 0.383 s | **0.69 s** | 1.38 s |
| Llama-3.2-3B W4A16 Genie 4096 | 775.8 | 28.2 | 0.644 s | 0.887 s | **1.53 s** | 3.06 s |
| Llama-3.2-3B-SSD W4A16 Genie 4096 | 970.9 | 55.2 | 0.515 s | 0.453 s | **0.97 s** | 1.94 s |
| Gemma-4-E2B Q4_0 llama.cpp-NPU 512 | 1894.4 | 33.7 | 0.264 s | 0.742 s | **1.01 s** | 2.01 s |
| Gemma-4-E4B Q4_0 llama.cpp-NPU 512 | 1115.8 | 17.6 | 0.448 s | 1.420 s | **1.87 s** | 3.74 s |
| Qwen3.5-0.8B Q4_0 llama.cpp-NPU 512 | 1170.5 | 45.7 | 0.427 s | 0.547 s | **0.97 s** | 1.95 s |
| Qwen3.5-2B Q4_0 llama.cpp-NPU 512 | 909.7 | 30.4 | 0.550 s | 0.822 s | **1.37 s** | 2.74 s |

- **Galaxy S26 Ultra**, Google LiteRT-LM:

| Model / backend | Prefill | Decode | 500/prefill | 25/decode | Per hop | 2 hops |
|---|---|---|---|---|---|---|
| Gemma 4 E2B GPU | 3808 | 52.1 | 0.131 s | 0.480 s | **0.61 s** | 1.22 s |
| Gemma 4 E2B GPU + MTP ("Rewrite tone" decode) | 3808 | 87.4 | 0.131 s | 0.286 s | **0.42 s** | 0.83 s |
| Gemma 4 E2B CPU | 557 | 46.9 | 0.898 s | 0.533 s | **1.43 s** | 2.86 s |
| Gemma 4 E4B GPU | 1293 | 22.1 | 0.387 s | 1.131 s | **1.52 s** | 3.04 s |
| Gemma 4 E4B CPU | 195 | 17.7 | 2.564 s | 1.412 s | **3.98 s** | 7.95 s |
| Qwen3-0.6B dyn-INT4 GPU (Galaxy S26, community) | 3442 | 81.4 | 0.145 s | 0.307 s | **0.45 s** | 0.90 s |

- **Galaxy S25 (Snapdragon 8 Elite for Galaxy)**, AI Hub NPU. These rows are shared with "Dragonwing Q-8750"; see Q1 caveat.

| Model / runtime / ctx | Prefill | Decode | 500/prefill | 25/decode | Per hop | 2 hops |
|---|---|---|---|---|---|---|
| Qwen3-0.6B W4A16 GenieX-QAIRT 1024 | 5230.1 | 79.9 | 0.096 s | 0.313 s | **0.41 s** | 0.82 s |
| Qwen3-1.7B W4A16 GenieX-QAIRT 1024 | 3000.9 | 39.8 | 0.167 s | 0.628 s | **0.79 s** | 1.59 s |
| Qwen3-4B W4A16 GenieX-QAIRT 1024 | 1754.9 | 22.3 | 0.285 s | 1.121 s | **1.41 s** | 2.81 s |
| Llama-3.2-1B W4A16 Genie 4096 | 1782.5 | 67.2 | 0.281 s | 0.372 s | **0.65 s** | 1.31 s |
| Llama-3.2-3B W4A16 Genie 4096 | 727.8 | 26.5 | 0.687 s | 0.943 s | **1.63 s** | 3.26 s |
| Gemma-4-E2B Q4_0 llama.cpp-NPU 512 | 1686.1 | 28.9 | 0.297 s | 0.865 s | **1.16 s** | 2.32 s |

- **S25 Ultra / S24 Ultra**, LiteRT (Google):
  - Qwen2.5-1.5B int8 GPU (S25 Ultra): 500/1667.75 = 0.300 s + 25/30.88 = 0.810 s = **1.11 s**/hop, 2.22 s for 2 hops.
  - Gemma3-1B GPU (S24 Ultra): 500/1191 = 0.420 + 25/24 = 1.042 → **1.46 s** (2.92 s).
  - Gemma3-1B CPU (S24 Ultra): 500/177 = 2.825 + 25/33 = 0.758 → **3.58 s** (7.16 s).
- **CPU-only ExecuTorch** (OnePlus 12, Snapdragon 8 Gen 3, 2024):
  - Llama-3.2-1B SpinQuant: 500/260.5 = 1.919 + 25/50.2 = 0.498 → **2.42 s** (4.83 s).
  - Llama-3.2-3B SpinQuant: 500/89.7 = 5.574 + 25/19.7 = 1.269 → **6.84 s** (13.69 s).
- **Gemini Nano nano-v2, Pixel 9 Pro** (the only published Gemini Nano decode rate): 500/510 = 0.980 s + 25/11 = 2.273 s → **3.25 s**/hop (6.51 s for 2 hops).
  - Nano-v3 on the Pixel 10 Pro lists only prefix speed: 500/940 = 0.532 s. Its decode cost cannot be sourced.
- **References from other platforms:**
  - Apple ~3B AFM, iPhone 15 Pro, 2024: 500 × 0.6 ms = 0.300 s + 25/30 = 0.833 s → **1.13 s** (2.27 s).
  - Gemma 4 E2B GPU, iPhone 17 Pro: 500/2878 = 0.174 + 25/56.5 = 0.442 → **0.62 s** (1.23 s).
  - Gemma 3n E2B NPU, Dimensity 9500: 500/1600 = 0.312 + 25/28 = 0.893 → **1.21 s** (2.41 s; upper bound, since the prefill claim is ">1600").
- **Cross-check against AI Hub's TTFT definition.** For the Genie (ctx 4096) rows, the TTFT lower bound is "up to 128 tokens, i.e., one iteration of the prompt processor", and the upper/lower ratio is exactly 32 (= 4096/128). Examples: 2463.36/76.98 for Llama-3.2-3B on the S25, 2081.44/65.045 for Qwen3-4B on the S25.
  - So a 500-token prompt (4 iterations) would take about 4 × TTFT_min. That gives 4 × 76.98 ms = 0.308 s for Llama-3.2-3B, less than the 0.687 s from the separate `prefill_tokens_per_second` (727.8).
  - With that TTFT-based prefill, Llama-3.2-3B on the S25 becomes 0.308 + 0.943 = **1.25 s**/hop (2.50 s). Qwen3-4B Genie on the S25 becomes 4 × 0.065 + 25/26.1 = 0.260 + 0.958 = **1.22 s** (2.44 s).
  - For the GenieX rows, prefill_tokens_per_second equals ctx / TTFT_max (e.g., 1024 / 0.5835 s = 1754.9), so both methods agree.

### Inferences
- **Feasibility answer: yes, with caveats.** With the best measured stack, a 0.6–2B 4-bit model on the S25/S26 NPU or GPU adds about 0.4–0.8 s per hop (about 0.7–1.6 s for a 2-hop question). Other stacks for 2B-class models give 1.0–1.4 s (llama.cpp NPU), so stack choice matters as much as model size. A 4B model adds about 1.4–1.5 s per hop on the QAIRT NPU (about 2.8–3.0 s for 2 hops). This is model compute only, excluding:
  - model load or warm-up (cold start can be seconds);
  - tokenization and chat-template overhead;
  - the embedding retrieval itself;
  - any BUSY/quota retries (Gemini Nano).
- **Decode share.** Decode is about 75–80% of the per-hop time for Qwen3 1.7–4B on the NPU. The biggest gains therefore come from:
  - fewer output tokens: emit only the rewritten sub-question, about 10–15 tokens, with no preamble;
  - speculative decoding (SSD, MTP);
  - a smaller model;
  - not from a faster prefill.
  At 10 output tokens, Qwen3-4B QAIRT on the S26 drops to 0.283 + 10/21.8 = 0.742 s/hop.
- **Qwen3 must run with thinking off.** The decode figures assume 25 generated tokens. AI Hub measures response rate "with thinking", and LiteRT's Qwen3 configuration notes "thinking is on unless `enable_thinking` is false" ([Qwen3-0.6B card](https://huggingface.co/litert-community/Qwen3-0.6B)). A thinking-mode reply would multiply output length and latency.
- **Korean token counts differ by tokenizer.** The "500 tokens" input can be noticeably more or fewer tokens depending on the model, which shifts prefill time linearly. Prefill is the smaller term here, so the effect on totals is modest. The only tokenizer-efficiency claim found is Kakao's ">30%" Korean improvement for Kanana-2 over its previous generation (Q4). No cross-model Korean token-count comparison was found.
- **Bounds on the estimate.**
  - The NPU numbers are best-case vendor measurements with warmed caches.
  - The community measurement on the Galaxy S26 shows the CPU dropping from 365 to about 231 tok/s prefill after the first run, so CPU-path estimates should be treated as optimistic.
  - If the NPU executor is not kept initialised between hops, add about 0.54 s per call. This is the Snapdragon 8 Elite executor-init cost measured with FastVLM in arXiv 2606.27906.
  - Sustained-load results after repeated long generations (2603.23640) vary:
    - About 15% loss on the S24 Ultra, per the body text.
    - "nearly half" on the iPhone 16 Pro, per the abstract.
    - The abstract also says the S24 Ultra stopped entirely.
    Weave's short calls should mostly stay out of that regime (inference).
- **Exynos units.** All Galaxy rows above are Snapdragon units. For Exynos 2600 Galaxy S26/S26+ units there is no sourced number. Only the LiteRT-LM GPU/CPU path (or LiteRT's Samsung NPU path, UNVERIFIED) would run there, at unknown speed.

### Gaps
- No sourced per-hop numbers for Exynos 2600 S26 units, or for Gemini Nano on any Galaxy.
- No measurement matches the exact 500/25 shape. Each source uses its own prompt length, so the per-hop values are linear estimates from rate figures:
  - AI Hub: 128-token chunks.
  - LiteRT-LM: 1024 + 256 tokens.
  - ExecuTorch: 64-token prompt.
  - Qwen3-0.6B community card: 256/256 or 1024/256 tokens.
