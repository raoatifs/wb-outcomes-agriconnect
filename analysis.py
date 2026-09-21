"""Portfolio analytics on the AgriConnect outcome table.

Produces the headline results, CSV tables, and PNG figures used in the
executive one-pager and the LinkedIn/Substack article. Every number is
reproducible from the SQL `projects` table.

Key measurement note: the AgriConnect extract reports three values per row:
  * baseline_value  - starting value
  * progress_value  - most recent *cumulative reported* value (ISR/ICR)
  * achieved_results - beneficiaries after within-project de-duplication and
    cross-project geospatial de-duplication (the Scorecard-consistent figure)
The gap between progress_value and achieved_results is the central story.
"""
from __future__ import annotations
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from . import config, db

REGION_LABELS = {
    "AFW": "West & Central Africa", "AFE": "East & Southern Africa",
    "SAR": "South Asia", "EAP": "East Asia & Pacific",
    "LCR": "Latin America & Caribbean", "MENAAP": "Middle East & N. Africa",
    "ECA": "Europe & Central Asia",
}
BLUE = "#00335b"
ACCENT = "#c8102e"


def _style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", alpha=0.25)


def load() -> pd.DataFrame:
    conn = db.connect()
    df = db.read_projects(conn)
    conn.close()
    return df


def compute(df: pd.DataFrame) -> dict:
    ach, prog = "achieved_results", "progress_value"
    tot_ach = float(df[ach].sum())
    tot_prog = float(df[prog].sum())
    s = df.sort_values(ach, ascending=False)

    by_region = (df.groupby("region")[ach].sum()
                 .sort_values(ascending=False))
    by_gp = df.groupby("global_practice")[ach].sum().sort_values(ascending=False)
    by_status = df.groupby("project_status")[ach].agg(["count", "sum"])

    single = df[df["is_regional_aggregate"] == 0]
    by_country = (single.groupby("country")[ach].sum()
                  .sort_values(ascending=False))

    d = df[df[prog] > 0].copy()
    d["ratio"] = d[ach] / d[prog]

    res = {
        "n_projects": int(df["project_id"].nunique()),
        "n_countries_single": int(single["country"].nunique()),
        "n_regional_ops": int((df["is_regional_aggregate"] == 1).sum()),
        "n_countries_incl_regional": int(df["country"].nunique()),
        "n_active": int((df["project_status"] == "Active").sum()),
        "n_closed": int((df["project_status"] == "Closed").sum()),
        "approval_year_min": int(df["approval_year"].min()),
        "approval_year_median": int(df["approval_year"].median()),
        "approval_year_max": int(df["approval_year"].max()),
        "total_reported_progress": round(tot_prog),
        "total_achieved_dedup": round(tot_ach),
        "dedup_reduction_pct": round(100 * (1 - tot_ach / tot_prog), 1),
        "top5_project_share_pct": round(100 * s[ach].head(5).sum() / tot_ach, 1),
        "top10_project_share_pct": round(100 * s[ach].head(10).sum() / tot_ach, 1),
        "top20_project_share_pct": round(100 * s[ach].head(20).sum() / tot_ach, 1),
        "africa_share_pct": round(
            100 * by_region.reindex(["AFW", "AFE"]).sum() / tot_ach, 1),
        "agr_practice_share_pct": round(100 * by_gp.get("AGR", 0) / tot_ach, 1),
        "active_share_of_achieved_pct": round(
            100 * by_status.loc["Active", "sum"] / tot_ach, 1),
        "baseline_zero_pct": round(100 * (df["baseline_value"] == 0).mean(), 1),
        "median_achieved_to_progress_ratio": round(d["ratio"].median(), 3),
        "top_country": by_country.index[0],
        "top_country_value": round(float(by_country.iloc[0])),
        "top5_countries": [(c, round(float(v)))
                           for c, v in by_country.head(5).items()],
        "by_region": {k: round(float(v)) for k, v in by_region.items()},
        "by_gp": {k: round(float(v)) for k, v in by_gp.head(6).items()},
    }
    return res


def write_tables(df: pd.DataFrame) -> None:
    config.TABLES.mkdir(parents=True, exist_ok=True)
    ach = "achieved_results"
    (df.groupby("region")[ach].sum().sort_values(ascending=False)
     .rename("achieved_beneficiaries")
     .to_csv(config.TABLES / "by_region.csv"))
    (df.groupby("global_practice")[ach].sum().sort_values(ascending=False)
     .rename("achieved_beneficiaries")
     .to_csv(config.TABLES / "by_global_practice.csv"))
    (df[df["is_regional_aggregate"] == 0].groupby("country")[ach].sum()
     .sort_values(ascending=False).head(15).rename("achieved_beneficiaries")
     .to_csv(config.TABLES / "top15_countries.csv"))
    cols = ["project_id", "project_name", "country", "global_practice",
            "project_status", "progress_value", "achieved_results"]
    (df.sort_values(ach, ascending=False)[cols].head(20)
     .to_csv(config.TABLES / "top20_projects.csv", index=False))


