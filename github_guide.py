"""One-page PDF: step-by-step guide to uploading this project to GitHub.

Explains which folders to upload (and which to skip), with two methods:
git push (recommended) and the GitHub website drag-and-drop.
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from . import config

BLUE = "#00335b"
ACCENT = "#c8102e"
GREEN = "#1a7f45"
INK = "#1a1a1a"
MUTED = "#5b6670"
BG = "#ffffff"
PANEL = "#eef2f5"
MONO = {"family": "monospace"}

OUT = config.OUTPUTS / "GitHub_upload_instructions.pdf"


def _line(ax, x, y, text, size=10.5, color=INK, weight="normal", mono=False, va="top"):
    kw = dict(MONO) if mono else {}
    ax.text(x, y, text, transform=ax.transAxes, fontsize=size, color=color,
            weight=weight, va=va, **kw)


def build() -> str:
    fig = plt.figure(figsize=(8.5, 11), dpi=150)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    ax.add_patch(plt.Rectangle((0, 0.972), 1, 0.028, color=ACCENT, clip_on=False))
    _line(ax, 0.06, 0.95, "GITHUB UPLOAD GUIDE", 12, ACCENT, "bold")
    _line(ax, 0.06, 0.935, "How to put this project on GitHub — step by step",
          16, BLUE, "bold")
    _line(ax, 0.06, 0.905,
          "Project folder: wb-outcomes-agriconnect  ·  it is already set up "
          "with Git, so you only need to push it.", 10, MUTED)
    ax.plot([0.06, 0.94], [0.884, 0.884], color="#d7dde2", lw=1)

    def panel(y0, y1):
        ax.add_patch(FancyBboxPatch((0.05, y0), 0.90, y1 - y0,
                     boxstyle="round,pad=0.004,rounding_size=0.010",
                     transform=ax.transAxes, facecolor=PANEL, edgecolor="none"))

    import textwrap

    # --- what to upload -----------------------------------------------------
    panel(0.565, 0.870)
    _line(ax, 0.08, 0.855, "1.  What to upload", 14, BLUE, "bold")
    _line(ax, 0.08, 0.830, "Upload these folders and files (✓ = include):",
          10.5, INK)
    inc = [
        "README.md, requirements.txt, run_pipeline.py",
        "methodology_note.md, ARTICLE_agriconnect.md, .gitignore",
        "src/        — all the Python code (pipeline, analysis, explainers)",
        "tests/      — the automated data-quality checks",
        "outputs/    — figures, explainers, tables, one-pagers, results",
        "data/raw/   — the released AgriConnect .xlsx + sample document",
    ]
    y = 0.806
    for t in inc:
        _line(ax, 0.10, y, "✓", 11, GREEN, "bold")
        _line(ax, 0.13, y, t, 10.0, INK, mono=True)
        y -= 0.0235
    _line(ax, 0.08, y - 0.002, "Do NOT upload (already ignored by .gitignore):",
          10.5, INK)
    y -= 0.028
    for t in ["data/db/    — local SQLite database (rebuilds itself)",
              "data/docs/  — any downloaded documents",
              "__pycache__/, .pytest_cache/, .DS_Store"]:
        _line(ax, 0.10, y, "✗", 11, ACCENT, "bold")
        _line(ax, 0.13, y, t, 10.0, MUTED, mono=True)
        y -= 0.0235

    # --- method A: git ------------------------------------------------------
    panel(0.320, 0.550)
    _line(ax, 0.08, 0.536, "2.  Easiest way — GitHub CLI (recommended)", 14,
          BLUE, "bold")
    _line(ax, 0.08, 0.511, "Open Terminal and run these, one per line:", 10.5, INK)
    y = 0.487
    for c in ['cd "wb-outcomes-agriconnect"',
              'gh repo create wb-outcomes-agriconnect --public --source=. --push']:
        ax.add_patch(FancyBboxPatch((0.09, y - 0.017), 0.82, 0.024,
                     boxstyle="round,pad=0.002,rounding_size=0.006",
                     transform=ax.transAxes, facecolor="#e2e8ee", edgecolor="none"))
        _line(ax, 0.10, y, "$ " + c, 9.6, "#0b3d2e", mono=True)
        y -= 0.030
    _line(ax, 0.08, y + 0.002,
          "That creates the repo and uploads everything in one step.", 10, MUTED)
    _line(ax, 0.08, y - 0.020, "If you use plain git instead:", 10.5, INK)
    y -= 0.044
    for c in ['git remote add origin https://github.com/<you>/wb-outcomes-agriconnect.git',
              'git branch -M main',
              'git push -u origin main']:
        _line(ax, 0.10, y, "$ " + c, 9.3, "#0b3d2e", mono=True)
        y -= 0.021

    # --- method B: website --------------------------------------------------
    panel(0.075, 0.305)
    _line(ax, 0.08, 0.291, "3.  Or upload on the GitHub website", 14, BLUE, "bold")
    steps = [
        "Go to github.com → New repository → name it "
        "“wb-outcomes-agriconnect” → Create (do not add a README).",
        "On the empty repo page, click “uploading an existing file”.",
        "Drag in the folders src, tests, outputs, and data (with only its raw "
        "sub-folder), plus the root files above.",
        "Do not add the data/db folder. Then click “Commit changes”.",
    ]
    y = 0.265
    for i, s in enumerate(steps, 1):
        _line(ax, 0.09, y, f"{i}.", 10.5, ACCENT, "bold")
        lines = textwrap.wrap(s, width=94)
        for j, ln in enumerate(lines):
            _line(ax, 0.12, y - j * 0.019, ln, 10, INK)
        y -= 0.019 * len(lines) + 0.011

    tip = ("Tip: keep the .xlsx in data/raw only if it is cleared for public "
           "release; otherwise upload the code and outputs and keep the data file "
           "private.")
    for j, ln in enumerate(textwrap.wrap(tip, width=104)):
        _line(ax, 0.06, 0.052 - j * 0.017, ln, 9.5, MUTED)
    _line(ax, 0.06, 0.016, "AgriConnect analytics project · prepared by Atif Rao",
          9, MUTED)

    config.OUTPUTS.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor=BG)
    fig.savefig(OUT.with_suffix(".png"), facecolor=BG, dpi=120)
    plt.close(fig)
    return str(OUT)


if __name__ == "__main__":
    print("wrote", build())
