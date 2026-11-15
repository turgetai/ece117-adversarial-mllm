"""Measure how visible Qi et al.'s adversarial images are.

Compares each released adversarial image against the clean panda it was
built from and reports:
  - L-inf : largest change to any single pixel value (0-255 scale)
  - L2    : mean per-pixel change (root mean square, 0-255 scale)
  - PSNR  : peak signal-to-noise ratio in dB (higher = harder to see)
  - SSIM  : structural similarity, 1.0 = identical
It also saves a side-by-side figure and an amplified "noise only" view.

Usage:
  python measure_perturbation.py <qi-repo>/adversarial_images <output dir>
"""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

SIZE = 224  # MiniGPT-4's input resolution; the attack images are 224x224
IMAGES = [
    ("eps = 16/255", "prompt_constrained_16.bmp", 16),
    ("eps = 32/255", "prompt_constrained_32.bmp", 32),
    ("eps = 64/255", "prompt_constrained_64.bmp", 64),
    ("unconstrained", "prompt_unconstrained.bmp", None),
]


def load(path, resize=False):
    img = Image.open(path).convert("RGB")
    if resize:
        # MiniGPT-4's eval processor resizes with bicubic interpolation
        img = img.resize((SIZE, SIZE), Image.BICUBIC)
    return np.asarray(img).astype(np.float64)


def main(img_dir, out_dir):
    img_dir, out_dir = Path(img_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    clean = load(img_dir / "clean.jpeg", resize=True)
    rows, advs = [], []
    for label, name, eps in IMAGES:
        adv = load(img_dir / name)
        diff = adv - clean
        rows.append({
            "image": label,
            "budget_eps": eps if eps is not None else "none",
            "linf": int(np.abs(diff).max()),
            "l2_rms": round(float(np.sqrt((diff ** 2).mean())), 2),
            "pct_pixels_changed": round(100 * float((np.abs(diff) > 1).mean()), 1),
            "psnr_db": round(float(peak_signal_noise_ratio(clean, adv, data_range=255)), 2),
            "ssim": round(float(structural_similarity(clean, adv, data_range=255, channel_axis=2)), 3),
        })
        advs.append((label, adv, diff))

    with open(out_dir / "perturbation_metrics.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    for r in rows:
        print(r)

    # Row 1: the images. Row 2: the added noise, amplified so it is visible.
    fig, axes = plt.subplots(2, 5, figsize=(15, 6.4))
    axes[0, 0].imshow(clean.astype(np.uint8))
    axes[0, 0].set_title("clean")
    axes[1, 0].axis("off")
    for i, ((label, adv, diff), r) in enumerate(zip(advs, rows), start=1):
        axes[0, i].imshow(adv.astype(np.uint8))
        axes[0, i].set_title(f"{label}\nPSNR {r['psnr_db']} dB, SSIM {r['ssim']}", fontsize=10)
        scale = 127 / max(np.abs(diff).max(), 1)
        axes[1, i].imshow(np.clip(diff * scale + 128, 0, 255).astype(np.uint8))
        axes[1, i].set_title(f"added noise (x{scale:.1f})", fontsize=10)
    for ax in axes.flat:
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("Qi et al. adversarial images vs. clean input")
    fig.tight_layout(h_pad=2.5)
    fig.savefig(out_dir / "side_by_side.png", dpi=150)

    # Slide-sized version: clean vs eps=16 only
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.8))
    label, adv, diff = advs[0]
    scale = 127 / max(np.abs(diff).max(), 1)
    for ax, img, title in [
        (axes[0], clean, "Clean image"),
        (axes[1], adv, f"Adversarial ({label})"),
        (axes[2], np.clip(diff * scale + 128, 0, 255), f"Hidden noise (amplified x{scale:.0f})"),
    ]:
        ax.imshow(img.astype(np.uint8))
        ax.set_title(title)
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_dir / "slide_clean_vs_adv.png", dpi=150)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
