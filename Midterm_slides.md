# Midterm Slides Draft: Team 4A, Picture Perfect Crimes

> [!summary]
> Follows the original 8-slide template: title plus 7 content slides. For a 5-minute talk that's about 40 seconds per content slide. Every slide keeps the footer **"Team 4A Picture Perfect Crimes: Etai, Nolan, Michael, and Jason"**. The rubric section each slide covers is in brackets.
> **Project plan:** (1) reproduce the jailbreak image and find the smallest change that still works, (2) build our own jailbreak images on today's open models, (3) test those images on closed models (ChatGPT, Gemini, Claude).
> Figures are in `project/results/`. The script that made them is `project/scripts/measure_perturbation.py`.

---

## Slide 1: Title (keep as is)

- Adversarial Attacks on Multi-modal Language Models
- Team 4A: Picture Perfect Crimes
- Etai, Nolan, Michael, and Jason
- Computer System Security, Fall 2026, Mid-term Presentation

---

## Slide 2: High-Level Problem Area [1 pt]

**On the slide:**
- Multimodal LLMs (MLLMs) accept images and audio, not just text. Each new input is a new attack surface.
- Safety training is done mostly on text, so the image channel is weakly protected.
- Pixels are continuous, so attackers can use gradients to craft small changes that steer the model.
- **Key problem:** can a crafted image push a safety-trained model into answering harmful requests, and do today's models still fall for it?

**Speaker notes:**
Text is discrete, so you can't change a word by 1% and attacking with text is slow trial and error. Pixels are numbers, so we can nudge each one along the gradient toward a harmful answer. Qi et al. (AAAI 2024) showed one such image jailbreaks aligned models across many prompts.

---

## Slide 3: Project Topic and Proposed Solution [1.5 pts]

**On the slide:**
- **Topic:** build visual jailbreak images and test how far they reach, from 2023 open models to today's closed models
- **Approach, in three stages:**
  1. **Reproduce + trade-off:** recreate Qi et al.'s jailbreak image and find the **smallest perturbation that still jailbreaks** (ε = 64 → 32 → 16 → 8)
  2. **Our own images on today's open models:** run the attack on newer open models (Qwen2.5-VL, Llama 3.2 Vision, LLaVA-1.5) and see how far we get
  3. **Closed models:** take our best images and test whether they transfer to ChatGPT, Gemini and Claude
- **Why this order:** the gradient attack needs model weights, so images have to be built on open models first. Closed models can only be reached by transfer.

Optional figure: a pipeline diagram (open model → craft image → test on closed models).

**Speaker notes:**
Each stage moves closer to real-world systems. Stage 1 checks the attack works and how subtle it can be. Stage 2 checks whether newer safety training stops it. Stage 3 is the realistic threat: an attacker without access to the model's internals.

---

## Slide 4: Project Goals [1 pt, with slide 5]

**On the slide:**
1. **Reproduce** Qi et al.'s jailbreak image and characterize it
2. **Trade-off:** find the smallest change (ε) that still jailbreaks, and how visible it is
3. **Today's open models:** generate our own jailbreak images and measure how often they work
4. **Closed models:** measure whether those images transfer to ChatGPT, Gemini and Claude

**Measured by:**
- **Attack success rate (ASR):** share of harmful prompts answered instead of refused
- **PSNR / SSIM:** how different the attack image is from the original

**Speaker notes:**
Goals 1 and 2 build the baseline. Goals 3 and 4 are the new part. Goal 1 is underway (slide 6). The rest are the second half of the quarter.

---

## Slide 5: Timeline + Deliverables (and Current Progress)

**On the slide:**

| Week | Task | Owner | Status |
|---|---|---|---|
| 5–6 | Literature review, get Qi et al. code + attack images | Etai, Nolan | ✅ Done |
| 7 | Measurement script (PSNR/SSIM) on Qi's images | Michael, Etai | ✅ Done |
| 7–8 | GPU setup: LLaVA-1.5-7B on Colab | Jason | ✅ Notebook built |
| 8 | Test Qi's images on LLaVA (40 prompts) | Jason, Nolan | ✅ Done |
| 8–9 | Find the smallest ε that works (needs our own images) | Nolan, Jason | ⏳ Next |
| 9 | Generate our own jailbreak images on newer open models | Nolan, Jason | ⏳ Next |
| 9–10 | Test our images on ChatGPT, Gemini, Claude; collect results | Michael, Etai | ⏳ Next |
| 10 (11/30) | Final presentation | All | ⏳ |
| 11 | Final report | All | ⏳ |

