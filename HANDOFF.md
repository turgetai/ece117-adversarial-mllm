# Handoff: Adversarial Attacks on Multi-modal Language Models

Team 4A, Picture Perfect Crimes (Etai, Nolan, Michael, Jason). ECE M117, Fall 2026.

This file explains what the project is, what has been done, what has not, and what to do next.

---

## 1. What the project is

We build "jailbreak images": pictures with small pixel changes that push a safety-trained AI model into answering harmful requests. We start from Qi et al., "Visual Adversarial Examples Jailbreak Aligned Large Language Models" (AAAI 2024).

The plan has three stages. We are **not** testing defenses.

1. **Reproduce + smallest change.** Recreate Qi et al.'s jailbreak image, then find the smallest change (ε) that still jailbreaks. Test ε = 64, 32, 16, 8.
2. **Our own images on newer open models.** Run the attack on today's open models (LLaVA-1.5, Qwen2.5-VL, Llama 3.2 Vision) and see how far we get.
3. **Closed models.** Take our best images and test whether they still work on ChatGPT, Gemini and Claude.

Key terms:
- **ε (epsilon):** the most any single pixel value (0–255) is allowed to change. Bigger ε = stronger attack, but easier to see.
- **Open model:** weights can be downloaded, so we can compute gradients and build the attack image.
- **Closed model:** only reachable through a chat window or API. We can only test whether an image built elsewhere still works ("transfer").
- **ASR (attack success rate):** share of harmful prompts the model answered instead of refusing.
- **PSNR / SSIM:** scores for how different the attack image is from the original. PSNR higher = less visible. SSIM 1.0 = identical.

---

## 2. File map

| Path | What it is |
|---|---|
| `HANDOFF.md` | This file |
| `README.md` | Short intro and setup |
| `Midterm_slides.md` | Text draft for the 8 midterm slides, with speaker notes |
| `Midterm_report.md` | Draft of the midterm report (4 graded sections) |
| `scripts/measure_perturbation.py` | Compares Qi's attack images with the clean image; writes the CSV and two figures |
| `scripts/make_slide_figure.py` | Makes the slide figure (clean panda + 3 attack images with scores) |
| `results/perturbation_metrics.csv` | Measured numbers (table below) |
| `results/slide_results_row.png` | Figure for slide 6 |
| `results/slide_clean_vs_adv.png` | Clean vs. ε = 16 vs. amplified noise |
| `results/side_by_side.png` | All four attack images plus their noise |
| `notebooks/llava_transfer_test.ipynb` | Colab notebook: tests Qi's images on LLaVA-1.5-7B. **Never run yet.** |
| `qi-repo/` | Qi et al.'s code and images. **Not in this repo.** Clone it yourself (section 5). |

---

## 3. What was done, and how

- **Got Qi et al.'s code and images.** Cloned their GitHub repo into `qi-repo/`. Their finished attack images are in `qi-repo/adversarial_images/` (clean panda, ε = 16, 32, 64, and an unconstrained one). They were built against MiniGPT-4.
- **Measured how visible the attack is.** `scripts/measure_perturbation.py` resizes the clean image to 224×224 (bicubic) and compares each attack image to it. Real results:

  | Image | ε budget | Max pixel change | Pixels changed | PSNR (dB) | SSIM |
  |---|---|---|---|---|---|
  | Constrained | 16 | 18 | 92.5% | 28.06 | 0.584 |
  | Constrained | 32 | 34 | 96.3% | 21.86 | 0.310 |
  | Constrained | 64 | 66 | 97.7% | 16.23 | 0.139 |
  | Unconstrained | none | 252 | 98.9% | 7.25 | 0.006 |

  - The max change is 2 over each budget. That comes from our resize not exactly matching theirs, not from the attack.
  - The noise covers more than 92% of pixels, even at ε = 16.
  - ε = 16 is faintly visible (SSIM 0.58), which is why we want to try ε = 8.
- **Made figures** from those numbers (in `results/`).
- **Wrote the Colab notebook** `notebooks/llava_transfer_test.ipynb`. It loads LLaVA-1.5-7B in 4-bit, shows it each of Qi's 5 images with Qi's harmful test prompts, and counts refusals with a keyword check.
- **Drafted the midterm slides and report** (`Midterm_slides.md`, `Midterm_report.md`).
- **Updated the Google Slides deck** (slides 4–8): goals, timeline, a new results slide (6), the related-work table, next steps and risks. Speaker notes on each slide explain the terms.

