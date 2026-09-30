"""Matplot Studio conversion of the fixed-window F/E/G figure."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import pandas as pd


PLOT_META = {
    "id": "line-feg-ten-year-window",
    "name": "F/E/G indices: 10-year window",
    "description": "EWMA-smoothed Foundation, Extension, and Generalization indices using a 10-year forward-citation window.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original result table is embedded; the upstream database query is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.75, 2.4], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "AI4Sci publication year", "required": True},
    {"path": "axes.f_y_label", "label": "Left-axis label", "group": "Axes", "type": "string", "default": "Foundation index", "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2014], "required": True},
    {"path": "axes.relative_padding", "label": "Relative Y padding", "group": "Axes", "type": "number", "default": 0.08, "min": 0, "max": 0.5, "step": 0.01, "required": True},
    {"path": "axes.minimum_padding", "label": "Minimum Y padding", "group": "Axes", "type": "number", "default": 0.005, "min": 0, "max": 0.2, "step": 0.001, "required": True},
    {"path": "axes.x_tick_interval", "label": "X tick interval", "group": "Axes", "type": "number", "default": 10, "min": 1, "max": 30, "step": 1, "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "series.foundation.color", "label": "Foundation color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.extension.color", "label": "Extension color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.generalization.color", "label": "Generalization color", "group": "Series", "type": "color", "default": "#009E73", "required": True},
    {"path": "series.line_width", "label": "Line width", "group": "Series", "type": "number", "default": 1.3, "min": 0.1, "max": 8, "step": 0.05, "required": True},
    {"path": "annotation.labels", "label": "Curve labels", "group": "Annotations", "type": "string_list", "default": ["Foundation", "Extension", "Generalization"], "required": True},
    {"path": "annotation.foundation_year", "label": "Foundation label year", "group": "Annotations", "type": "integer", "default": 2006, "min": 1995, "max": 2014, "required": True},
    {"path": "annotation.extension_year", "label": "Extension label year", "group": "Annotations", "type": "integer", "default": 2008, "min": 1995, "max": 2014, "required": True},
    {"path": "annotation.generalization_year", "label": "Generalization label year", "group": "Annotations", "type": "integer", "default": 1997, "min": 1995, "max": 2014, "required": True},
    {"path": "annotation.offset", "label": "Label offset", "group": "Annotations", "type": "number_pair", "default": [4, 5], "min": -30, "max": 30, "step": 1, "required": True},
    {"path": "annotation.font_size", "label": "Label font size", "group": "Annotations", "type": "number", "default": 7.2, "min": 4, "max": 24, "step": 0.1, "required": True},
    {"path": "annotation.background", "label": "Label background", "group": "Annotations", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "annotation.background_alpha", "label": "Label background opacity", "group": "Annotations", "type": "number", "default": 0.78, "min": 0, "max": 1, "step": 0.01, "required": True},
    {"path": "annotation.background_pad", "label": "Label background padding", "group": "Annotations", "type": "number", "default": 0.5, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "header.text", "label": "Header text", "group": "Annotations", "type": "string", "default": "10-year forward-citation window", "required": True},
    {"path": "header.position", "label": "Header position", "group": "Annotations", "type": "number_pair", "default": [0.5, 1.02], "min": -1, "max": 2, "step": 0.01, "required": True},
    {"path": "header.font_size", "label": "Header font size", "group": "Annotations", "type": "number", "default": 8, "min": 4, "max": 24, "step": 0.5, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [2.75, 2.4], "figure.facecolor": "#FFFFFF",
    "axes.x_label": "AI4Sci publication year", "axes.f_y_label": "Foundation index",
    "axes.x_range": [1995, 2014], "axes.relative_padding": 0.08,
    "axes.minimum_padding": 0.005, "axes.x_tick_interval": 10,
    "axes.grid": False, "axes.spine_width": 0.6,
    "series.foundation.color": "#D55E5E", "series.extension.color": "#3B6FB6",
    "series.generalization.color": "#009E73", "series.line_width": 1.3,
    "annotation.labels": ["Foundation", "Extension", "Generalization"],
    "annotation.foundation_year": 2006, "annotation.extension_year": 2008,
    "annotation.generalization_year": 1997, "annotation.offset": [4, 5],
    "annotation.font_size": 7.2, "annotation.background": "#FFFFFF",
    "annotation.background_alpha": 0.78, "annotation.background_pad": 0.5,
    "header.text": "10-year forward-citation window", "header.position": [0.5, 1.02],
    "header.font_size": 8, "typography.font_family": "Arial",
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


def _padded_limits(values, relative_padding, minimum_padding):
    low, high = float(values.min()), float(values.max())
    padding = max((high - low) * relative_padding, minimum_padding)
    return max(0, low - padding), min(1, high + padding)


def render(data, settings):
    s = _resolved(settings)
    fig, ax_f = plt.subplots(figsize=s["figure.size"], facecolor=s["figure.facecolor"])
    ax_eg = ax_f.twinx()
    ax_f.plot(data["year"], data["F_ewma5"], color=s["series.foundation.color"],
              lw=s["series.line_width"])
    ax_eg.plot(data["year"], data["E_ewma5"], color=s["series.extension.color"],
               lw=s["series.line_width"])
    ax_eg.plot(data["year"], data["G_ewma5"], color=s["series.generalization.color"],
               lw=s["series.line_width"])
    ax_f.set(xlabel=s["axes.x_label"], ylabel=s["axes.f_y_label"], xlim=s["axes.x_range"],
             ylim=_padded_limits(data["F_ewma5"], s["axes.relative_padding"], s["axes.minimum_padding"]))
    ax_eg.set_ylim(_padded_limits(pd.concat([data["E_ewma5"], data["G_ewma5"]]),
                                  s["axes.relative_padding"], s["axes.minimum_padding"]))
    ax_f.xaxis.set_major_locator(MultipleLocator(s["axes.x_tick_interval"]))
    labels = s["annotation.labels"]
    annotations = [
        (ax_f, "F", s["annotation.foundation_year"], labels[0], s["series.foundation.color"]),
        (ax_eg, "E", s["annotation.extension_year"], labels[1], s["series.extension.color"]),
        (ax_eg, "G", s["annotation.generalization_year"], labels[2], s["series.generalization.color"]),
    ]
    text_items = []
    for axis, key, year, label, color in annotations:
        row = data.loc[data["year"].eq(year)].iloc[0]
        text_items.append(axis.annotate(
            label, xy=(year, row[f"{key}_ewma5"]), xytext=s["annotation.offset"],
            textcoords="offset points", color=color, fontsize=s["annotation.font_size"],
            bbox={"facecolor": s["annotation.background"], "edgecolor": "none",
                  "alpha": s["annotation.background_alpha"], "pad": s["annotation.background_pad"]}))
    header = ax_f.text(*s["header.position"], s["header.text"], transform=ax_f.transAxes,
                       ha="center", va="bottom", fontsize=s["header.font_size"])
    ax_f.xaxis.label.set_size(s["typography.axis_label_size"])
    ax_f.yaxis.label.set_size(s["typography.axis_label_size"])
    ax_eg.yaxis.label.set_size(s["typography.axis_label_size"])
    for axis in (ax_f, ax_eg):
        axis.tick_params(labelsize=s["typography.tick_label_size"], direction="out",
                         width=s["typography.tick_width"], length=s["typography.tick_length"])
        for spine in axis.spines.values():
            spine.set_linewidth(s["axes.spine_width"])
        axis.grid(s["axes.grid"])
    ax_f.spines["top"].set_visible(False)
    ax_f.spines["right"].set_visible(False)
    ax_eg.spines["top"].set_visible(False)
    ax_eg.spines["left"].set_visible(False)
    ax_eg.spines["bottom"].set_visible(False)
    font_items = [ax_f.xaxis.label, ax_f.yaxis.label, *ax_f.get_xticklabels(),
                  *ax_f.get_yticklabels(), *ax_eg.get_yticklabels(), header, *text_items]
    for item in font_items:
        item.set_fontfamily(s["typography.font_family"])
    fig.tight_layout()
    return fig