def make_figures(df: pd.DataFrame, res: dict) -> None:
    config.FIGURES.mkdir(parents=True, exist_ok=True)
    ach = "achieved_results"

    # 1. De-duplication: reported vs Scorecard-consistent
    fig, ax = plt.subplots(figsize=(6.4, 4))
    vals = [res["total_reported_progress"], res["total_achieved_dedup"]]
    bars = ax.bar(["Reported\n(cumulative ISR/ICR)", "De-duplicated\n(Scorecard-consistent)"],
                  vals, color=[ACCENT, BLUE], width=0.6)
    ax.set_title("AgriConnect beneficiaries: reported vs de-duplicated", fontweight="bold")
    ax.set_ylabel("People")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M"))
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, v, f"{v/1e6:.1f}M",
                ha="center", va="bottom", fontweight="bold")
    ax.text(0.5, 0.9, f"-{res['dedup_reduction_pct']:.0f}% after de-duplication",
            transform=ax.transAxes, ha="center", color=ACCENT, fontweight="bold")
    _style(ax); fig.tight_layout()
    fig.savefig(config.FIGURES / "fig1_dedup.png", dpi=150); plt.close(fig)

    # 2. Beneficiaries by region
    br = df.groupby("region")[ach].sum().sort_values()
    fig, ax = plt.subplots(figsize=(6.8, 4))
    labels = [REGION_LABELS.get(r, r) for r in br.index]
    ax.barh(labels, br.values / 1e6, color=BLUE)
    ax.set_title("De-duplicated beneficiaries by region", fontweight="bold")
    ax.set_xlabel("People (millions)")
    _style(ax); ax.grid(axis="x", alpha=0.25); ax.grid(axis="y", alpha=0)
    fig.tight_layout()
    fig.savefig(config.FIGURES / "fig2_region.png", dpi=150); plt.close(fig)

    # 3. Portfolio concentration (Lorenz curve)
    s = df.sort_values(ach, ascending=False)[ach].values
    cum = s.cumsum() / s.sum()
    x = [i / len(s) for i in range(1, len(s) + 1)]
    fig, ax = plt.subplots(figsize=(6.0, 4))
    ax.plot([0, 1], [0, 1], "--", color="grey", lw=1, label="Perfectly even")
    ax.plot([0] + x, [0] + list(cum), color=BLUE, lw=2, label="AgriConnect")
    ax.fill_between([0] + x, [0] + list(cum), alpha=0.08, color=BLUE)
    ax.set_title("Outcome concentration across projects", fontweight="bold")
    ax.set_xlabel("Cumulative share of projects (largest first)")
    ax.set_ylabel("Cumulative share of beneficiaries")
    ax.text(0.35, 0.80, f"Top 5 projects = {res['top5_project_share_pct']:.0f}%\n"
            f"Top 20 projects = {res['top20_project_share_pct']:.0f}%",
            transform=ax.transAxes, fontweight="bold", color=BLUE)
    ax.legend(frameon=False, loc="lower right")
    _style(ax); fig.tight_layout()
    fig.savefig(config.FIGURES / "fig3_concentration.png", dpi=150); plt.close(fig)

    # 4. By global practice
    gp = df.groupby("global_practice")[ach].sum().sort_values(ascending=False).head(6)
    fig, ax = plt.subplots(figsize=(6.4, 4))
    ax.bar(gp.index, gp.values / 1e6, color=BLUE)
    ax.set_title("Beneficiaries by Global Practice", fontweight="bold")
    ax.set_ylabel("People (millions)")
    _style(ax); fig.tight_layout()
    fig.savefig(config.FIGURES / "fig4_practice.png", dpi=150); plt.close(fig)


def run() -> dict:
    df = load()
    res = compute(df)
    write_tables(df)
    make_figures(df, res)
    config.OUTPUTS.mkdir(parents=True, exist_ok=True)
    (config.OUTPUTS / "results_summary.json").write_text(json.dumps(res, indent=2))
    return res


if __name__ == "__main__":
    res = run()
    print(json.dumps(res, indent=2))
