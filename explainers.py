"""Turn the key findings into shareable JPEG explainer cards (16:9, 1200x675).

Each card is a self-contained visual explanation of one result, sized for
LinkedIn / Substack. Numbers are read from outputs/results_summary.json so the
cards stay in sync with the analysis.
"""
from __future__ import annotations
import json
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch, Circle

from . import config

BLUE = "#00335b"
ACCENT = "#c8102e"
INK = "#1a1a1a"
MUTED = "#5b6670"
BG = "#f5f7f9"
CARD = "#ffffff"
STEP_BG = "#eef2f5"

EXPLAINERS = config.OUTPUTS / "explainers"


def _load() -> dict:
    return json.loads((config.OUTPUTS / "results_summary.json").read_text())


def _new_card():
    fig = plt.figure(figsize=(12, 6.75), dpi=100)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0.045, 0.06, 0.91, 0.88])  # card panel
    ax.set_facecolor(CARD)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("#e2e6ea")
    # accent bar
    ax.add_patch(plt.Rectangle((0, 0.965), 1, 0.035, color=ACCENT,
                               transform=ax.transAxes, clip_on=False))
    return fig, ax


def _wrap(ax, text, x, y, width, size, color=INK, weight="normal", line=0.052):
    for i, ln in enumerate(textwrap.wrap(text, width=width)):
        ax.text(x, y - i * line, ln, transform=ax.transAxes, fontsize=size,
                color=color, weight=weight, va="top")
    return y - len(textwrap.wrap(text, width=width)) * line


def _kicker(ax, text):
    ax.text(0.05, 0.9, text.upper(), transform=ax.transAxes, fontsize=13,
            color=ACCENT, weight="bold", va="top")


def _bullets(ax, items, x=0.06, y=0.66, size=15.5, width=74, gap=0.028):
    """Draw a list of wrapped bullet points, returning the final y position."""
    for it in items:
        y = _wrap(ax, "•  " + it, x, y, width=width, size=size, color=INK)
        y -= gap
    return y


def _footer(ax, text="Sources: World Bank AgriConnect program figures · 245-project outcome extract · analysis by Atif Rao"):
    ax.text(0.05, 0.045, text, transform=ax.transAxes, fontsize=9.5,
            color=MUTED, va="bottom")


def _chip(ax, x, w, big, label):
    ax.add_patch(FancyBboxPatch((x, 0.545), w, 0.155,
                 boxstyle="round,pad=0.006,rounding_size=0.02",
                 transform=ax.transAxes, facecolor=STEP_BG, edgecolor="none"))
    ax.text(x + w / 2, 0.665, big, transform=ax.transAxes, fontsize=30,
            color=BLUE, weight="bold", ha="center", va="center")
    ax.text(x + w / 2, 0.585, label, transform=ax.transAxes, fontsize=11.5,
            color=MUTED, ha="center", va="center")


def card_summary(res):
    fig, ax = _new_card()
    _kicker(ax, "AgriConnect · at a glance")
    ax.text(0.05, 0.86, "The whole story on one page",
            transform=ax.transAxes, fontsize=27, color=BLUE, weight="bold", va="top")
    # three headline stat chips
    A = config.AGRICONNECT
    _chip(ax, 0.05, 0.283, A["reach_short"], f"farmers reached ({A['reach_asof']})")
    _chip(ax, 0.358, 0.283, f"{res['africa_share_pct']:.0f}%", "in Sub-Saharan Africa")
    _chip(ax, 0.666, 0.283, A["goal_short"], f"goal by {A['goal_year']}")
    # contents of the series
    ax.text(0.05, 0.485, "In this series:", transform=ax.transAxes,
            fontsize=13, color=ACCENT, weight="bold", va="top")
    items = [
        "The challenge small farmers face",
        "What AgriConnect does about it",
        "The impact so far — 19M farmers reached",
        "Reaching where it matters — 85% in Africa",
        "Why the numbers can be trusted",
        "The road to 2030",
        "An invitation for more countries to join",
    ]
    col_x = [0.06, 0.52]
    for i, it in enumerate(items):
        col = 0 if i < 4 else 1
        row = i if i < 4 else i - 4
        y = 0.42 - row * 0.075
        cx = col_x[col]
        ax.add_patch(Circle((cx + 0.012, y), 0.015, transform=ax.transAxes,
                            color=ACCENT, clip_on=False))
        ax.text(cx + 0.012, y - 0.001, str(i + 1), transform=ax.transAxes,
                fontsize=10.5, color="white", weight="bold", ha="center", va="center")
        ax.text(cx + 0.045, y, it, transform=ax.transAxes, fontsize=12.5,
                color=INK, va="center")
    _footer(ax)
    return fig


