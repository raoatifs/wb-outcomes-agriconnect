"""One-page PDF that tells the AgriConnect story stepwise, for a lay reader.

Portrait Letter page: header -> 5 numbered steps (challenge, solution, reach,
where, trust) -> footer. Numbers come from outputs/results_summary.json so the
page stays in sync with the analysis.
"""
from __future__ import annotations
import json
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

from . import config

BLUE = "#00335b"
ACCENT = "#c8102e"
INK = "#1a1a1a"
MUTED = "#5b6670"
BG = "#ffffff"
STEP_BG = "#eef2f5"

OUT = config.OUTPUTS / "AgriConnect_story_onepager.pdf"


def _load() -> dict:
    return json.loads((config.OUTPUTS / "results_summary.json").read_text())


def _wrap(ax, text, x, y, width, size, color=INK, weight="normal", line=0.019):
    lines = textwrap.wrap(text, width=width)
    for i, ln in enumerate(lines):
        ax.text(x, y - i * line, ln, transform=ax.transAxes, fontsize=size,
                color=color, weight=weight, va="top")
    return y - len(lines) * line


def _step_number(ax, n, y):
    ax.add_patch(Circle((0.085, y), 0.017, transform=ax.transAxes,
                        color=ACCENT, zorder=5, clip_on=False))
    ax.text(0.085, y - 0.0015, str(n), transform=ax.transAxes, fontsize=13,
            color="white", weight="bold", ha="center", va="center", zorder=6)


def build() -> str:
    res = _load()
    fig = plt.figure(figsize=(8.5, 11), dpi=150)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    # --- header -------------------------------------------------------------
    ax.add_patch(plt.Rectangle((0, 0.972), 1, 0.028, color=ACCENT, clip_on=False))
    ax.text(0.06, 0.95, "AGRICONNECT", fontsize=12, color=ACCENT, weight="bold")
    ax.text(0.06, 0.935, "Helping smallholder farmers: the story in one page",
            fontsize=16, color=BLUE, weight="bold", va="top")
    _wrap(ax, "What the World Bank's AgriConnect program does for small farmers, "
          f"and its impact so far across {res['n_projects']} projects in "
          f"{res['n_countries_single']} countries.",
          0.06, 0.905, width=104, size=10, color=MUTED)
    ax.plot([0.06, 0.94], [0.876, 0.876], color="#d7dde2", lw=1)

    def step_panel(y0, y1):
        ax.add_patch(FancyBboxPatch((0.12, y0), 0.82, y1 - y0,
                     boxstyle="round,pad=0.004,rounding_size=0.010",
                     transform=ax.transAxes, facecolor=STEP_BG,
                     edgecolor="none", clip_on=False, zorder=0))

    XT, WF, SZ, LN = 0.145, 92, 10.5, 0.019  # text left, width, size, line height

    # --- step 1: the challenge ---------------------------------------------
    step_panel(0.705, 0.855)
    _step_number(ax, 1, 0.840)
    ax.text(XT, 0.845, "The challenge small farmers face",
            fontsize=14, color=BLUE, weight="bold", va="top")
    _wrap(ax, "Small farms grow much of the world's food, but many farmers can't "
          "reach buyers or get a fair price; loans, quality seeds, and equipment "
          "are hard to get; and droughts and floods can wipe out a whole season. "
          "The result is low, unpredictable incomes and food-insecure families.",
          XT, 0.812, width=WF, size=SZ, line=LN)

    # --- step 2: the solution ----------------------------------------------
    step_panel(0.525, 0.690)
    _step_number(ax, 2, 0.675)
    ax.text(XT, 0.680, "What AgriConnect does about it",
            fontsize=14, color=BLUE, weight="bold", va="top")
    y = _wrap(ax, "AgriConnect connects farmers to what they need to succeed:",
              XT, 0.648, width=WF, size=SZ, color=INK, line=LN)
    for b in [
        "Finance and investment, so farmers can afford to grow more.",
        "Links to markets and agribusiness, so they can sell at a fair price.",
        "Better seeds, tools, and training to raise their yields.",
        "Climate-smart farming to withstand droughts and floods.",
    ]:
        y = _wrap(ax, "•  " + b, XT, y - 0.004, width=WF, size=SZ, line=LN)
    _wrap(ax, "It brings governments, private business, and farmers together toward "
          "the same goal.", XT, y - 0.006, width=WF, size=SZ, color=MUTED, line=LN)

    # --- step 3: the impact -------------------------------------------------
    step_panel(0.385, 0.510)
    _step_number(ax, 3, 0.495)
    ax.text(XT, 0.500, "The impact so far", fontsize=14, color=BLUE,
            weight="bold", va="top")
    A = config.AGRICONNECT
    ax.text(XT, 0.468, f"{A['reach_long']} farmers reached",
            fontsize=19, color=BLUE, weight="bold", va="top")
    _wrap(ax, f"By {A['reach_asof']}, AgriConnect had reached {A['reach_long']} "
          f"farmers — an early step toward its goal of {A['goal_long']} by "
          f"{A['goal_year']}, with finance, markets, tools, and training, and most "
          "of the progress coming from programs still running and growing.",
          XT, 0.428, width=WF, size=SZ, line=LN)

    # --- step 4: where ------------------------------------------------------
    step_panel(0.195, 0.370)
    _step_number(ax, 4, 0.355)
    ax.text(XT, 0.360, "Reaching where it matters most",
            fontsize=14, color=BLUE, weight="bold", va="top")
    _wrap(ax, f"{res['africa_share_pct']:.0f}% of farmers reached are in "
          "Sub-Saharan Africa, where hunger and climate risk hit hardest. Farming "
          "programs are the large majority, and a few big national and regional "
          "programs lead the way — the 5 largest reached about two-thirds of "
          "all farmers.",
          XT, 0.330, width=40, size=SZ, line=LN)
    iax = fig.add_axes([0.615, 0.225, 0.29, 0.115]); iax.set_facecolor(STEP_BG)
    names = [c for c, _ in res["top5_countries"]][::-1]
    vals = [v / 1e6 for _, v in res["top5_countries"]][::-1]
    iax.barh(names, vals, color=BLUE)
    iax.set_xlabel("farmers reached (millions)", fontsize=8)
    iax.tick_params(labelsize=8)
    iax.set_title("Top 5 countries", fontsize=9, color=INK, loc="left")
    for s in ("top", "right"):
        iax.spines[s].set_visible(False)

    # --- step 5: trust ------------------------------------------------------
    step_panel(0.045, 0.180)
    _step_number(ax, 5, 0.165)
    ax.text(XT, 0.170, "Why the numbers can be trusted",
            fontsize=14, color=BLUE, weight="bold", va="top")
    _wrap(ax, "Every project is checked from start to finish. Goals and targets are "
          "set at the start in a Project Appraisal Document (PAD); progress is "
          "tracked along the way in Implementation Status and Results Reports (ISRs); "
          "and final results are confirmed at the end in an Implementation Completion "
          "and Results Report (ICR). Each farmer is counted only once, so the figures "
          "reflect real people helped.",
          XT, 0.140, width=WF, size=SZ, line=LN)

    ax.text(0.06, 0.022, "Sources: World Bank AgriConnect program figures "
            f"· {res['n_projects']}-project outcome extract · analysis by Atif Rao",
            fontsize=8.5, color=MUTED)

    config.OUTPUTS.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor=BG)
    fig.savefig(OUT.with_suffix(".png"), facecolor=BG, dpi=120)  # preview
    plt.close(fig)
    return str(OUT)


if __name__ == "__main__":
    print("wrote", build())
