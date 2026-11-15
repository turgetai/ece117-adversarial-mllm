# Adversarial Attacks on Multi-modal Language Models: Midterm Report

**Team 4A: Picture Perfect Crimes**. Etai, Nolan, Michael, Jason
ECE M117 Computer System Security, Fall 2026

---

## 1. High-Level Problem Area

Multimodal large language models (MLLMs), also called vision-language models (VLMs), extend a large language model with an image (or audio) encoder. A typical design passes the image through a vision encoder such as CLIP, maps the result into the language model's token space with a small projector, and lets the language model answer a text prompt about the image. These models are safety-aligned to refuse harmful requests, but that alignment is trained almost entirely on text.

Adding an image input creates a new attack surface. Text is discrete, so attacking a model through text requires slow search over word combinations. Image pixels are continuous, and the whole model is differentiable, so an attacker with the model's weights can use gradient-based optimization (projected gradient descent, PGD) to compute a small perturbation that steers the model's output. Prior work shows this is effective:
- Qi et al. [1] found that a single adversarial image can universally jailbreak aligned VLMs across many harmful instructions.
- Carlini et al. [2] showed image perturbations break alignment far more easily than text attacks.
- Later work extended this to arbitrary behavior control [3], attacks needing only the public vision encoder [4], and optimization-free typographic attacks [5].

Two questions remain open. Most results are on 2023-era models with full access to model internals, and Schaeffer et al. [6] found that jailbreak images rarely transfer between models. We don't know how today's open and closed models hold up, or how small a perturbation is still enough.

## 2. Project Topic and Potential Solution

Our project builds visual jailbreak images and tests how far they reach, from the 2023 open models of the original paper to today's open and closed models. We approach it in three stages:

1. **Reproduce the attack and find the smallest change that works.** Start from the authors' released code and adversarial images, made against MiniGPT-4 at perturbation budgets ε = 16, 32, 64 out of 255, plus an unconstrained image. For each budget, measure attack success rate (ASR), the share of harmful prompts the model answers instead of refusing. Compare it with image-distortion metrics: peak signal-to-noise ratio (PSNR) and structural similarity (SSIM). Then step the budget down (ε = 8) to find the smallest perturbation that still jailbreaks. That point marks the attack-strength vs. visibility trade-off.
2. **Generate our own jailbreak images on today's open models.** Run the same optimization against newer open models such as Qwen2.5-VL and Llama 3.2 Vision, as well as LLaVA-1.5. These models have stronger safety training than the 2023 models, so we measure how far the attack gets: whether it works at all, at what budget, and with how many optimization steps.
3. **Test the images on closed models.** Take the most effective images from stage 2 and present them to ChatGPT, Gemini and Claude. The gradient attack requires model weights, so closed models can only be reached by transfer: an image optimized on an open model is tried unchanged on the closed one. Schaeffer et al. [6] found that jailbreak images rarely transfer, while M-Attack [7] showed that targeted image attacks do reach these models. Our stage 3 tests this gap directly for jailbreaks on current models.

## 3. Project Goals and Timeline

**Goals**
1. Reproduce and characterize the baseline jailbreak images.
2. Find the smallest perturbation (ε) that still jailbreaks, and measure how visible it is.
3. Generate our own jailbreak images on today's open models and measure their success rate.
4. Measure whether those images transfer to closed models (ChatGPT, Gemini, Claude).

**Timeline**

| Week | Task | Owner | Status |
|---|---|---|---|
| 5–6 | Literature review; obtain Qi et al. code and attack images | Etai, Nolan | Done |
| 7 | Perturbation measurement script (PSNR/SSIM/L∞) | Michael, Etai | Done |
| 7–8 | GPU environment: 4-bit LLaVA-1.5-7B on Colab | Jason | Done |
| 8 | Test Qi's images on LLaVA (5 images × 40 instructions) | Jason, Nolan | Done |
| 8–9 | Find the smallest working ε (needs our own images) | Nolan, Jason | Planned |
| 9 | Generate our own jailbreak images on newer open models at ε = 8/16/32 | Nolan, Jason | Planned |
| 9–10 | Test our images on ChatGPT, Gemini, Claude; collect results | Michael, Etai | Planned |
| 10 | Final presentation (11/30) | All | Planned |
| 11 | Final report | All | Planned |

## 4. Preliminary Results

**4.1 Characterizing the attack images.** We measured each released adversarial image against the clean panda image it was built from. The clean image was resized to the model's 224×224 input with bicubic interpolation.