def card_cover(res):
    fig, ax = _new_card()
    _kicker(ax, "World Bank · AgriConnect")
    ax.text(0.05, 0.77, "Backing the world's", transform=ax.transAxes,
            fontsize=40, color=BLUE, weight="bold", va="top")
    ax.text(0.05, 0.645, "smallholder farmers", transform=ax.transAxes,
            fontsize=40, color=BLUE, weight="bold", va="top")
    _wrap(ax,
          "Small farms grow much of the world's food, yet millions of small "
          "farmers struggle to reach markets, finance, and modern tools. "
          "AgriConnect helps change that — so farmers can grow more, earn "
          "more, and stand up to a changing climate.",
          0.05, 0.47, width=64, size=16.5, color=INK, line=0.056)
    ax.text(0.05, 0.13, f"A simple look at {res['n_projects']} AgriConnect "
            f"projects across {res['n_countries_single']} countries.",
            transform=ax.transAxes, fontsize=12.5, color=MUTED, va="bottom", style="italic")
    _footer(ax)
    return fig


def card_problem(res):
    fig, ax = _new_card()
    _kicker(ax, "The challenge")
    ax.text(0.05, 0.81, "Small farmers feed the world —",
            transform=ax.transAxes, fontsize=25, color=BLUE, weight="bold", va="top")
    ax.text(0.05, 0.705, "but face big barriers every day",
            transform=ax.transAxes, fontsize=25, color=BLUE, weight="bold", va="top")
    _bullets(ax, [
        "It is hard to reach buyers and get a fair price for their harvest.",
        "Loans, quality seeds, and equipment are often out of reach.",
        "Droughts, floods, and a changing climate can wipe out a season.",
        "Low and unpredictable incomes leave families food-insecure.",
    ], x=0.06, y=0.57, size=15.5, width=78)
    _footer(ax)
    return fig


def card_solution(res):
    fig, ax = _new_card()
    _kicker(ax, "What AgriConnect does")
    ax.text(0.05, 0.81, "Connecting farmers to what",
            transform=ax.transAxes, fontsize=25, color=BLUE, weight="bold", va="top")
    ax.text(0.05, 0.705, "they need to succeed",
            transform=ax.transAxes, fontsize=25, color=BLUE, weight="bold", va="top")
    _bullets(ax, [
        "Finance and investment, so farmers can afford to grow more.",
        "Links to markets and agribusiness, so they can sell for a fair price.",
        "Better seeds, tools, and training to raise yields.",
        "Climate-smart, resilient farming to withstand droughts and floods.",
    ], x=0.06, y=0.57, size=15.5, width=78)
    ax.text(0.05, 0.11, "Governments, private business, and farmers working "
            "together toward the same goal.",
            transform=ax.transAxes, fontsize=12.5, color=BLUE, va="bottom", weight="bold")
    _footer(ax)
    return fig


def card_reach(res):
    A = config.AGRICONNECT
    fig, ax = _new_card()
    _kicker(ax, "The impact so far")
    ax.text(0.05, 0.79, f"{A['reach_long']} farmers",
            transform=ax.transAxes, fontsize=38, color=BLUE, weight="bold", va="top")
    ax.text(0.055, 0.605, f"reached as of {A['reach_asof']} with finance, markets, "
            "tools, and training",
            transform=ax.transAxes, fontsize=13, color=MUTED, va="top")
    _wrap(ax,
          f"By {A['reach_asof']}, AgriConnect had already reached {A['reach_long']} "
          "farmers — an early step toward its goal of reaching "
          f"{A['goal_long']} farmers by {A['goal_year']}. Most of this progress "
          "comes from programs that are still running and still growing, so the "
          "number keeps rising.",
          0.05, 0.49, width=90, size=15, color=INK)
    _footer(ax)
    return fig


def card_geography(res):
    fig, ax = _new_card()
    _kicker(ax, "Reaching where it matters most")
    ax.text(0.05, 0.81, f"{res['africa_share_pct']:.0f}% of farmers reached",
            transform=ax.transAxes, fontsize=24, color=BLUE, weight="bold", va="top")
    ax.text(0.05, 0.715, "are in Sub-Saharan Africa",
            transform=ax.transAxes, fontsize=24, color=BLUE, weight="bold", va="top")
    _wrap(ax,
          "AgriConnect focuses on the places where hunger and climate risk hit "
          "hardest. Farming programs make up the large majority of this support.",
          0.05, 0.60, width=34, size=14.5, color=INK)
    _wrap(ax,
          "Big national and regional programs lead the way: the 5 largest reached "
          "about two-thirds of all farmers, and the top 20 reached nearly nine in ten.",
          0.05, 0.34, width=34, size=13.5, color=MUTED)
    # top-5 countries bars
    iax = fig.add_axes([0.62, 0.17, 0.31, 0.50]); iax.set_facecolor(CARD)
    names = [c for c, _ in res["top5_countries"]][::-1]
    vals = [v/1e6 for _, v in res["top5_countries"]][::-1]
    iax.barh(names, vals, color=BLUE)
    iax.set_xlabel("farmers reached (millions)", fontsize=9)
    iax.tick_params(labelsize=9)
    for s in ("top", "right"):
        iax.spines[s].set_visible(False)
    iax.set_title("Top 5 countries", fontsize=10, color=INK, loc="left")
    _footer(ax)
    return fig


