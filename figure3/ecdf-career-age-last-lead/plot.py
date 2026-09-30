"""Matplot Studio conversion of a career-age ECDF."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "ecdf-career-age-last-lead",
    "name": "Career age at first AI4Sci last-authorship",
    "description": "ECDF of career age at authors’ first AI4Sci last-authorship, by Specialist class.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original aggregated ECDF table is embedded; the upstream database query is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Career age at first AI4Sci last-authorship", "required": True},
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
    "axes.x_label": "Career age at first AI4Sci last-authorship", "axes.y_label": "Cumulative share",
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