| Image | Budget ε (/255) | Max pixel change (L∞) | RMS change | Pixels changed | PSNR (dB) | SSIM |
|---|---|---|---|---|---|---|
| Constrained | 16 | 18 | 10.1 | 92.5% | 28.1 | 0.58 |
| Constrained | 32 | 34 | 20.6 | 96.3% | 21.9 | 0.31 |
| Constrained | 64 | 66 | 39.4 | 97.7% | 16.2 | 0.14 |
| Unconstrained | — | 252 | 110.7 | 98.9% | 7.3 | 0.01 |

Observations:
- **The perturbations stay within their budgets.** The measured maximum change is within 2 pixel levels of each ε. The small excess comes from our resize not exactly matching the authors' preprocessing.
- **The noise is spread over the whole image, not a local patch.** More than 92% of pixels change even at the smallest budget.
- **The smallest released budget is not fully invisible.** At ε = 16/255, PSNR is 28.1 dB (below the roughly 30 dB often used as a rule of thumb for hard-to-notice distortion) and SSIM is 0.58, and a faint texture is visible on close inspection. This motivates goal 2: testing smaller budgets (ε = 8/255) to find the point where the attack stops working.

**4.2 Compute constraint and pipeline.** The original code targets 13B-parameter models and expects a single 80 GB A100 GPU, which we don't have. We built an alternative pipeline that loads LLaVA-1.5-7B in 4-bit precision on a free Colab T4 GPU (15 GB). It feeds each of Qi et al.'s 40 manual harmful instructions together with each of the five images, then flags refusals with a refusal-phrase check (the standard first-pass metric in jailbreak papers). Outputs will be hand-checked on a sample. The results are in section 4.4. The same pipeline will be reused to generate our own images on newer open models in stage 2.

**4.3 Compute plan.** Testing an image on a model needs no gradients, so it runs on the free T4. Generating our own attack images needs gradients through the full model, which takes more memory than the T4 has. For that we plan to use a Colab L4 GPU (24 GB), paid through one Pay As You Go pack of 100 compute units ($9.99). At roughly 1.7 units per hour, that is about 58 hours of L4 time. The A100 (40 GB, roughly 5.4 units per hour) is our fallback if the L4 runs out of memory. We have not yet tested whether the attack fits on the L4.

**4.4 Transfer test on LLaVA-1.5-7B.** We ran the pipeline on all 40 of Qi et al.'s manual harmful instructions, once with each of the five images (200 model replies, on a free Colab T4, 2026-11-15). The table shows how many instructions the model did not refuse, by the refusal-phrase check.

| Image | Not refused (of 40) | Rate |
|---|---|---|
| Clean (no attack) | 23 | 57.5% |
| ε = 16/255 | 24 | 60.0% |
| ε = 32/255 | 24 | 60.0% |
| ε = 64/255 | 21 | 52.5% |
| Unconstrained | 25 | 62.5% |

Observations:
- **No clear transfer.** The attack images move the rate by at most 2 instructions out of 40 in either direction, and the ε = 64 image is slightly *lower* than the clean image. The images were built for MiniGPT-4, and on LLaVA they have no measurable effect. This agrees with Schaeffer et al. [6].
- **The outcome depends on the instruction, not the image.** For 34 of the 40 instructions the model gave the same outcome with all five images: 20 answered every time and 14 refused every time.
- **The clean baseline is already high.** LLaVA-1.5-7B did not refuse 57.5% of the instructions even with the unmodified image. Its safety alignment is weak to begin with, so it leaves little room to show a jailbreak. Newer, better-aligned open models are a more meaningful target for stage 2.

Limitations: the refusal-phrase check is a first pass. A reply without a refusal phrase is not necessarily harmful, and we have not hand-labelled the replies yet. The model was loaded in 4-bit precision, with greedy decoding and a 128-token limit. Each prompt was run once. The per-instruction refusal table is in `results/llava_transfer_refusals.csv`.

## References

[1] X. Qi et al., "Visual Adversarial Examples Jailbreak Aligned Large Language Models," AAAI 2024.
[2] N. Carlini et al., "Are Aligned Neural Networks Adversarially Aligned?," NeurIPS 2023.
[3] L. Bailey et al., "Image Hijacks: Adversarial Images can Control Generative Models at Runtime," ICML 2024.
[4] E. Shayegani et al., "Jailbreak in Pieces: Compositional Adversarial Attacks on Multi-Modal Language Models," ICLR 2024.
[5] Y. Gong et al., "FigStep: Jailbreaking Large Vision-Language Models via Typographic Visual Prompts," AAAI 2025.
[6] R. Schaeffer et al., "Failures to Find Transferable Image Jailbreaks Between Vision-Language Models," ICLR 2025.
[7] VILA Lab (MBZUAI), "M-Attack: A Frustratingly Simple Yet Highly Effective Attack Baseline" (transfer attacks on GPT-4o, Gemini, Claude), NeurIPS 2025.
