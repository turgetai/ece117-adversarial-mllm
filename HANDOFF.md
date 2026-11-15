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
| `first_test.md` | Write-up of the LLaVA transfer test: what, why, how, results |
| `README.md` | Short intro and setup |
| `Midterm_slides.md` | Text draft for the 8 midterm slides, with speaker notes |
| `Midterm_report.md` | Draft of the midterm report (4 graded sections) |
| `scripts/measure_perturbation.py` | Compares Qi's attack images with the clean image; writes the CSV and two figures |
| `scripts/make_slide_figure.py` | Makes the slide figure (clean panda + 3 attack images with scores) |
| `results/perturbation_metrics.csv` | Measured numbers (table below) |
| `results/slide_results_row.png` | Figure for slide 6 |
| `results/slide_clean_vs_adv.png` | Clean vs. ε = 16 vs. amplified noise |
| `results/side_by_side.png` | All four attack images plus their noise |
| `notebooks/llava_transfer_test.ipynb` | Colab notebook: tests Qi's images on LLaVA-1.5-7B. Run on 2026-11-15, works. |
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
- Our workaround: **7B models on Colab**. Testing runs on the free T4 GPU with the model loaded in 4-bit. Building attack images uses a paid L4 GPU. See the GPU plan below.

---

### GPU plan and cost (about $10 total)

The free student Colab Pro offer did **not** show up on Etai's UCLA account (checked 2026-11-15), so we plan to pay a small amount instead.

| Job | GPU | Memory | Cost | Why |
|---|---|---|---|---|
| Testing images on a model (Stage 1 LLaVA test, any "ask the model" run) | **T4** | 15 GB | Free | The 4-bit 7B model fits, and no gradients are needed |
| Building our own attack images (Stage 2) | **L4** | 24 GB | about 1.7 compute units/hour, roughly $0.17/hour | Building an image needs gradients, which takes much more memory than the T4 has |
| Only if the L4 runs out of memory | A100 | 40 GB | about 5.4 compute units/hour, roughly $0.54/hour | 3x the price of the L4, so use it as a last resort |

- **What to buy:** one **Pay As You Go** pack, **$9.99 for 100 compute units**. It is a one-time purchase, so there is no subscription to cancel. Colab Pro costs the same per month for the same 100 units, but it renews.
- **How far it goes:** 100 units is about 58 hours on the L4, or about 18 hours on the A100.
- **How to split it:** units belong to one Google account and cannot be shared. One person buys the pack and runs the GPU jobs, and the team splits the $10. Everyone else can still open and edit the shared notebook.
- **To pick the GPU in Colab:** Runtime → Change runtime type → choose T4, L4 or A100.
- **Not tested yet:** the unit rates above are from a March 2026 price check and move a little. Whether the full attack fits in the L4's 24 GB is an estimate. If it doesn't, try the 4-bit model first, then the A100.
- Stop the runtime when you finish (Runtime → Disconnect and delete runtime). Idle sessions still burn units.

### LLaVA transfer test: done (2026-11-15)

Ran all 40 of Qi's harmful test prompts with each of the 5 images on LLaVA-1.5-7B (4-bit, free Colab T4, about 20 minutes).

| Image | Not refused (of 40) | Rate |
|---|---|---|
| Clean | 23 | 57.5% |
| ε = 16 | 24 | 60.0% |
| ε = 32 | 24 | 60.0% |
| ε = 64 | 21 | 52.5% |
| Unconstrained | 25 | 62.5% |

- **No clear transfer:** Qi's images were built for MiniGPT-4 and make no real difference on LLaVA.
- **The prompt decides, not the image:** 34 of 40 prompts got the same outcome with all five images.
- **LLaVA-1.5 is weakly protected:** it already answers 57.5% with a clean image, so it is a poor model to show a jailbreak on.
- "Not refused" means no refusal phrase was found. It does not prove the reply was harmful. Someone should hand-check a sample.
- Per-prompt table: `results/llava_transfer_refusals.csv` (1 = refused). It has no model text. The full replies are in `results/llava_transfer_results_40.csv` on Etai's computer only. That file is git-ignored because the repo is public and the replies can be offensive. A rerun on 2026-11-15 gave the same counts.

---

## 4. What is NOT done

- **Slide 6 picture:** the slide now has the results table. The panda figure is optional.
- **The LLaVA replies are not hand-checked.** The numbers below come from a keyword check only.
- **Stages 2 and 3** (our own images, closed models) have not been started.

---

## 5. What to do next, and how

### A. Hand-check the LLaVA results (do this first)

The test has been run (results above). What is left is checking it by hand.

1. Open the notebook in Colab straight from the repo: `https://colab.research.google.com/github/turgetai/ece117-adversarial-mllm/blob/main/notebooks/llava_transfer_test.ipynb`
2. Runtime → Change runtime type → **T4 GPU**, then Runtime → **Run all**. Model download takes about 6 minutes. The first part runs 10 prompts. The last cell runs all 40 (about 20 minutes).
3. Open `llava_transfer_results_40.csv` from the folder icon on the left. Read a sample of the replies marked "not refused" and decide whether each one really complied. A reply can avoid refusal words and still not be harmful.
4. If the hand-checked numbers differ from the keyword numbers, update `Midterm_report.md` section 4.4 and slide 6.

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

Optional. Slide 6 already has the results table and is full. If you want the panda picture too, use `results/slide_results_row.png`, but you would need to shrink the table or move it to its own slide.

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
