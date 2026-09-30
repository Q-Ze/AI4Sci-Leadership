"""Matplot Studio conversion of an author-level pivot chart."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PLOT_META = {
    "id": "bar-pivot-active-ai-to-ai4sci",
    "name": "AI-active to AI4Sci-active pivot",
    "description": "Author-level mean citation percentile around the first AI-active to AI4Sci-active transition.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original four-category summary is embedded; the large author-level intermediate table is not required for rendering.",
    "data_export": {"csv": True, "json": True, "note": "Embedded plotted summary with confidence intervals."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.title", "label": "Title", "group": "Axes", "type": "string", "default": "AI-active → AI4Sci-active", "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Mean citation percentile", "required": True},
    {"path": "axes.x_tick_labels", "label": "Category labels", "group": "Axes", "type": "string_list", "default": ["Pre-pivot\nAI", "Post-pivot\nAI", "Single-origin\nAI4Sci", "Cross-origin\nAI4Sci"], "required": True},
    {"path": "axes.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0, 0.8], "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "bars.colors", "label": "Category colors", "group": "Bars", "type": "color_list", "default": ["#A6A6A6", "#D4A72C", "#B89AC9", "#7A5195"], "required": True},
    {"path": "bars.width", "label": "Bar width", "group": "Bars", "type": "number", "default": 0.66, "min": 0.1, "max": 1, "step": 0.01, "required": True},
    {"path": "bars.cap_size", "label": "Error-bar cap size", "group": "Bars", "type": "number", "default": 2, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "bars.error_line_width", "label": "Error-bar width", "group": "Bars", "type": "number", "default": 0.7, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "phase.color", "label": "Post-pivot shading", "group": "Phase", "type": "color", "default": "#7A5195", "required": True},
    {"path": "phase.alpha", "label": "Post-pivot opacity", "group": "Phase", "type": "number", "default": 0.055, "min": 0, "max": 1, "step": 0.005, "required": True},
    {"path": "reference.color", "label": "Reference color", "group": "Reference", "type": "color", "default": "#777777", "required": True},
    {"path": "reference.line_width", "label": "Reference width", "group": "Reference", "type": "number", "default": 0.7, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.title_size", "label": "Title size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.title_pad", "label": "Title padding", "group": "Typography", "type": "number", "default": 7, "min": 0, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [3.8, 2.4], "figure.facecolor": "#FFFFFF",
    "axes.title": "AI-active → AI4Sci-active", "axes.y_label": "Mean citation percentile",
    "axes.x_tick_labels": ["Pre-pivot\nAI", "Post-pivot\nAI", "Single-origin\nAI4Sci", "Cross-origin\nAI4Sci"],
    "axes.y_range": [0, 0.8], "axes.grid": False, "axes.spine_width": 0.6,
    "bars.colors": ["#A6A6A6", "#D4A72C", "#B89AC9", "#7A5195"],
    "bars.width": 0.66, "bars.cap_size": 2, "bars.error_line_width": 0.7,
    "phase.color": "#7A5195", "phase.alpha": 0.055,
    "reference.color": "#777777", "reference.line_width": 0.7,
    "typography.font_family": "Arial", "typography.title_size": 9,
    "typography.title_pad": 7, "typography.axis_label_size": 9,
    "typography.tick_label_size": 8, "typography.tick_width": 0.6, "typography.tick_length": 3,
}

_CSV_GZIP_B64 = "H4sIAAAAAAAAA2WQS2rDQBBE9zqFDzAO/f8sQ1bZGXyAYBzhCBLLSHIgt0/L9irZDE0x3a+qjoelP43TT/vqD+c2v7fz2+G6fIzTXNPlcOlrmPt2HFK73dRvL8P3uGzm8Tod+wZPJpKp4CRsYBglETtpgjgZoCRTE3K3xkZAWh8AEMVRTS0lndX4phJJCFm4EUpgdLtxXv4CVdEFhKUItWArUJMT2ep1c/HG4lG8JA278zjBrWSqy6ZwV6l8RpqAqkD56fbD+fTZb8dpOA3nzfOr7I/DmrGuWxaLhcucrEiHUo1NKgGLNgoJbohElHekQTWSmEAZQTeNURjKPZaklZO6l2mc5/9Az0AwKteYAbgCCyDmSLVf22s6FGhkHPwAolapgqHOqJXt0alx3QkQYPZk7n4BNzwyv/EBAAA="


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
    category_order = ["Pre-pivot source", "Post-pivot source", "Single-origin AI4Sci", "Cross-origin AI4Sci"]
    summary = data.set_index("category").loc[category_order].reset_index()
    x = np.arange(len(summary))
    fig, ax = plt.subplots(figsize=s["figure.size"], facecolor=s["figure.facecolor"])
    ax.axvspan(0.5, len(summary) - 0.5, color=s["phase.color"], alpha=s["phase.alpha"],
               linewidth=0, zorder=0)
    ax.bar(x, summary["mean"], yerr=summary["ci95"], color=s["bars.colors"],
           width=s["bars.width"], edgecolor="none", capsize=s["bars.cap_size"],
           error_kw={"lw": s["bars.error_line_width"]})
    before = float(summary.loc[summary["category"] == "Pre-pivot source", "mean"].iloc[0])
    ax.axvline(0.5, color=s["reference.color"], lw=s["reference.line_width"], ls="--", zorder=2)
    ax.axhline(before, color=s["reference.color"], lw=s["reference.line_width"], ls=":", zorder=3)
    ax.set_xticks(x, s["axes.x_tick_labels"])
    ax.set_ylabel(s["axes.y_label"])
    ax.set_ylim(s["axes.y_range"])
    ax.set_title(s["axes.title"], fontsize=s["typography.title_size"], pad=s["typography.title_pad"])
    ax.xaxis.label.set_size(s["typography.axis_label_size"])
    ax.yaxis.label.set_size(s["typography.axis_label_size"])
    ax.tick_params(labelsize=s["typography.tick_label_size"], direction="out",
                   width=s["typography.tick_width"], length=s["typography.tick_length"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for spine in ax.spines.values():
        spine.set_linewidth(s["axes.spine_width"])
    ax.grid(s["axes.grid"])
    for item in [ax.title, ax.yaxis.label, *ax.get_xticklabels(), *ax.get_yticklabels()]:
        item.set_fontfamily(s["typography.font_family"])
    fig.tight_layout()
    return fig
