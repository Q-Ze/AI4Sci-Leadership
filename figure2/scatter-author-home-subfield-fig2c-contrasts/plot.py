"""Matplot Studio conversion of within-author audience contrasts."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PLOT_META = {
    "id": "scatter-author-home-subfield-fig2c-contrasts",
    "name": "Figure 2c: within-author audience contrasts",
    "description": "Author-weighted outside-minus-home citation contrasts with bootstrap confidence intervals.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original six-estimate result table is embedded; bootstrap sampling is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.2, 2.4], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "text", "default": "Relative citation advantage\nof outside audience", "required": True},
    {"path": "axes.y_label_pad", "label": "Y-label padding", "group": "Axes", "type": "number", "default": 2.5, "min": 0, "max": 20, "step": 0.5, "required": True},
    {"path": "axes.x_tick_labels", "label": "X tick labels", "group": "Axes", "type": "string_list", "default": ["All\noutside", "Outside\nw/o CS", "Computer\nScience"], "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [-0.22, 2.36], "required": True},
    {"path": "axes.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [-0.025, 0.62], "required": True},
    {"path": "axes.x_tick_rotation", "label": "X tick rotation", "group": "Axes", "type": "number", "default": 25, "min": -90, "max": 90, "step": 1, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "series.ai.color", "label": "AI-led color", "group": "Series", "type": "color", "default": "#3B73B9", "required": True},
    {"path": "series.domain.color", "label": "Domain-led color", "group": "Series", "type": "color", "default": "#D95B59", "required": True},
    {"path": "series.group_offset", "label": "Group offset", "group": "Series", "type": "number", "default": 0.06, "min": 0, "max": 0.4, "step": 0.01, "required": True},
    {"path": "series.marker_size", "label": "Marker size", "group": "Series", "type": "number", "default": 3.5, "min": 0.5, "max": 20, "step": 0.5, "required": True},
    {"path": "series.line_width", "label": "Error-bar width", "group": "Series", "type": "number", "default": 0.8, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "series.cap_size", "label": "Error-bar cap size", "group": "Series", "type": "number", "default": 2, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "reference.y", "label": "Reference level", "group": "Reference", "type": "number", "default": 0, "min": -1, "max": 1, "step": 0.05, "required": True},
    {"path": "reference.color", "label": "Reference color", "group": "Reference", "type": "color", "default": "#777777", "required": True},
    {"path": "reference.line_width", "label": "Reference width", "group": "Reference", "type": "number", "default": 0.7, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "legend.labels", "label": "Legend labels", "group": "Legend", "type": "string_list", "default": ["AI-led", "Domain-led"], "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "options": ["lower center", "upper center", "best"], "default": "lower center", "required": True},
    {"path": "legend.anchor", "label": "Legend anchor", "group": "Legend", "type": "number_pair", "default": [0.5, 1.02], "min": -1, "max": 2, "step": 0.01, "required": True},
    {"path": "legend.columns", "label": "Legend columns", "group": "Legend", "type": "integer", "default": 2, "min": 1, "max": 4, "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.2, "min": 4, "max": 24, "step": 0.1, "required": True},
    {"path": "legend.label_spacing", "label": "Legend label spacing", "group": "Legend", "type": "number", "default": 0.6, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "legend.handle_length", "label": "Legend handle length", "group": "Legend", "type": "number", "default": 0.8, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "legend.handle_text_pad", "label": "Legend handle-text pad", "group": "Legend", "type": "number", "default": 0.35, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [2.2, 2.4], "figure.facecolor": "#FFFFFF",
    "axes.y_label": "Relative citation advantage\nof outside audience", "axes.y_label_pad": 2.5,
    "axes.x_tick_labels": ["All\noutside", "Outside\nw/o CS", "Computer\nScience"],
    "axes.x_range": [-0.22, 2.36], "axes.y_range": [-0.025, 0.62],
    "axes.x_tick_rotation": 25, "axes.spine_width": 0.6,
    "series.ai.color": "#3B73B9", "series.domain.color": "#D95B59",
    "series.group_offset": 0.06, "series.marker_size": 3.5,
    "series.line_width": 0.8, "series.cap_size": 2,
    "reference.y": 0, "reference.color": "#777777", "reference.line_width": 0.7,
    "legend.labels": ["AI-led", "Domain-led"], "legend.location": "lower center",
    "legend.anchor": [0.5, 1.02], "legend.columns": 2, "legend.font_size": 7.2,
    "legend.label_spacing": 0.6, "legend.handle_length": 0.8,
    "legend.handle_text_pad": 0.35, "typography.font_family": "Arial",
    "typography.axis_label_size": 9, "typography.tick_label_size": 8,
    "typography.tick_width": 0.6, "typography.tick_length": 3,
}

_CSV_GZIP_B64 = "H4sIAAAAAAAAA3WRPW7bQBCFe52CByCc+f8pDadJ5cIHEAiKiAhQpCFS8BVc+4g5SXaJqFJc7C4wmP3emzfT0J2G67GfunVt+2Xert26tfOxu23n5bq2l6Gb2348TstHfc7j7/Ph+Vf7PE3NctvW8TQ0fz6/mvNyGVpX8xaeWFU5kIXQPMJKicIYQJwzjQijlATdMJVBUjCUrGJf/yE/fizNy9sDGVkxBFRYBSF3Dpgjp4U6ZgIQVjkALifUUhTBd/bLcnm/bcO1eevHYe4ffSsScIRLBFJALQlzAhaGMTsx164QwaRiXphQDz+XSzfO/w+kYHaP9TtkvdAkA/dZQEAEyvCFn2FSfWNYJpmRU5a+uNO/y+UuQK6eUEwjUGHuGVRRY4QgEwqqfGZRZhJPLcEo3/HfR3MXKO7LRl2IEmrSlQbsdb1Fs2SmXveM5SERcQAPtuTDX/lyWNhgAgAA"


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
    order = ["All outside − home", "Outside w/o CS − home", "Computer Science − home"]
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=s["figure.size"], facecolor=s["figure.facecolor"])
    labels = s["legend.labels"]
    groups = [("AI", -s["series.group_offset"], labels[0], s["series.ai.color"]),
              ("Domain", s["series.group_offset"], labels[1], s["series.domain.color"])]
    for leader, offset, label, color in groups:
        subset = data.loc[data["leader_class"].eq(leader)].set_index("contrast").loc[order]
        mean = subset["mean"].to_numpy()
        error = np.vstack([mean - subset["ci_low"].to_numpy(),
                           subset["ci_high"].to_numpy() - mean])
        ax.errorbar(x + offset, mean, yerr=error, fmt="o", markersize=s["series.marker_size"],
                    lw=s["series.line_width"], capsize=s["series.cap_size"], color=color, label=label)
    ax.axhline(s["reference.y"], color=s["reference.color"],
               lw=s["reference.line_width"], ls="--")
    ax.set_xticks(x, s["axes.x_tick_labels"])
    ax.set_xlim(s["axes.x_range"])
    ax.set_ylim(s["axes.y_range"])
    ax.set_yticks([0, 0.2, 0.4, 0.6])
    ax.set_ylabel(s["axes.y_label"], fontsize=s["typography.axis_label_size"],
                  labelpad=s["axes.y_label_pad"])
    legend = ax.legend(frameon=False, loc=s["legend.location"], bbox_to_anchor=s["legend.anchor"],
                       ncol=s["legend.columns"], borderaxespad=0,
                       labelspacing=s["legend.label_spacing"], handlelength=s["legend.handle_length"],
                       handletextpad=s["legend.handle_text_pad"], fontsize=s["legend.font_size"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for spine in ax.spines.values():
        spine.set_linewidth(s["axes.spine_width"])
    for label in ax.get_xticklabels():
        label.set_rotation(s["axes.x_tick_rotation"])
        label.set_ha("right")
    ax.tick_params(axis="both", direction="out", labelsize=s["typography.tick_label_size"],
                   width=s["typography.tick_width"], length=s["typography.tick_length"])
    for item in [ax.yaxis.label, *ax.get_xticklabels(), *ax.get_yticklabels(), *legend.get_texts()]:
        item.set_fontfamily(s["typography.font_family"])
    fig.tight_layout()
    return fig
