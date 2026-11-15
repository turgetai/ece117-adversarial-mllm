# Adversarial Attacks on Multi-modal Language Models

Team 4A, Picture Perfect Crimes. ECE M117 Computer System Security, Fall 2026.

We reproduce the visual jailbreak attack of Qi et al. (AAAI 2024), find the smallest image change that still works, build our own images on newer open models, and test whether they transfer to closed models.

**Start with [HANDOFF.md](HANDOFF.md).** It explains what is done, what is not, and what to do next.

## Setup

```bash
pip install numpy pillow scikit-image matplotlib
git clone --depth 1 https://github.com/Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models.git qi-repo
python scripts/measure_perturbation.py qi-repo/adversarial_images results
python scripts/make_slide_figure.py qi-repo/adversarial_images results
```

Qi et al.'s repo is not included here. The clone above puts it in `qi-repo/`, which is git-ignored.

The LLaVA test runs on Google Colab (free T4 GPU; building our own attack images later uses a paid L4 GPU, about $10 total, see HANDOFF.md): upload `notebooks/llava_transfer_test.ipynb` and choose Run all.

Model outputs from the test prompts may be offensive. Report counts only.
