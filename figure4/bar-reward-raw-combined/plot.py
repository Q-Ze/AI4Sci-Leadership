"""Matplot Studio conversion of the combined reward bar chart."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd


PLOT_META = {
    "id": "bar-reward-raw-combined",
    "name": "Raw reward probabilities",
    "description": "Unadjusted NIH, NSF, and news probabilities with confidence intervals by leader class.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original plotted result table is embedded; upstream count aggregation is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "layout.top", "label": "Layout top", "group": "Layout", "type": "number", "default": 1, "min": 0.5, "max": 1, "step": 0.01, "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Papers with recorded outcome", "required": True},
    {"path": "axes.x_tick_labels", "label": "Outcome labels", "group": "Axes", "type": "string_list", "default": ["NIH", "NSF", "News"], "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "format.percent_decimals", "label": "Percent decimals (-1 = auto)", "group": "Axes", "type": "integer", "default": 1, "min": -1, "max": 3, "required": True},
    {"path": "bars.ai.color", "label": "AI-led color", "group": "Bars", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "bars.domain.color", "label": "Domain-led color", "group": "Bars", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "bars.width", "label": "Bar width", "group": "Bars", "type": "number", "default": 0.34, "min": 0.05, "max": 0.9, "step": 0.01, "required": True},
    {"path": "error.color", "label": "Error-bar color", "group": "Error bars", "type": "color", "default": "#000000", "required": True},
    {"path": "error.line_width", "label": "Error-bar width", "group": "Error bars", "type": "number", "default": 0.7, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "error.cap_size", "label": "Error-bar cap size", "group": "Error bars", "type": "number", "default": 2, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "legend.labels", "label": "Legend labels", "group": "Legend", "type": "string_list", "default": ["AI Specialist-led", "Domain Specialist-led"], "required": True},
    {"path": "legend.columns", "label": "Legend columns", "group": "Legend", "type": "integer", "default": 1, "min": 1, "max": 4, "required": True},
    {"path": "legend.use_anchor", "label": "Use anchored legend", "group": "Legend", "type": "boolean", "default": False, "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "options": ["best", "lower center", "upper center", "upper right", "upper left"], "default": "best", "required": True},
    {"path": "legend.anchor", "label": "Legend anchor", "group": "Legend", "type": "number_pair", "default": [0.5, 1.02], "min": -1, "max": 2, "step": 0.01, "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.2, "min": 4, "max": 24, "step": 0.1, "required": True},
    {"path": "legend.handle_length", "label": "Legend handle length", "group": "Legend", "type": "number", "default": 1.8, "min": 0, "max": 8, "step": 0.1, "required": True},
    {"path": "legend.label_spacing", "label": "Legend label spacing", "group": "Legend", "type": "number", "default": 0.3, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "legend.column_spacing", "label": "Legend column spacing", "group": "Legend", "type": "number", "default": 0.7, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "legend.border_axes_pad", "label": "Legend axes padding", "group": "Legend", "type": "number", "default": 0.2, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [3.8, 2.4], "figure.facecolor": "#FFFFFF", "layout.top": 1,
    "axes.y_label": "Papers with recorded outcome", "axes.x_tick_labels": ["NIH", "NSF", "News"],
    "axes.grid": False, "axes.spine_width": 0.6, "format.percent_decimals": 1,
    "bars.ai.color": "#3B6FB6", "bars.domain.color": "#D55E5E", "bars.width": 0.34,
    "error.color": "#000000", "error.line_width": 0.7, "error.cap_size": 2,
    "legend.labels": ["AI Specialist-led", "Domain Specialist-led"], "legend.columns": 1,
    "legend.use_anchor": False, "legend.location": "best", "legend.anchor": [0.5, 1.02],
    "legend.font_size": 7.2, "legend.handle_length": 1.8, "legend.label_spacing": 0.3,
    "legend.column_spacing": 0.7, "legend.border_axes_pad": 0.2,
    "typography.font_family": "Arial", "typography.axis_label_size": 9,
    "typography.tick_label_size": 8, "typography.tick_width": 0.6, "typography.tick_length": 3,
}

_VALUE_COLUMN = "probability"
_CSV_GZIP_B64 = "H4sIAAAAAAAAA1VQO24CMRDt9yxWNH/PlJGiKDQ0OQACsgorLSwCEpTbZ1hTQGPLzzPvN/1cttO+L2O//upPq+24Pp/LoRyn83AZfvtyPE2b9WYYh8tf2Q6rcbrert3wveuWi4/yuiikUisUCS/wAoCRbxASzqOKWEOrMwZCgq6iPIOEZIRVVA0A2GbGt2m/Hg5FHEW8kN9pLYlZ0JTMEao3WnUAF4lKobUKtlHiVHNmEpBc6Zaf7w9GKURvc4iqIXLbMwJqRhFTliumHIMhSAMjTWKE1PTA7jPjs1FjawRMRIaZt9bK2pQyRS67WOSnBrbB7IGqIlgaVYhu2V/PDz5Tc47DTgzZUDYBJkENVM82HD1p3aDpgGR2C45IyUzhjfLZKLs2iqwO3HIlLxWIGcwygiAQOTslvk+SUsbPZjFcvXb/wNvlDzUCAAA="


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
    outcome_keys = ["NIH", "NSF", "News"]
    x = np.arange(len(outcome_keys))
    width = s["bars.width"]
    fig, ax = plt.subplots(figsize=s["figure.size"], facecolor=s["figure.facecolor"])
    labels = s["legend.labels"]
    for offset, leader, label, color in [(-width / 2, "AI", labels[0], s["bars.ai.color"]),
                                          (width / 2, "Domain", labels[1], s["bars.domain.color"])]:
        subset = data.set_index(["outcome", "leader_class"]).loc[
            [(outcome, leader) for outcome in outcome_keys]].reset_index()
        values = subset[_VALUE_COLUMN].to_numpy()
        error = np.vstack([values - subset["ci_low"].to_numpy(),
                           subset["ci_high"].to_numpy() - values])
        ax.bar(x + offset, values, width=width, color=color, label=label)
        ax.errorbar(x + offset, values, yerr=error, fmt="none", color=s["error.color"],
                    lw=s["error.line_width"], capsize=s["error.cap_size"])
    ax.set_xticks(x, s["axes.x_tick_labels"])
    ax.set_ylabel(s["axes.y_label"])
    decimals = None if s["format.percent_decimals"] < 0 else s["format.percent_decimals"]
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=decimals))
    legend_kwargs = dict(frameon=False, fontsize=s["legend.font_size"], ncol=s["legend.columns"],
                         handlelength=s["legend.handle_length"], labelspacing=s["legend.label_spacing"],
                         columnspacing=s["legend.column_spacing"], borderaxespad=s["legend.border_axes_pad"])
    if s["legend.use_anchor"]:
        legend_kwargs.update(loc=s["legend.location"], bbox_to_anchor=s["legend.anchor"])
    legend = ax.legend(**legend_kwargs)
    ax.xaxis.label.set_size(s["typography.axis_label_size"])
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
