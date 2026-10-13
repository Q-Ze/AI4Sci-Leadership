"""Manuscript Figure 4C: citation impact around the Domain-active transition."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PLOT_META = {
    "id": "fig-4-c-bar-domain-active-transition-impact",
    "name": "Figure 4C — Domain-active transition",
    "description": "Mean citation percentiles before and after the first Domain-active to AI4Sci-active transition.",
    "version": 1, "data_mode": "inline",
    "data_note": "Final author-weighted category estimates and confidence intervals are embedded.",
    "data_export": {"csv": True, "json": True, "note": "Four category-level estimates with counts and uncertainty."},
}
PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 16, "step": 0.1, "required": True},
    {"path": "axes.main.title", "label": "Panel title", "group": "Axes", "type": "string", "default": "Domain-active → AI4Sci-active"},
    {"path": "axes.main.ylabel", "label": "Y label", "group": "Axes", "type": "string", "default": "Mean citation percentile"},
    {"path": "axes.main.y_range", "label": "Y range", "group": "Axes", "type": "number_pair", "default": [0, 0.8]},
    {"path": "series.bars.colors", "label": "Bar colors", "group": "Series", "type": "color_list", "default": ["#A6A6A6", "#D4A72C", "#B89AC9", "#009E73"]},
    {"path": "series.bars.width", "label": "Bar width", "group": "Series", "type": "number", "default": 0.66, "min": 0.05, "max": 0.95, "step": 0.01},
    {"path": "reference.lines.color", "label": "Guide color", "group": "Reference", "type": "color", "default": "#777777"},
    {"path": "postperiod.shading.color", "label": "Post-period shading", "group": "Reference", "type": "color", "default": "#009E73"},
    {"path": "postperiod.shading.alpha", "label": "Post-period alpha", "group": "Reference", "type": "number", "default": 0.055, "min": 0, "max": 1, "step": 0.005},
    {"path": "typography.title_size", "label": "Title size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5},
    {"path": "typography.tick_size", "label": "Tick size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5},
]
PLOT_SETTINGS = {
    "figure.size": [3.8, 2.4], "axes.main.title": "Domain-active → AI4Sci-active",
    "axes.main.ylabel": "Mean citation percentile", "axes.main.y_range": [0, 0.8],
    "series.bars.colors": ["#A6A6A6", "#D4A72C", "#B89AC9", "#009E73"],
    "series.bars.width": 0.66, "reference.lines.color": "#777777",
    "postperiod.shading.color": "#009E73", "postperiod.shading.alpha": 0.055,
    "typography.title_size": 9, "typography.tick_size": 8,
}
_DATA = [{'category': 'Pre-pivot source',
  'mean': 0.5998461789040089,
  'sd': 0.243908371425881,
  'n_authors': 93624,
  'n_papers': 1251599,
  'se': 0.0007971372616636,
  'ci95': 0.0015623890328607},
 {'category': 'Post-pivot source',
  'mean': 0.5755843949677104,
  'sd': 0.2462385437300179,
  'n_authors': 80021,
  'n_papers': 998083,
  'se': 0.0008704704785512,
  'ci95': 0.0017061221379605},
 {'category': 'Single-origin AI4Sci',
  'mean': 0.6319499584690258,
  'sd': 0.287630176123537,
  'n_authors': 66375,
  'n_papers': 218738,
  'se': 0.0011164317534632,
  'ci95': 0.0021882062367879},
 {'category': 'Cross-origin AI4Sci',
  'mean': 0.6690864033298447,
  'sd': 0.2565492700578639,
  'n_authors': 75891,
  'n_papers': 354531,
  'se': 0.000931270070339,
  'ci95': 0.0018252893378645}]


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


def prepare_data():
    return pd.DataFrame(_DATA)


def render(data, settings):
    cfg = _resolved(settings)
    categories = ["Pre-pivot source", "Post-pivot source", "Single-origin AI4Sci", "Cross-origin AI4Sci"]
    summary = data.set_index("category").loc[categories].reset_index()
    x = np.arange(len(summary))
    fig, ax = plt.subplots(figsize=cfg["figure.size"])
    ax.axvspan(0.5, 3.5, color=cfg["postperiod.shading.color"],
               alpha=cfg["postperiod.shading.alpha"], linewidth=0, zorder=0)
    ax.bar(x, summary["mean"], yerr=summary["ci95"], color=cfg["series.bars.colors"],
           width=cfg["series.bars.width"], edgecolor="none", capsize=2, error_kw={"lw": 0.7})
    before = float(summary.loc[summary["category"].eq("Pre-pivot source"), "mean"].iloc[0])
    ax.axvline(0.5, color=cfg["reference.lines.color"], lw=0.7, ls="--", zorder=2)
    ax.axhline(before, color=cfg["reference.lines.color"], lw=0.7, ls=":", zorder=3)
    ax.set_xticks(x, ["Pre-pivot\nDomain", "Post-pivot\nDomain",
                      "Single-origin\nAI4Sci", "Cross-origin\nAI4Sci"])
    ax.set(ylabel=cfg["axes.main.ylabel"], ylim=cfg["axes.main.y_range"],
           title=cfg["axes.main.title"])
    ax.title.set_fontsize(cfg["typography.title_size"])
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=cfg["typography.tick_size"], direction="out")
    ax.grid(False)
    fig.tight_layout()
    return fig

