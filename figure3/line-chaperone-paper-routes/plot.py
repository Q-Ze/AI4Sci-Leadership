"""Matplot Studio conversion of paper-level chaperone routes."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "line-chaperone-paper-routes",
    "name": "Chaperone paper routes",
    "description": "EWMA-smoothed shares of established, chaperoned, and independent AI4Sci paper routes.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original result table is embedded; the upstream database query is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Year", "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Share of classified AI4Sci papers", "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2024], "required": True},
    {"path": "axes.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0, 1], "required": True},
    {"path": "axes.x_tick_interval", "label": "X tick interval", "group": "Axes", "type": "number", "default": 10, "min": 1, "max": 30, "step": 1, "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "series.established.color", "label": "Established color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.chaperoned.color", "label": "Chaperoned color", "group": "Series", "type": "color", "default": "#7A5195", "required": True},
    {"path": "series.independent.color", "label": "Independent color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.line_width", "label": "Line width", "group": "Series", "type": "number", "default": 1.3, "min": 0.1, "max": 8, "step": 0.05, "required": True},
    {"path": "legend.labels", "label": "Legend labels", "group": "Legend", "type": "string_list", "default": ["Established: Domain Specialist-led", "Chaperoned: AI Specialist-led", "Independent: AI Specialist-led"], "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 6.8, "min": 4, "max": 24, "step": 0.1, "required": True},
    {"path": "legend.handle_length", "label": "Legend handle length", "group": "Legend", "type": "number", "default": 1.8, "min": 0, "max": 8, "step": 0.1, "required": True},
    {"path": "legend.label_spacing", "label": "Legend label spacing", "group": "Legend", "type": "number", "default": 0.3, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "legend.border_axes_pad", "label": "Legend axes padding", "group": "Legend", "type": "number", "default": 0.2, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [3.8, 2.4], "figure.facecolor": "#FFFFFF",
    "axes.x_label": "Year", "axes.y_label": "Share of classified AI4Sci papers",
    "axes.x_range": [1995, 2024], "axes.y_range": [0, 1],
    "axes.x_tick_interval": 10, "axes.grid": False, "axes.spine_width": 0.6,
    "series.established.color": "#D55E5E", "series.chaperoned.color": "#7A5195",
    "series.independent.color": "#3B6FB6", "series.line_width": 1.3,
    "legend.labels": ["Established: Domain Specialist-led", "Chaperoned: AI Specialist-led", "Independent: AI Specialist-led"],
    "legend.font_size": 6.8, "legend.handle_length": 1.8,
    "legend.label_spacing": 0.3, "legend.border_axes_pad": 0.2,
    "typography.font_family": "Arial", "typography.axis_label_size": 9,
    "typography.tick_label_size": 8, "typography.tick_width": 0.6,
    "typography.tick_length": 3,
}

_CSV_GZIP_B64 = "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"


def _typed_rows(csv_text):
    rows = list(csv.DictReader(StringIO(csv_text)))
    for row in rows:
        for key, value in row.items():
            try:
                row[key] = float(value) if "." in value else int(value)
            except ValueError:
                pass
    return rows


def prepare_data():
    return pd.DataFrame(_typed_rows(decompress(b64decode(_CSV_GZIP_B64)).decode("utf-8")))


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


def render(data, settings):
    s = _resolved(settings)
    keys = ["Established: Domain Specialist-led", "Chaperoned: AI Specialist-led", "Independent: AI Specialist-led"]
    labels = s["legend.labels"]
    colors = [s["series.established.color"], s["series.chaperoned.color"], s["series.independent.color"]]
    fig, ax = plt.subplots(figsize=s["figure.size"], facecolor=s["figure.facecolor"])
    for category, label, color in zip(keys, labels, colors):
        subset = data[data["category"] == category]
        ax.plot(subset["year"], subset["share_ewma5"], color=color,
                lw=s["series.line_width"], label=label)
    ax.set(xlabel=s["axes.x_label"], ylabel=s["axes.y_label"],
           xlim=s["axes.x_range"], ylim=s["axes.y_range"])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.xaxis.set_major_locator(MultipleLocator(s["axes.x_tick_interval"]))
    legend = ax.legend(frameon=False, fontsize=s["legend.font_size"],
                       handlelength=s["legend.handle_length"], labelspacing=s["legend.label_spacing"],
                       borderaxespad=s["legend.border_axes_pad"])
    ax.xaxis.label.set_size(s["typography.axis_label_size"])
    ax.yaxis.label.set_size(s["typography.axis_label_size"])
    ax.tick_params(labelsize=s["typography.tick_label_size"], direction="out",
                   width=s["typography.tick_width"], length=s["typography.tick_length"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for spine in ax.spines.values():
        spine.set_linewidth(s["axes.spine_width"])
    ax.grid(s["axes.grid"])
    for item in [ax.xaxis.label, ax.yaxis.label, *ax.get_xticklabels(), *ax.get_yticklabels(), *legend.get_texts()]:
        item.set_fontfamily(s["typography.font_family"])
    fig.tight_layout()
    return fig
