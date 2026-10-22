"""Matplot Studio figure for Figure 3e: Top 10% Foundation share."""

from __future__ import annotations

from csv import DictReader
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd


PLOT_META = {
    "id": "fig-3-b-top10-foundation-by-route",
    "name": "Figure 3b — Top 10% Foundation share by route",
    "description": "Share of papers in the field-year top 10% of the one-year-window Foundation index, by last-author route, with naive 95% confidence intervals.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "Complete group summary for the ever-exposed route specification.",
    "data_export": {"csv": True, "json": True, "note": "Complete embedded group summary."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.45, 2.15], "min": 1.5, "max": 12, "step": 0.01, "required": True},
    {"path": "figure.facecolor", "label": "Background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.main.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Top 10% Foundation share", "required": True},
    {"path": "axes.main.y_percent_decimals", "label": "Y tick decimals", "group": "Axes", "type": "integer", "default": 1, "min": 0, "max": 3, "step": 1, "required": True},
    {"path": "axes.main.category_labels", "label": "Category labels", "group": "Axes", "type": "string_list", "default": ["Domain", "Chaperoned\nAI", "Independent\nAI"], "required": True},
    {"path": "axes.main.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 3, "step": 0.1, "required": True},
    {"path": "axes.main.tick_length", "label": "Tick length", "group": "Axes", "type": "number", "default": 3, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "series.domain.color", "label": "Domain color", "group": "Points", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.chaperoned.color", "label": "Chaperoned AI color", "group": "Points", "type": "color", "default": "#7A5195", "required": True},
    {"path": "series.independent.color", "label": "Independent AI color", "group": "Points", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.marker", "label": "Point shape", "group": "Points", "type": "select", "default": "o", "options": ["o", "s", "D", "^", "v", "X"], "required": True},
    {"path": "series.marker_size", "label": "Point area", "group": "Points", "type": "number", "default": 28, "min": 1, "max": 200, "step": 1, "required": True},
    {"path": "errorbar.color", "label": "Error-bar color", "group": "Confidence intervals", "type": "color", "default": "#333333", "required": True},
    {"path": "errorbar.linewidth", "label": "Error-bar width", "group": "Confidence intervals", "type": "number", "default": 0.8, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "errorbar.capsize", "label": "Cap size", "group": "Confidence intervals", "type": "number", "default": 2, "min": 0, "max": 15, "step": 0.5, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.label_size", "label": "Axis-label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "typography.tick_size", "label": "Tick-label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 20, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {'figure.size': [3.8, 1.6],
 'figure.facecolor': '#FFFFFF',
 'axes.main.y_label': 'Percent of top 10%  F',
 'axes.main.y_percent_decimals': 1,
 'axes.main.category_labels': ['Domain-led', 'Chaperoned AI-led', 'Independent AI-led'],
 'axes.main.spine_width': 0.6,
 'axes.main.tick_length': 3,
 'series.domain.color': '#D55E5E',
 'series.chaperoned.color': '#7A5195',
 'series.independent.color': '#3B6FB6',
 'series.marker': 'o',
 'series.marker_size': 28,
 'errorbar.color': '#333333',
 'errorbar.linewidth': 0.8,
 'errorbar.capsize': 2,
 'typography.font_family': 'Arial',
 'typography.label_size': 9,
 'typography.tick_size': 8}

GROUPS = ["Domain-led", "Chaperoned AI-led", "Independent AI-led"]


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


_CSV_DATA = """specification,group,outcome,estimate,se_naive,ci_low_naive,ci_high_naive,n_papers,n_outcome,n_leaders
ever-exposed route,Domain-led,Top 10% Foundation share,0.09974356707047484,0.0006641685037911938,0.0984417968030441,0.10104533733790558,203632,203562,104980
ever-exposed route,Chaperoned AI-led,Top 10% Foundation share,0.09138851071154719,0.0011399286963026509,0.089154250466794,0.09362277095630038,63911,63903,16678
ever-exposed route,Independent AI-led,Top 10% Foundation share,0.10807329261521377,0.0014631934147174817,0.10520543352236751,0.11094115170806003,45038,45025,31327
"""


def prepare_data():
    rows = []
    for row in DictReader(StringIO(_CSV_DATA)):
        if not row or "group" not in row:
            continue
        rows.append({
            "specification": row["specification"], "group": row["group"],
            "outcome": row["outcome"], "estimate": float(row["estimate"]),
            "se_naive": float(row["se_naive"]),
            "ci_low_naive": float(row["ci_low_naive"]),
            "ci_high_naive": float(row["ci_high_naive"]),
            "n_papers": int(row["n_papers"]), "n_outcome": int(row["n_outcome"]),
            "n_leaders": int(row["n_leaders"]),
        })
    return pd.DataFrame(rows)


def render(data, settings):
    c = _resolved(settings)
    style = {
        "font.family": c["typography.font_family"], "font.size": 8,
        "axes.labelsize": c["typography.label_size"],
        "xtick.labelsize": c["typography.tick_size"],
        "ytick.labelsize": c["typography.tick_size"],
        "axes.linewidth": c["axes.main.spine_width"],
        "xtick.major.width": c["axes.main.spine_width"],
        "ytick.major.width": c["axes.main.spine_width"],
        "xtick.major.size": c["axes.main.tick_length"],
        "ytick.major.size": c["axes.main.tick_length"],
    }
    with plt.rc_context(style):
        ordered = data.set_index("group").loc[GROUPS]
        x = np.arange(len(GROUPS))
        fig, ax = plt.subplots(figsize=tuple(c["figure.size"]), facecolor=c["figure.facecolor"])
        ax.set_facecolor(c["figure.facecolor"])
        ax.errorbar(
            x, ordered.estimate, yerr=1.96 * ordered.se_naive,
            fmt="none", ecolor=c["errorbar.color"],
            elinewidth=c["errorbar.linewidth"], capsize=c["errorbar.capsize"], zorder=1,
        )
        colors = [c["series.domain.color"], c["series.chaperoned.color"], c["series.independent.color"]]
        ax.scatter(x, ordered.estimate, s=c["series.marker_size"], marker=c["series.marker"], color=colors, zorder=2)
        labels = c["axes.main.category_labels"]
        if len(labels) != len(GROUPS):
            raise ValueError("Category labels must contain exactly three entries")
        ax.set_xticks(x, labels)
        ax.set_xlim([-0.45,2.45])
        ax.set_ylabel(c["axes.main.y_label"], family=c["typography.font_family"], fontsize=c["typography.label_size"])
        ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=c["axes.main.y_percent_decimals"]))
        ax.tick_params(direction="out", labelsize=c["typography.tick_size"], width=c["axes.main.spine_width"], length=c["axes.main.tick_length"])
        for tick in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
            tick.set_fontfamily(c["typography.font_family"])
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines["left"].set_linewidth(c["axes.main.spine_width"])
        ax.spines["bottom"].set_linewidth(c["axes.main.spine_width"])
        ax.grid(False)
        fig.tight_layout()
        return fig
