"""Matplot Studio alternative for Figure 4a using raw citation amounts."""

from csv import DictReader
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
import pandas as pd


PLOT_META = {
    "id": "fig-4-a-citation-audience-amount",
    "name": "Figure 4a — Citation audience amount",
    "description": "Raw AI- and Domain-origin citation-edge counts to AI4Sci papers across historical JCR quartiles, shown on a logarithmic axis.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "Complete Q1–Q4 citation-edge counts. AI4Sci citing papers are excluded. Targets are 1998–2024 AI4Sci papers assigned publication-year-minus-one historical JCR quartiles.",
    "data_export": {"csv": True, "json": True, "note": "Complete embedded raw-count table."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.80, 2.40], "min": 1.5, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.main.title", "label": "Title", "group": "Axes", "type": "string", "default": "", "required": True},
    {"path": "axes.main.title_size", "label": "Title size", "group": "Axes", "type": "number", "default": 9, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "axes.main.title_pad", "label": "Title padding", "group": "Axes", "type": "number", "default": 4, "min": 0, "max": 30, "step": 0.5, "required": True},
    {"path": "axes.main.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "JCR quartile", "required": True},
    {"path": "axes.main.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Number of citation edges", "required": True},
    {"path": "axes.main.x_labels", "label": "Quartile labels", "group": "Axes", "type": "string_list", "default": ["Q1", "Q2", "Q3", "Q4"], "required": True},
    {"path": "axes.main.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [-0.45, 3.45], "min": -2, "max": 6, "step": 0.05, "required": True},
    {"path": "axes.main.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [50000, 4000000], "min": 1, "max": 10000000, "step": 10000, "required": True},
    {"path": "axes.main.y_scale", "label": "Y-axis scale", "group": "Axes", "type": "select", "default": "log", "options": ["log", "linear"], "required": True},
    {"path": "axes.main.y_log_base", "label": "Log base", "group": "Axes", "type": "number", "default": 10, "min": 2, "max": 20, "step": 1, "required": True},
    {"path": "axes.main.y_tick_step", "label": "Linear Y tick interval", "group": "Axes", "type": "number", "default": 500000, "min": 1000, "max": 5000000, "step": 1000, "required": True},
    {"path": "axes.main.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 3, "step": 0.1, "required": True},
    {"path": "axes.main.tick_length", "label": "Tick length", "group": "Axes", "type": "number", "default": 3, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "connector.color", "label": "Connector color", "group": "Connectors", "type": "color", "default": "#B8B8B8", "required": True},
    {"path": "connector.linewidth", "label": "Connector width", "group": "Connectors", "type": "number", "default": 0.8, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "series.ai.color", "label": "AI color", "group": "Points", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.domain.color", "label": "Domain color", "group": "Points", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.marker_shape", "label": "Point shape", "group": "Points", "type": "select", "default": "o", "options": ["o", "s", "D", "^", "v", "X"], "required": True},
    {"path": "series.marker_size", "label": "Point area", "group": "Points", "type": "number", "default": 25, "min": 1, "max": 200, "step": 1, "required": True},
    {"path": "legend.ai_label", "label": "AI legend label", "group": "Legend", "type": "string", "default": "From AI papers", "required": True},
    {"path": "legend.domain_label", "label": "Domain legend label", "group": "Legend", "type": "string", "default": "From Domain papers", "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "default": "upper right", "options": ["upper right", "upper left", "lower right", "lower left", "best"], "required": True},
    {"path": "legend.columns", "label": "Legend columns", "group": "Legend", "type": "integer", "default": 2, "min": 1, "max": 4, "step": 1, "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.2, "min": 4, "max": 16, "step": 0.1, "required": True},
    {"path": "legend.frame", "label": "Legend frame", "group": "Legend", "type": "boolean", "default": False, "required": True},
    {"path": "legend.handle_text_pad", "label": "Handle-text gap", "group": "Legend", "type": "number", "default": 0.4, "min": 0, "max": 2, "step": 0.05, "required": True},
    {"path": "legend.column_spacing", "label": "Column spacing", "group": "Legend", "type": "number", "default": 0.9, "min": 0, "max": 3, "step": 0.1, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.label_size", "label": "Axis-label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "typography.tick_size", "label": "Tick-label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 20, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {'figure.size': [3.8, 2.4],
 'figure.facecolor': '#FFFFFF',
 'axes.main.title': '',
 'axes.main.title_size': 9,
 'axes.main.title_pad': 4,
 'axes.main.x_label': 'JCR quartile',
 'axes.main.y_label': 'Number of citation edges',
 'axes.main.x_labels': ['Q1', 'Q2', 'Q3', 'Q4'],
 'axes.main.x_range': [-0.45, 3.45],
 'axes.main.y_range': [50000, 4000000],
 'axes.main.y_scale': 'log',
 'axes.main.y_log_base': 10,
 'axes.main.y_tick_step': 500000,
 'axes.main.spine_width': 0.6,
 'axes.main.tick_length': 3,
 'connector.color': '#B8B8B8',
 'connector.linewidth': 0.8,
 'series.ai.color': '#3B6FB6',
 'series.domain.color': '#D55E5E',
 'series.marker_shape': 'o',
 'series.marker_size': 25,
 'legend.ai_label': 'From AI papers',
 'legend.domain_label': 'From Domain papers',
 'legend.location': 'upper right',
 'legend.columns': 1,
 'legend.font_size': 7.2,
 'legend.frame': False,
 'legend.handle_text_pad': 0.4,
 'legend.column_spacing': 0.9,
 'typography.font_family': 'Arial',
 'typography.label_size': 9,
 'typography.tick_size': 8}

ORDER = ["Q1", "Q2", "Q3", "Q4"]

_CSV_DATA = """jcr,AI,Domain,n_ai_domain
Q1,1437466,2918674,4356140
Q2,300718,662977,963695
Q3,117156,238309,355465
Q4,65634,105494,171128
"""


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


def prepare_data():
    rows = []
    for row in DictReader(StringIO(_CSV_DATA)):
        rows.append({"jcr": row["jcr"], "AI": int(row["AI"]),
                     "Domain": int(row["Domain"]),
                     "n_ai_domain": int(row["n_ai_domain"])})
    return pd.DataFrame(rows)


def render(data, settings):
    c = _resolved(settings)
    style = {
        "font.family": c["typography.font_family"], "font.size": 8,
        "axes.labelsize": c["typography.label_size"],
        "xtick.labelsize": c["typography.tick_size"],
        "ytick.labelsize": c["typography.tick_size"],
        "legend.fontsize": c["legend.font_size"],
        "axes.linewidth": c["axes.main.spine_width"],
        "xtick.major.width": c["axes.main.spine_width"],
        "ytick.major.width": c["axes.main.spine_width"],
        "xtick.major.size": c["axes.main.tick_length"],
        "ytick.major.size": c["axes.main.tick_length"],
    }
    with plt.rc_context(style):
        return _draw(data, c)


def _draw(data, c):
    plot_data = data.set_index("jcr").reindex(ORDER)
    ai = plot_data["AI"].to_numpy(dtype=float)
    domain = plot_data["Domain"].to_numpy(dtype=float)
    x = np.arange(len(ORDER))
    fig, ax = plt.subplots(figsize=tuple(c["figure.size"]), facecolor=c["figure.facecolor"])
    ax.set_facecolor(c["figure.facecolor"])
    for index in range(len(ORDER)):
        ax.plot([index, index], [ai[index], domain[index]],
                color=c["connector.color"], lw=c["connector.linewidth"], zorder=1)
    ax.scatter(x, ai, s=c["series.marker_size"], marker=c["series.marker_shape"],
               color=c["series.ai.color"], label=c["legend.ai_label"], zorder=3)
    ax.scatter(x, domain, s=c["series.marker_size"], marker=c["series.marker_shape"],
               color=c["series.domain.color"], label=c["legend.domain_label"], zorder=3)
    labels = c["axes.main.x_labels"]
    if len(labels) != len(ORDER):
        raise ValueError("Quartile labels must contain exactly four entries")
    ax.set_xticks(x, labels)
    ax.set_xlim(*c["axes.main.x_range"])
    if c["axes.main.y_scale"] == "log":
        ax.set_yscale("log", base=c["axes.main.y_log_base"])
    else:
        ax.set_yscale("linear")
    ax.set_ylim(*c["axes.main.y_range"])
    if c["axes.main.y_scale"] == "linear":
        ax.yaxis.set_major_locator(MultipleLocator(c["axes.main.y_tick_step"]))
    if c["axes.main.title"]:
        ax.set_title(c["axes.main.title"], family=c["typography.font_family"],
                     fontsize=c["axes.main.title_size"], pad=c["axes.main.title_pad"])
    ax.set_xlabel(c["axes.main.x_label"], family=c["typography.font_family"],
                  fontsize=c["typography.label_size"])
    ax.set_ylabel(c["axes.main.y_label"], family=c["typography.font_family"],
                  fontsize=c["typography.label_size"])
    legend = ax.legend(frameon=c["legend.frame"], fontsize=c["legend.font_size"],
                       ncol=c["legend.columns"], loc=c["legend.location"],
                       handletextpad=c["legend.handle_text_pad"],
                       columnspacing=c["legend.column_spacing"])
    for text in legend.get_texts():
        text.set_fontfamily(c["typography.font_family"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(c["axes.main.spine_width"])
    ax.spines["bottom"].set_linewidth(c["axes.main.spine_width"])
    ax.tick_params(direction="out", labelsize=c["typography.tick_size"],
                   width=c["axes.main.spine_width"], length=c["axes.main.tick_length"])
    for tick in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        tick.set_fontfamily(c["typography.font_family"])
    ax.grid(False)
    fig.tight_layout()
    return fig