**Speaker notes:**
We're about a week behind our intro plan. The main reason is hardware (slide 8). We adjusted by moving to smaller models on Colab: the free T4 GPU for testing, and about $10 of L4 GPU time for building our own images.

---

## Slide 6: Results / Explorations (+ Demo) [1.5 pts]

**On the slide:**
- Figure: `results/slide_clean_vs_adv.png` (clean | adversarial ε = 16/255 | amplified noise)
- Table (from `results/perturbation_metrics.csv`):

| Image | Max pixel change | PSNR (dB) | SSIM |
|---|---|---|---|
| ε = 16/255 | 18 | 28.1 | 0.58 |
| ε = 32/255 | 34 | 21.9 | 0.31 |
| ε = 64/255 | 66 | 16.2 | 0.14 |
| Unconstrained | 252 | 7.3 | 0.01 |

- **Findings so far:**
  - The noise touches **over 92% of pixels**, even at the smallest budget. It's spread everywhere, not a small patch.
  - At ε = 16 the texture is faintly visible (SSIM 0.58), so finding the smallest working ε matters.
  - Next: find whether ε = 8 still jailbreaks.

**Demo (optional, ~30 s):** show `results/side_by_side.png`, which has all four budgets plus their amplified noise. Or open the Colab notebook to show the pipeline.

**Speaker notes:**
PSNR measures how much the pixels changed: higher is less visible, and roughly 30 dB or more is hard to notice. SSIM measures whether the image structure is preserved: 1.0 means identical. Max pixel change confirms the attack stayed within its budget. Our measured 18 vs. 16 is ±2 from resizing the clean image.

- **LLaVA transfer test (40 prompts, keyword check):** not refused 57.5% with the clean image vs. 52.5–62.5% with the attack images. No clear transfer, and the clean baseline is already high.

---

## Slide 7: Comparisons with Related Work

**On the slide:**

| | Qi et al. [1] | Schaeffer et al. [2] | M-Attack [3] | **Ours** |
|---|---|---|---|---|
| Models | MiniGPT-4, InstructBLIP, LLaVA (13B, 2023) | 40+ open VLMs | GPT-4o, Gemini, Claude | LLaVA → newer open VLMs → closed models |
| Access | White-box | White-box → transfer | Black-box transfer | White-box → transfer |
| Goal | Jailbreak | Jailbreak | Misdescribe image | Jailbreak + smallest working ε |
| Compute | 80 GB A100 | Large cluster | — | Colab: free T4, paid L4 (~$10) |
| Finding | One image jailbreaks many prompts | Jailbreaks rarely transfer | >90% transfer for targeted descriptions | No transfer to LLaVA so far |

- **What we add:**
  - Jailbreak tests on today's open models
  - The smallest perturbation that still works
  - A direct transfer test on current closed models

**Speaker notes:**
Qi et al. showed the attack works. Schaeffer et al. found jailbreak images mostly don't transfer between models, but M-Attack shows a related kind of attack *does* reach commercial models. Our stage 3 tests that gap directly.

Footer: [1] Qi et al., AAAI 2024 · [2] Schaeffer et al., ICLR 2025 · [3] M-Attack, NeurIPS 2025

---

## Slide 8: Next Steps + Risks / Backup Plans

**On the slide:**

Next steps:
- Finish testing Qi's images on LLaVA and find the smallest working ε
- Run the attack ourselves on newer open models (Qwen2.5-VL, Llama 3.2 Vision) at ε = 8, 16, 32
- Take the best images to ChatGPT, Gemini and Claude, and record refusal vs. compliance

| Risk | Backup |
|---|---|
| Original code needs an 80 GB GPU | 7B models on Colab: free T4 (15 GB) for testing, L4 (24 GB, about $10 total) for building images; A100 only if the L4 runs out of memory |
| Newer open models resist the attack | Report how far we got (ASR per ε); try larger ε or more optimization steps |
| Images don't transfer to closed models | Still a valid result (agrees with Schaeffer et al.); try an ensemble of open models as the source |
| Closed-model terms of service | Small number of benign-category test prompts; check with Kaiyuan first |
| Keyword refusal check is noisy | Hand-label a sample of outputs |

**Speaker notes:**
End with the one-sentence summary: "Adding vision created a backdoor around safety training. We're testing how small that backdoor can get, and whether it still reaches today's models."

---

## Changes from the previous draft
- Removed defenses from the plan.
- The plan is now three stages: reproduce + find the smallest working ε → our own images on today's open models → transfer to closed models.
- Goals, timeline, related work and risks are updated to match.
