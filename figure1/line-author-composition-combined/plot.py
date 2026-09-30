"""Matplot Studio conversion of the combined author-composition figure."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "line-author-composition-combined",
    "name": "Author composition by authorship position",
    "description": "EWMA-smoothed Domain Specialist shares for all, first, and last authors.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original result table is embedded; the upstream database query is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.45, 2.15], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Year", "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Domain Specialist share", "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2024], "required": True},
    {"path": "axes.y_padding", "label": "Y-axis padding", "group": "Axes", "type": "number", "default": 0.035, "min": 0, "max": 0.5, "step": 0.005, "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.top_spine", "label": "Show top spine", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.right_spine", "label": "Show right spine", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "format.percent_decimals", "label": "Percent decimals", "group": "Axes", "type": "integer", "default": 0, "min": 0, "max": 3, "required": True},
    {"path": "series.domain.color", "label": "Line color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.line_width", "label": "Line width", "group": "Series", "type": "number", "default": 1.35, "min": 0.1, "max": 8, "step": 0.05, "required": True},
    {"path": "series.all.line_style", "label": "All-author line style", "group": "Series", "type": "select", "options": ["-", "--", ":", "-."], "default": "-", "required": True},
    {"path": "series.first.line_style", "label": "First-author line style", "group": "Series", "type": "select", "options": ["-", "--", ":", "-."], "default": "--", "required": True},
    {"path": "series.last.line_style", "label": "Last-author line style", "group": "Series", "type": "select", "options": ["-", "--", ":", "-."], "default": ":", "required": True},
    {"path": "legend.labels", "label": "Legend labels", "group": "Legend", "type": "string_list", "default": ["All distinct authors", "First-author positions", "Last-author positions"], "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.2, "min": 4, "max": 24, "step": 0.1, "required": True},
    {"path": "legend.handle_length", "label": "Legend handle length", "group": "Legend", "type": "number", "default": 2.3, "min": 0, "max": 8, "step": 0.1, "required": True},
    {"path": "legend.label_spacing", "label": "Legend label spacing", "group": "Legend", "type": "number", "default": 0.3, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "legend.border_axes_pad", "label": "Legend axes padding", "group": "Legend", "type": "number", "default": 0.2, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [2.45, 2.15], "figure.facecolor": "#FFFFFF",
    "axes.x_label": "Year", "axes.y_label": "Domain Specialist share",
    "axes.x_range": [1995, 2024], "axes.y_padding": 0.035, "axes.grid": False,
    "axes.top_spine": False, "axes.right_spine": False, "axes.spine_width": 0.6,
    "format.percent_decimals": 0, "series.domain.color": "#D55E5E",
    "series.line_width": 1.35, "series.all.line_style": "-",
    "series.first.line_style": "--", "series.last.line_style": ":",
    "legend.labels": ["All distinct authors", "First-author positions", "Last-author positions"],
    "legend.font_size": 7.2, "legend.handle_length": 2.3, "legend.label_spacing": 0.3,
    "legend.border_axes_pad": 0.2, "typography.font_family": "Arial",
    "typography.axis_label_size": 9, "typography.tick_label_size": 8,
    "typography.tick_width": 0.6, "typography.tick_length": 3,
}

_CSV_GZIP_B64 = "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"


def prepare_data():
    csv_text = decompress(b64decode(_CSV_GZIP_B64)).decode("utf-8")
    return pd.DataFrame(_typed_rows(csv_text))


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
    labels = s["legend.labels"]
    specs = [
        ("all_domain_share_ewma5", labels[0], s["series.all.line_style"]),
        ("first_domain_share_ewma5", labels[1], s["series.first.line_style"]),
        ("last_domain_share_ewma5", labels[2], s["series.last.line_style"]),
    ]
    for column, label, line_style in specs:
        ax.plot(data["year"], data[column], color=s["series.domain.color"],
                lw=s["series.line_width"], ls=line_style, label=label)
    smooth = pd.concat([data[column] for column, _, _ in specs], ignore_index=True)
    padding = s["axes.y_padding"]
    ax.set(xlabel=s["axes.x_label"], ylabel=s["axes.y_label"],
           xlim=s["axes.x_range"],
           ylim=(max(0, smooth.min() - padding), min(1, smooth.max() + padding)))
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=s["format.percent_decimals"]))
    ax.legend(frameon=False, fontsize=s["legend.font_size"],
              handlelength=s["legend.handle_length"], labelspacing=s["legend.label_spacing"],
              borderaxespad=s["legend.border_axes_pad"])
    ax.xaxis.label.set_size(s["typography.axis_label_size"])
    ax.yaxis.label.set_size(s["typography.axis_label_size"])
    ax.tick_params(labelsize=s["typography.tick_label_size"], direction="out",
                   width=s["typography.tick_width"], length=s["typography.tick_length"])
    ax.spines["top"].set_visible(s["axes.top_spine"])
    ax.spines["right"].set_visible(s["axes.right_spine"])
    for spine in ax.spines.values():
        spine.set_linewidth(s["axes.spine_width"])
    ax.grid(s["axes.grid"])
    for item in [ax.xaxis.label, ax.yaxis.label, *ax.get_xticklabels(), *ax.get_yticklabels(), *ax.get_legend().get_texts()]:
        item.set_fontfamily(s["typography.font_family"])
    fig.tight_layout()
    return fig