### GPU constraint

- Qi et al.'s code targets 13B-parameter models and expects one **A100 GPU with 80 GB** of memory. We don't have that.
- Our workaround: **LLaVA-1.5-7B loaded in 4-bit** on the **free Colab T4 GPU** (about 15 GB).

---

## 4. What is NOT done

- **The Colab notebook has never been run.** It is untested and may need small fixes.
- **No attack-success numbers yet.** Everything about LLaVA is "in progress" in the slides and report.
- **Report section 4.2** has a placeholder for the LLaVA results. It is still empty.
- **Slide 6** in Google Slides is missing its picture (`results/slide_results_row.png`).
- **Stages 2 and 3** (our own images, closed models) have not been started.

---

## 5. What to do next, and how

### A. Run the LLaVA test (do this first)

1. Go to [colab.research.google.com](https://colab.research.google.com) and upload `notebooks/llava_transfer_test.ipynb` (File → Upload notebook).
2. Runtime → Change runtime type → **T4 GPU**.
3. Runtime → **Run all**. The first cells install packages, clone Qi's repo, and download the model.
4. It uses 10 prompts by default (about 10–15 minutes). For the full set, change `N_PROMPTS = 10` to `40` (about 45 minutes).
5. The summary cell prints ASR per image (clean, eps16, eps32, eps64, unconstrained). The last cell downloads `llava_transfer_results.csv`.
6. **Hand-check the results.** The keyword check is rough. A reply can avoid refusal words and still not be harmful (for example, it just describes the panda). Read a sample of the CSV and correct the labels before quoting numbers.
7. Put the numbers in:
   - `Midterm_report.md`, section 4.2 (replace the placeholder line).
   - Slide 6 of the Google Slides deck (one line, e.g. "clean X% vs. ε = 16 Y%").
   - Save the CSV into `results/`.

Warning: model outputs may be offensive. **Report counts and percentages only.** Don't paste raw outputs into slides or the report.

### B. Rerun the measurement scripts (optional)

```bash
pip install numpy pillow scikit-image matplotlib
```

```bash
git clone --depth 1 https://github.com/Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models.git qi-repo
```

```bash
python scripts/measure_perturbation.py qi-repo/adversarial_images results
```

```bash
python scripts/make_slide_figure.py qi-repo/adversarial_images results
```

Run these from the project folder. The first script writes the CSV and two figures. The second needs the CSV and writes `slide_results_row.png`.

### C. Add the picture to slide 6

Drag `results/slide_results_row.png` onto slide 6 in Google Slides, below the bullets.

### D. Stage 1: find the smallest ε that works

- Qi only released images for ε = 16, 32, 64. To test ε = 8 we have to generate an image ourselves.
- Their attack scripts are in `qi-repo/` (`minigpt_visual_attack.py`, `llava_llama_v2_visual_attack.py`). They take an `--eps` setting, but they are written for 13B models.
- Plan: adapt the attack loop (projected gradient descent in `qi-repo/minigpt_utils/visual_attacker.py`) to a 7B model that fits on Colab, and run it at ε = 8, 16, 32.
- Then measure ASR for each ε with the notebook, and PSNR/SSIM with `measure_perturbation.py`.

### E. Stage 2: our own images on newer open models

- Run the same attack on newer open models (Qwen2.5-VL, Llama 3.2 Vision).
- Record for each: does it work at all, at which ε, and the ASR.
- If a model resists, that is still a result. Report how far we got.

### F. Stage 3: closed models

- **Check with the TA (Kaiyuan, kaiyuanzhang@ucla.edu) first.** ChatGPT, Gemini and Claude forbid deliberate jailbreak attempts in their terms of service.
- If approved: use a small number of test prompts, record refuse vs. comply, and report counts only.
- If the images don't transfer, that agrees with Schaeffer et al. (ICLR 2025) and is a valid finding.

### G. Deadlines (from the intro deck)

- Midterm presentation + report: 11/16
- Final presentation: 11/30
- Final report: week 11