def card_trust(res):
    fig, ax = _new_card()
    _kicker(ax, "Numbers you can trust")
    ax.text(0.05, 0.81, "Every result is checked",
            transform=ax.transAxes, fontsize=25, color=BLUE, weight="bold", va="top")
    ax.text(0.05, 0.705, "from start to finish",
            transform=ax.transAxes, fontsize=25, color=BLUE, weight="bold", va="top")
    y = _wrap(ax,
              "•  Each project sets clear goals and targets at the start in a "
              "Project Appraisal Document (PAD).",
              0.06, 0.59, width=86, size=14.5, color=INK)
    y = _wrap(ax,
              "•  Progress is tracked along the way in Implementation Status "
              "and Results Reports (ISRs).",
              0.06, y - 0.028, width=86, size=14.5, color=INK)
    y = _wrap(ax,
              "•  Final results are confirmed at the end in an Implementation "
              "Completion and Results Report (ICR).",
              0.06, y - 0.028, width=86, size=14.5, color=INK)
    _wrap(ax,
          "•  And each farmer is counted only once, so the numbers reflect "
          "real people helped.",
          0.06, y - 0.028, width=86, size=14.5, color=INK)
    _footer(ax)
    return fig


def card_future(res):
    fig, ax = _new_card()
    _kicker(ax, "What comes next")
    ax.text(0.05, 0.81, "The road to 2030", transform=ax.transAxes,
            fontsize=27, color=BLUE, weight="bold", va="top")
    _wrap(ax, "AgriConnect is just getting started. Its next steps aim to help "
          "many more farmers:", 0.06, 0.70, width=88, size=14, color=INK)
    _bullets(ax, [
        "Reach 200 million farmers by 2030 — up from 19 million today.",
        "Grow World Bank Group agribusiness financing to about $9 billion a year.",
        "Sign more country compacts that turn national plans into real action.",
        "Bring in more private investment, and reduce its risk, so money reaches farms.",
        "Deepen partnerships — governments, businesses, IFAD, and others together.",
    ], x=0.06, y=0.585, size=14.5, width=80, gap=0.022)
    ax.text(0.05, 0.075, "Based on AgriConnect's publicly announced goals.",
            transform=ax.transAxes, fontsize=10, color=MUTED, va="bottom", style="italic")
    _footer(ax)
    return fig


def card_join(res):
    fig, ax = _new_card()
    _kicker(ax, "An invitation")
    ax.text(0.05, 0.81, "Agricultural countries:",
            transform=ax.transAxes, fontsize=26, color=BLUE, weight="bold", va="top")
    ax.text(0.05, 0.705, "join AgriConnect", transform=ax.transAxes,
            fontsize=26, color=ACCENT, weight="bold", va="top")
    _wrap(ax, "Countries with large farming communities can join AgriConnect to "
          "unlock real benefits for their smallholder farmers:",
          0.06, 0.60, width=90, size=14, color=INK)
    _bullets(ax, [
        "Investment and financing for farmers and agribusiness.",
        "New jobs across the food system, from farm to market.",
        "Stronger food security and higher, steadier farmer incomes.",
        "Climate-resilient, modern farming to withstand droughts and floods.",
    ], x=0.06, y=0.49, size=14.5, width=80, gap=0.022)
    ax.text(0.05, 0.085, "Bring your farmers into the network — to grow more, "
            "earn more, and build resilience.",
            transform=ax.transAxes, fontsize=12.5, color=BLUE, va="bottom", weight="bold")
    _footer(ax)
    return fig


def run() -> list:
    EXPLAINERS.mkdir(parents=True, exist_ok=True)
    res = _load()
    cards = {
        "explainer_00_summary.jpg": card_summary,
        "explainer_0_cover.jpg": card_cover,
        "explainer_1_problem.jpg": card_problem,
        "explainer_2_solution.jpg": card_solution,
        "explainer_3_reach.jpg": card_reach,
        "explainer_4_geography.jpg": card_geography,
        "explainer_5_trust.jpg": card_trust,
        "explainer_6_future.jpg": card_future,
        "explainer_7_join.jpg": card_join,
    }
    paths = []
    for name, fn in cards.items():
        fig = fn(res)
        p = EXPLAINERS / name
        fig.savefig(p, dpi=100, facecolor=fig.get_facecolor(),
                    pil_kwargs={"quality": 92})
        plt.close(fig)
        paths.append(p)
    return paths


if __name__ == "__main__":
    for p in run():
        print("wrote", p)
