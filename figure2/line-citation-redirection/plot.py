"""Matplot Studio conversion of citation redirection."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "line-citation-redirection",
    "name": "Citation redirection",
    "description": "AI versus AI4Sci reference shares in Domain Specialist-led AI4Sci papers.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original result table is embedded; the upstream database query is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.8, 2.4], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Publication year", "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "text", "default": "Share within AI + AI4Sci\nreferences", "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2024], "required": True},
    {"path": "axes.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0, 1], "required": True},
    {"path": "axes.x_tick_interval", "label": "X tick interval", "group": "Axes", "type": "number", "default": 10, "min": 1, "max": 30, "step": 1, "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "series.ai.color", "label": "AI reference color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.ai4sci.color", "label": "AI4Sci reference color", "group": "Series", "type": "color", "default": "#7A5195", "required": True},
    {"path": "series.line_width", "label": "Line width", "group": "Series", "type": "number", "default": 1.3, "min": 0.1, "max": 8, "step": 0.05, "required": True},
    {"path": "reference.y", "label": "Reference level", "group": "Reference", "type": "number", "default": 0.5, "min": 0, "max": 1, "step": 0.05, "required": True},
    {"path": "reference.color", "label": "Reference color", "group": "Reference", "type": "color", "default": "#777777", "required": True},
    {"path": "reference.line_width", "label": "Reference width", "group": "Reference", "type": "number", "default": 0.7, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "reference.line_style", "label": "Reference style", "group": "Reference", "type": "select", "options": ["-", "--", ":", "-."], "default": "--", "required": True},
    {"path": "legend.labels", "label": "Legend labels", "group": "Legend", "type": "string_list", "default": ["AI references", "AI4Sci references"], "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.2, "min": 4, "max": 24, "step": 0.1, "required": True},
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
    "figure.size": [2.8, 2.4], "figure.facecolor": "#FFFFFF",
    "axes.x_label": "Publication year", "axes.y_label": "Share within AI + AI4Sci\nreferences",
    "axes.x_range": [1995, 2024], "axes.y_range": [0, 1], "axes.x_tick_interval": 10,
    "axes.grid": False, "axes.spine_width": 0.6,
    "series.ai.color": "#3B6FB6", "series.ai4sci.color": "#7A5195", "series.line_width": 1.3,
    "reference.y": 0.5, "reference.color": "#777777", "reference.line_width": 0.7,
    "reference.line_style": "--", "legend.labels": ["AI references", "AI4Sci references"],
    "legend.font_size": 7.2, "legend.handle_length": 1.8, "legend.label_spacing": 0.3,
    "legend.border_axes_pad": 0.2, "typography.font_family": "Arial",
    "typography.axis_label_size": 9, "typography.tick_label_size": 8,
    "typography.tick_width": 0.6, "typography.tick_length": 3,
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
    fig, ax = plt.subplots(figsize=s["figure.size"], facecolor=s["figure.facecolor"])
    labels = s["legend.labels"]
    ax.plot(data["year"], data["ai_share_ewma5"], color=s["series.ai.color"],
            lw=s["series.line_width"], label=labels[0])
    ax.plot(data["year"], data["ai4sci_share_ewma5"], color=s["series.ai4sci.color"],
            lw=s["series.line_width"], label=labels[1])
    ax.axhline(s["reference.y"], color=s["reference.color"],
               lw=s["reference.line_width"], ls=s["reference.line_style"])
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
