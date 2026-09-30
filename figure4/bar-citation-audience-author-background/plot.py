"""Matplot Studio conversion of a citation-audience stacked bar chart."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd


PLOT_META = {
    "id": "bar-citation-audience-author-background",
    "name": "Citation audience by author background",
    "description": "Stacked shares of classified citation events by citing last-author Specialist class and JCR quartile.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original plotted result table is embedded; the upstream citation query is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.5, 3], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "layout.top", "label": "Layout top", "group": "Layout", "type": "number", "default": 0.93, "min": 0.5, "max": 1, "step": 0.01, "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Share of classified citation events", "required": True},
    {"path": "axes.x_tick_labels", "label": "JCR labels", "group": "Axes", "type": "string_list", "default": ["Q1", "Q2", "Q3", "Q4", "Overall"], "required": True},
    {"path": "axes.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0, 1], "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "bars.colors", "label": "Audience colors", "group": "Bars", "type": "color_list", "default": ["#3B6FB6", "#D55E5E"], "required": True},
    {"path": "bars.width", "label": "Bar width", "group": "Bars", "type": "number", "default": 0.72, "min": 0.1, "max": 1, "step": 0.01, "required": True},
    {"path": "legend.labels", "label": "Legend labels", "group": "Legend", "type": "string_list", "default": ["AI Specialist", "Domain Specialist"], "required": True},
    {"path": "legend.columns", "label": "Legend columns", "group": "Legend", "type": "integer", "default": 2, "min": 1, "max": 4, "required": True},
    {"path": "legend.anchor", "label": "Legend anchor", "group": "Legend", "type": "number_pair", "default": [0.5, 1.02], "min": -1, "max": 2, "step": 0.01, "required": True},
    {"path": "legend.column_spacing", "label": "Legend column spacing", "group": "Legend", "type": "number", "default": 1.0, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "legend.handle_length", "label": "Legend handle length", "group": "Legend", "type": "number", "default": 1.2, "min": 0, "max": 8, "step": 0.1, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.legend_size", "label": "Legend size", "group": "Typography", "type": "number", "default": 7.2, "min": 4, "max": 30, "step": 0.1, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [3.5, 3], "figure.facecolor": "#FFFFFF", "layout.top": 0.93,
    "axes.y_label": "Share of classified citation events",
    "axes.x_tick_labels": ["Q1", "Q2", "Q3", "Q4", "Overall"],
    "axes.y_range": [0, 1], "axes.grid": False, "axes.spine_width": 0.6,
    "bars.colors": ["#3B6FB6", "#D55E5E"], "bars.width": 0.72,
    "legend.labels": ["AI Specialist", "Domain Specialist"], "legend.columns": 2,
    "legend.anchor": [0.5, 1.02], "legend.column_spacing": 1.0, "legend.handle_length": 1.2,
    "typography.font_family": "Arial", "typography.axis_label_size": 9,
    "typography.tick_label_size": 8, "typography.legend_size": 7.2,
    "typography.tick_width": 0.6, "typography.tick_length": 3,
}

_TYPE_COLUMN = "citer_background"
_TYPE_KEYS = ["AI", "Domain"]
_CSV_GZIP_B64 = "H4sIAAAAAAAAA02Qy0rEYAyF9/+zBMn1T7IU3LiSPoHUWnR07EC9PL8pU6ybEHIOX5LzNq0wnb7m9fFpnN5f1sv38gyfr+M6w9IGgtt7wBuOIHNOclJKI6AwVMHNcHf5GE9LmZwolB2DwwI1Qa1G3dvAV4oQeTBHJmq1Ar2LaGz6H6RHMLkTYlq1DqRd2bgNskMYqTZn9EQvDDBhsm36AfEMK51kk6IuUU+mNujOcFOx7OxcVQ0SbXtG/yFYrSuKs1c1AzLsKO3hZ17H83mPJT1FWbiyYXHgSonlMB3RIGM37175eL8+nirtF+5xhil9AQAA"


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
    jcr_keys = ["Q1", "Q2", "Q3", "Q4", "Overall"]
    x = np.arange(len(jcr_keys))
    bottom = np.zeros(len(jcr_keys))
    fig, ax = plt.subplots(figsize=s["figure.size"], facecolor=s["figure.facecolor"])
    for audience, color, label in zip(_TYPE_KEYS, s["bars.colors"], s["legend.labels"]):
        subset = data[data[_TYPE_COLUMN] == audience].set_index("jcr").loc[jcr_keys]
        values = subset["share"].to_numpy()
        ax.bar(x, values, bottom=bottom, color=color, width=s["bars.width"], label=label)
        bottom += values
    ax.set_xticks(x, s["axes.x_tick_labels"])
    ax.set_ylabel(s["axes.y_label"])
    ax.set_ylim(s["axes.y_range"])
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    legend = ax.legend(frameon=False, ncol=s["legend.columns"], loc="lower center",
                       bbox_to_anchor=s["legend.anchor"], borderaxespad=0,
                       columnspacing=s["legend.column_spacing"], handlelength=s["legend.handle_length"],
                       fontsize=s["typography.legend_size"])
    ax.yaxis.label.set_size(s["typography.axis_label_size"])
    ax.tick_params(labelsize=s["typography.tick_label_size"], direction="out",
                   width=s["typography.tick_width"], length=s["typography.tick_length"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for spine in ax.spines.values():
        spine.set_linewidth(s["axes.spine_width"])
    ax.grid(s["axes.grid"])
    for item in [ax.yaxis.label, *ax.get_xticklabels(), *ax.get_yticklabels(), *legend.get_texts()]:
        item.set_fontfamily(s["typography.font_family"])
    fig.tight_layout(rect=(0, 0, 1, s["layout.top"]))
    return fig
