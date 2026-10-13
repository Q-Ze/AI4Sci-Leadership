"""Manuscript Figure 4D: citation impact around the AI-active transition."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PLOT_META = {
    "id": "fig-4-d-bar-ai-active-transition-impact",
    "name": "Figure 4D — AI-active transition",
    "description": "Mean citation percentiles before and after the first AI-active to AI4Sci-active transition.",
    "version": 1, "data_mode": "inline",
    "data_note": "Final author-weighted category estimates and confidence intervals are embedded.",
    "data_export": {"csv": True, "json": True, "note": "Four category-level estimates with counts and uncertainty."},
}
PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 16, "step": 0.1, "required": True},
    {"path": "axes.main.title", "label": "Panel title", "group": "Axes", "type": "string", "default": "AI-active → AI4Sci-active"},
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
    "figure.size": [3.8, 2.4], "axes.main.title": "AI-active → AI4Sci-active",
    "axes.main.ylabel": "Mean citation percentile", "axes.main.y_range": [0, 0.8],
    "series.bars.colors": ["#A6A6A6", "#D4A72C", "#B89AC9", "#009E73"],
    "series.bars.width": 0.66, "reference.lines.color": "#777777",
    "postperiod.shading.color": "#009E73", "postperiod.shading.alpha": 0.055,
    "typography.title_size": 9, "typography.tick_size": 8,
}
_DATA = [{'category': 'Pre-pivot source',
  'mean': 0.6449950724360618,
  'sd': 0.2372590472601493,
  'n_authors': 42776,
  'n_papers': 362025,
  'se': 0.0011471565694973,
  'ci95': 0.0022484268762148},
 {'category': 'Post-pivot source',
  'mean': 0.5517404349042246,
  'sd': 0.2593913693976747,
  'n_authors': 34786,
  'n_papers': 392586,
  'se': 0.0013907634722146,
  'ci95': 0.0027258964055407},
 {'category': 'Single-origin AI4Sci',
  'mean': 0.6391692463438764,
  'sd': 0.2706396364949345,
  'n_authors': 28483,
  'n_papers': 112229,
  'se': 0.0016036091902988,
  'ci95': 0.0031430740129856},
 {'category': 'Cross-origin AI4Sci',
  'mean': 0.6798106239019801,
  'sd': 0.2284467120742986,
  'n_authors': 39140,
  'n_papers': 263839,
  'se': 0.0011547141857315,
  'ci95': 0.0022632398040337}]


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
    ax.set_xticks(x, ["Pre-pivot\nAI", "Post-pivot\nAI",
                      "Single-origin\nAI4Sci", "Cross-origin\nAI4Sci"])
    ax.set(ylabel=cfg["axes.main.ylabel"], ylim=cfg["axes.main.y_range"],
           title=cfg["axes.main.title"])
    ax.title.set_fontsize(cfg["typography.title_size"])
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=cfg["typography.tick_size"], direction="out")
    ax.grid(False)
    fig.tight_layout()
    return fig

