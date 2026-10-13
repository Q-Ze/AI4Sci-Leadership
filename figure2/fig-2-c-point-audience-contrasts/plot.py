"""Manuscript Figure 2C: author-weighted citation-audience contrasts."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PLOT_META = {
    "id": "fig-2-c-point-audience-contrasts",
    "name": "Figure 2C — Citation-audience contrasts",
    "description": "Author-weighted outside-versus-home citation advantages with bootstrap confidence intervals.",
    "version": 1, "data_mode": "inline",
    "data_note": "The six final manuscript estimates and bootstrap intervals are embedded.",
    "data_export": {"csv": True, "json": True, "note": "Six tabular group-by-contrast estimates."},
}
PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.2, 2.4], "min": 1, "max": 16, "step": 0.1, "required": True},
    {"path": "axes.main.ylabel", "label": "Y label", "group": "Axes", "type": "text", "default": "Relative citation advantage\nof outside audience"},
    {"path": "axes.main.y_range", "label": "Y range", "group": "Axes", "type": "number_pair", "default": [-0.025, 0.62]},
    {"path": "series.ai.color", "label": "AI-led color", "group": "Series", "type": "color", "default": "#3B73B9"},
    {"path": "series.domain.color", "label": "Domain-led color", "group": "Series", "type": "color", "default": "#D95B59"},
    {"path": "series.points.marker_size", "label": "Marker size", "group": "Series", "type": "number", "default": 3.5, "min": 1, "max": 20, "step": 0.5},
    {"path": "series.points.linewidth", "label": "Error-bar width", "group": "Series", "type": "number", "default": 0.8, "min": 0.1, "max": 5, "step": 0.1},
    {"path": "reference.zero.color", "label": "Zero-line color", "group": "Reference", "type": "color", "default": "#777777"},
    {"path": "legend.visible", "label": "Show legend", "group": "Legend", "type": "boolean", "default": True},
    {"path": "typography.label_size", "label": "Label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5},
    {"path": "typography.tick_size", "label": "Tick size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5},
]
PLOT_SETTINGS = {
    "figure.size": [2.2, 2.4], "axes.main.ylabel": "Relative citation advantage\nof outside audience",
    "axes.main.y_range": [-0.025, 0.62], "series.ai.color": "#3B73B9", "series.domain.color": "#D95B59",
    "series.points.marker_size": 3.5, "series.points.linewidth": 0.8, "reference.zero.color": "#777777",
    "legend.visible": True, "typography.label_size": 9, "typography.tick_size": 8,
}
_DATA = [{'leader_class': 'AI',
  'contrast': 'All outside − home',
  'n_authors': 7567,
  'mean': 0.3555381342167886,
  'ci_low': 0.2863004739962218,
  'ci_high': 0.4176195304941852},
 {'leader_class': 'AI',
  'contrast': 'Outside w/o CS − home',
  'n_authors': 7567,
  'mean': 0.1351840543541091,
  'ci_low': 0.0671396857199002,
  'ci_high': 0.2003200856945107},
 {'leader_class': 'AI',
  'contrast': 'Computer Science − home',
  'n_authors': 7567,
  'mean': 0.5120388748812807,
  'ci_low': 0.4339014516337233,
  'ci_high': 0.584419276143215},
 {'leader_class': 'Domain',
  'contrast': 'All outside − home',
  'n_authors': 12818,
  'mean': 0.1633096330164981,
  'ci_low': 0.1040440941145986,
  'ci_high': 0.2186992662729981},
 {'leader_class': 'Domain',
  'contrast': 'Outside w/o CS − home',
  'n_authors': 12818,
  'mean': 0.2757902801024091,
  'ci_low': 0.2163363108264282,
  'ci_high': 0.3345332479594553},
 {'leader_class': 'Domain',
  'contrast': 'Computer Science − home',
  'n_authors': 12818,
  'mean': 0.0968137422905719,
  'ci_low': 0.0377886010874576,
  'ci_high': 0.1576244470078369}]


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


def prepare_data():
    return pd.DataFrame(_DATA)


def render(data, settings):
    cfg = _resolved(settings)
    order = ["All outside − home", "Outside w/o CS − home", "Computer Science − home"]
    x = np.arange(len(order))
    fig, ax = plt.subplots(figsize=cfg["figure.size"])
    for leader, offset, label, color_path in [
        ("AI", -0.06, "AI-led", "series.ai.color"),
        ("Domain", 0.06, "Domain-led", "series.domain.color"),
    ]:
        subset = data.loc[data["leader_class"].eq(leader)].set_index("contrast").loc[order]
        mean = subset["mean"].to_numpy()
        error = np.vstack([mean - subset["ci_low"].to_numpy(), subset["ci_high"].to_numpy() - mean])
        ax.errorbar(x + offset, mean, yerr=error, fmt="o",
                    markersize=cfg["series.points.marker_size"],
                    lw=cfg["series.points.linewidth"], capsize=2,
                    color=cfg[color_path], label=label)
    ax.axhline(0, color=cfg["reference.zero.color"], lw=0.7, ls="--")
    ax.set_xticks(x, ["All\noutside", "Outside\nw/o CS", "Computer\nScience"])
    ax.set(xlim=(-0.22, 2.36), ylim=cfg["axes.main.y_range"], ylabel=cfg["axes.main.ylabel"])
    ax.set_yticks([0, 0.2, 0.4, 0.6])
    if cfg["legend.visible"]:
        ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.02),
                  ncol=2, borderaxespad=0, handlelength=0.8, handletextpad=0.35, fontsize=7.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha="right")
    ax.tick_params(labelsize=cfg["typography.tick_size"], direction="out")
    ax.yaxis.label.set_size(cfg["typography.label_size"])
    ax.grid(False)
    fig.tight_layout()
    return fig

