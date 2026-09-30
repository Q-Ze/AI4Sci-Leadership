"""Matplot Studio conversion of JCR-stratified last-author shares."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "line-jcr-last-author-share",
    "name": "AI Specialist last-author share by JCR quartile",
    "description": "EWMA-smoothed AI Specialist last-author share for JCR quartiles Q1–Q4.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original result table is embedded; the upstream database query is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.5, 2.8], "min": 1, "max": 12, "step": 0.1, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Year", "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "AI Specialist last-author share", "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2024], "required": True},
    {"path": "axes.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0.15, 0.5], "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.top_spine", "label": "Show top spine", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.right_spine", "label": "Show right spine", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "series.q1.color", "label": "Q1 color", "group": "Series", "type": "color", "default": "#440154", "required": True},
    {"path": "series.q2.color", "label": "Q2 color", "group": "Series", "type": "color", "default": "#31688E", "required": True},
    {"path": "series.q3.color", "label": "Q3 color", "group": "Series", "type": "color", "default": "#35B779", "required": True},
    {"path": "series.q4.color", "label": "Q4 color", "group": "Series", "type": "color", "default": "#FDE725", "required": True},
    {"path": "series.line_width", "label": "Line width", "group": "Series", "type": "number", "default": 1.25, "min": 0.1, "max": 8, "step": 0.05, "required": True},
    {"path": "legend.title", "label": "Legend title", "group": "Legend", "type": "string", "default": "JCR", "required": True},
    {"path": "legend.columns", "label": "Legend columns", "group": "Legend", "type": "integer", "default": 2, "min": 1, "max": 4, "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.2, "min": 4, "max": 24, "step": 0.1, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [3.5, 2.8], "figure.facecolor": "#FFFFFF",
    "axes.x_label": "Year", "axes.y_label": "AI Specialist last-author share",
    "axes.x_range": [1995, 2024], "axes.y_range": [0.15, 0.5], "axes.grid": False,
    "axes.top_spine": False, "axes.right_spine": False, "axes.spine_width": 0.6,
    "series.q1.color": "#440154", "series.q2.color": "#31688E",
    "series.q3.color": "#35B779", "series.q4.color": "#FDE725",
    "series.line_width": 1.25, "legend.title": "JCR", "legend.columns": 2,
    "legend.font_size": 7.2, "typography.font_family": "Arial",
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
    quartiles = [("Q1", s["series.q1.color"]), ("Q2", s["series.q2.color"]),
                 ("Q3", s["series.q3.color"]), ("Q4", s["series.q4.color"])]
    for quartile, color in quartiles:
        subset = data[data["jcr"] == quartile]
        ax.plot(subset["year"], subset["ai_specialist_share_ewma5"],
                color=color, lw=s["series.line_width"], label=quartile)
    ax.set(xlabel=s["axes.x_label"], ylabel=s["axes.y_label"],
           xlim=s["axes.x_range"], ylim=s["axes.y_range"])
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    legend = ax.legend(frameon=False, ncol=s["legend.columns"], title=s["legend.title"],
                       fontsize=s["legend.font_size"])
    ax.xaxis.label.set_size(s["typography.axis_label_size"])
    ax.yaxis.label.set_size(s["typography.axis_label_size"])
    ax.tick_params(labelsize=s["typography.tick_label_size"], direction="out",
                   width=s["typography.tick_width"], length=s["typography.tick_length"])
    ax.spines["top"].set_visible(s["axes.top_spine"])
    ax.spines["right"].set_visible(s["axes.right_spine"])
    for spine in ax.spines.values():
        spine.set_linewidth(s["axes.spine_width"])
    ax.grid(s["axes.grid"])
    for item in [ax.xaxis.label, ax.yaxis.label, legend.get_title(), *ax.get_xticklabels(), *ax.get_yticklabels(), *legend.get_texts()]:
        item.set_fontfamily(s["typography.font_family"])
    fig.tight_layout()
    return fig
