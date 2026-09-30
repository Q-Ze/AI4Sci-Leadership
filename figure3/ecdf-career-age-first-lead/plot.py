"""Matplot Studio conversion of a career-age ECDF."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "ecdf-career-age-first-lead",
    "name": "Career age at first AI4Sci first-authorship",
    "description": "ECDF of career age at authors’ first AI4Sci first-authorship, by Specialist class.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original aggregated ECDF table is embedded; the upstream database query is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Career age at first AI4Sci first-authorship", "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Cumulative share", "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [0, 50], "required": True},
    {"path": "axes.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0, 1], "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "format.percent_decimals", "label": "Percent decimals", "group": "Axes", "type": "integer", "default": 0, "min": 0, "max": 3, "required": True},
    {"path": "series.ai.color", "label": "AI Specialist color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.domain.color", "label": "Domain Specialist color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.line_width", "label": "Line width", "group": "Series", "type": "number", "default": 1.3, "min": 0.1, "max": 8, "step": 0.05, "required": True},
    {"path": "series.step_where", "label": "Step alignment", "group": "Series", "type": "select", "options": ["pre", "post", "mid"], "default": "post", "required": True},
    {"path": "legend.labels", "label": "Legend labels", "group": "Legend", "type": "string_list", "default": ["AI Specialist", "Domain Specialist"], "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "options": ["lower right", "lower left", "upper right", "upper left", "best"], "default": "lower right", "required": True},
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
    "figure.size": [3.8, 2.4], "figure.facecolor": "#FFFFFF",
    "axes.x_label": "Career age at first AI4Sci first-authorship", "axes.y_label": "Cumulative share",
    "axes.x_range": [0, 50], "axes.y_range": [0, 1], "axes.grid": False,
    "axes.spine_width": 0.6, "format.percent_decimals": 0,
    "series.ai.color": "#3B6FB6", "series.domain.color": "#D55E5E",
    "series.line_width": 1.3, "series.step_where": "post",
    "legend.labels": ["AI Specialist", "Domain Specialist"], "legend.location": "lower right",
    "legend.font_size": 7.2, "legend.handle_length": 1.8,
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
    fig, ax = plt.subplots(figsize=s["figure.size"], facecolor=s["figure.facecolor"])
    labels = s["legend.labels"]
    for author_class, color, label in [("AI", s["series.ai.color"], labels[0]),
                                        ("Domain", s["series.domain.color"], labels[1])]:
        subset = data[data["author_class"] == author_class]
        ax.step(subset["career_age"], subset["cdf"], where=s["series.step_where"],
                color=color, lw=s["series.line_width"], label=label)
    ax.set(xlabel=s["axes.x_label"], ylabel=s["axes.y_label"],
           xlim=s["axes.x_range"], ylim=s["axes.y_range"])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=s["format.percent_decimals"]))
    legend = ax.legend(frameon=False, loc=s["legend.location"], fontsize=s["legend.font_size"],
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
