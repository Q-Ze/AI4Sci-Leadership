"""Matplot Studio conversion of annual active-role shares."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "area-annual-active-role-shares",
    "name": "Annual active-role shares",
    "description": "EWMA-smoothed composition of active roles among annual AI4Sci participants.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original result table is embedded; the upstream database query is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.45, 2.15], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Year", "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Share of AI4Sci participants", "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2024], "required": True},
    {"path": "axes.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0, 1], "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.top_spine", "label": "Show top spine", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.right_spine", "label": "Show right spine", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "series.colors", "label": "Role colors", "group": "Series", "type": "color_list", "default": ["#3B6FB6", "#7A5195", "#D55E5E"], "required": True},
    {"path": "series.alpha", "label": "Area opacity", "group": "Series", "type": "number", "default": 0.88, "min": 0, "max": 1, "step": 0.01, "required": True},
    {"path": "series.edge_color", "label": "Edge color", "group": "Series", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "series.line_width", "label": "Edge width", "group": "Series", "type": "number", "default": 0.35, "min": 0, "max": 5, "step": 0.05, "required": True},
    {"path": "legend.labels", "label": "Legend labels", "group": "Legend", "type": "string_list", "default": ["AI-active", "AI4Sci-active", "Domain-active"], "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "options": ["upper left", "upper right", "lower left", "lower right", "best"], "default": "upper left", "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7, "min": 4, "max": 24, "step": 0.1, "required": True},
    {"path": "legend.facecolor", "label": "Legend background", "group": "Legend", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "legend.frame_alpha", "label": "Legend opacity", "group": "Legend", "type": "number", "default": 0.88, "min": 0, "max": 1, "step": 0.01, "required": True},
    {"path": "legend.label_spacing", "label": "Legend label spacing", "group": "Legend", "type": "number", "default": 0.25, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "legend.border_axes_pad", "label": "Legend axes padding", "group": "Legend", "type": "number", "default": 0.2, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "legend.handle_length", "label": "Legend handle length", "group": "Legend", "type": "number", "default": 1.5, "min": 0, "max": 8, "step": 0.1, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [2.45, 2.15], "figure.facecolor": "#FFFFFF",
    "axes.x_label": "Year", "axes.y_label": "Share of AI4Sci participants",
    "axes.x_range": [1995, 2024], "axes.y_range": [0, 1], "axes.grid": False,
    "axes.top_spine": False, "axes.right_spine": False, "axes.spine_width": 0.6,
    "series.colors": ["#3B6FB6", "#7A5195", "#D55E5E"], "series.alpha": 0.88,
    "series.edge_color": "#FFFFFF", "series.line_width": 0.35,
    "legend.labels": ["AI-active", "AI4Sci-active", "Domain-active"],
    "legend.location": "upper left", "legend.font_size": 7,
    "legend.facecolor": "#FFFFFF", "legend.frame_alpha": 0.88,
    "legend.label_spacing": 0.25, "legend.border_axes_pad": 0.2,
    "legend.handle_length": 1.5, "typography.font_family": "Arial",
    "typography.axis_label_size": 9, "typography.tick_label_size": 8,
    "typography.tick_width": 0.6, "typography.tick_length": 3,
}

_CSV_GZIP_B64 = "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"


def prepare_data():
    return pd.DataFrame(_typed_rows(decompress(b64decode(_CSV_GZIP_B64)).decode("utf-8")))


def _typed_rows(csv_text):
    rows = list(csv.DictReader(StringIO(csv_text)))
    for row in rows:
        for key, value in row.items():
            try:
                row[key] = float(value) if "." in value else int(value)
            except ValueError:
                pass
    return rows


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


def render(data, settings):
    s = _resolved(settings)
    fig, ax = plt.subplots(figsize=s["figure.size"], facecolor=s["figure.facecolor"])
    ax.stackplot(data["year"], data["AI_ewma5"], data["AI4Sci_ewma5"], data["Domain_ewma5"],
                 labels=s["legend.labels"], colors=s["series.colors"], alpha=s["series.alpha"],
                 edgecolor=s["series.edge_color"], linewidth=s["series.line_width"])
    ax.set(xlabel=s["axes.x_label"], ylabel=s["axes.y_label"],
           xlim=s["axes.x_range"], ylim=s["axes.y_range"])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    legend = ax.legend(frameon=True, facecolor=s["legend.facecolor"], edgecolor="none",
                       framealpha=s["legend.frame_alpha"], fontsize=s["legend.font_size"],
                       loc=s["legend.location"], labelspacing=s["legend.label_spacing"],
                       borderaxespad=s["legend.border_axes_pad"], handlelength=s["legend.handle_length"])
    ax.xaxis.label.set_size(s["typography.axis_label_size"])
    ax.yaxis.label.set_size(s["typography.axis_label_size"])
    ax.tick_params(labelsize=s["typography.tick_label_size"], direction="out",
                   width=s["typography.tick_width"], length=s["typography.tick_length"])
    ax.spines["top"].set_visible(s["axes.top_spine"])
    ax.spines["right"].set_visible(s["axes.right_spine"])
    for spine in ax.spines.values():
        spine.set_linewidth(s["axes.spine_width"])
    ax.grid(s["axes.grid"])
    for item in [ax.xaxis.label, ax.yaxis.label, *ax.get_xticklabels(), *ax.get_yticklabels(), *legend.get_texts()]:
        item.set_fontfamily(s["typography.font_family"])
    fig.tight_layout()
    return fig
