"""Slide figure: clean image next to each constrained attack image, with its scores."""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

img_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
rows = list(csv.DictReader(open(out_dir / "perturbation_metrics.csv")))[:3]
files = ["prompt_constrained_16.bmp", "prompt_constrained_32.bmp", "prompt_constrained_64.bmp"]

fig, axes = plt.subplots(1, 4, figsize=(13, 4.1))
axes[0].imshow(Image.open(img_dir / "clean.jpeg").convert("RGB").resize((224, 224), Image.BICUBIC))
axes[0].set_title("Clean image", fontsize=17)
axes[0].set_xlabel("original", fontsize=15)
for ax, r, f in zip(axes[1:], rows, files):
    ax.imshow(Image.open(img_dir / f).convert("RGB"))
    ax.set_title(f"Attack, ε = {r['budget_eps']}/255", fontsize=17)
    ax.set_xlabel(f"PSNR {float(r['psnr_db']):.1f} dB   SSIM {float(r['ssim']):.2f}", fontsize=15)
for ax in axes:
    ax.set_xticks([])
    ax.set_yticks([])
fig.tight_layout()
fig.savefig(out_dir / "slide_results_row.png", dpi=150)
