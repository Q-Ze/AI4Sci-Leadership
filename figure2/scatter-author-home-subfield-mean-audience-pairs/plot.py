"""Matplot Studio conversion of home/outside audience mean pairs."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


PLOT_META = {
    "id": "scatter-author-home-subfield-mean-audience-pairs",
    "name": "Mean home versus outside-audience pairs",
    "description": "Dumbbell comparison of mean normalized home and outside-audience citations by leader class.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original plotted mean-pair table is embedded; paper-level aggregation is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "layout.left", "label": "Left margin", "group": "Layout", "type": "number", "default": 0.31, "min": 0, "max": 1, "step": 0.01, "required": True},
    {"path": "layout.right", "label": "Right margin", "group": "Layout", "type": "number", "default": 0.98, "min": 0, "max": 1, "step": 0.01, "required": True},
    {"path": "layout.bottom", "label": "Bottom margin", "group": "Layout", "type": "number", "default": 0.2, "min": 0, "max": 1, "step": 0.01, "required": True},
    {"path": "layout.top", "label": "Top margin", "group": "Layout", "type": "number", "default": 0.73, "min": 0, "max": 1, "step": 0.01, "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Mean normalized citations", "required": True},
    {"path": "axes.y_tick_labels", "label": "Audience labels", "group": "Axes", "type": "string_list", "default": ["All outside", "Outside w/o CS", "Computer Science"], "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [0.7, 1.3], "required": True},
    {"path": "axes.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [-0.48, 2.48], "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "series.ai.color", "label": "AI-led color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.domain.color", "label": "Domain-led color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.group_offset", "label": "Vertical group offset", "group": "Series", "type": "number", "default": 0.12, "min": 0, "max": 0.4, "step": 0.01, "required": True},
    {"path": "series.connector_width", "label": "Connector width", "group": "Series", "type": "number", "default": 1, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "series.marker_size", "label": "Marker size", "group": "Series", "type": "number", "default": 24, "min": 1, "max": 100, "step": 1, "required": True},
    {"path": "series.home_edge_width", "label": "Home marker edge", "group": "Series", "type": "number", "default": 1.1, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "series.outside_edge_width", "label": "Outside marker edge", "group": "Series", "type": "number", "default": 0.35, "min": 0, "max": 5, "step": 0.05, "required": True},
    {"path": "annotation.vertical_offset", "label": "Value-label offset", "group": "Annotations", "type": "number", "default": 0.07, "min": 0, "max": 0.3, "step": 0.01, "required": True},
    {"path": "annotation.font_size", "label": "Value-label size", "group": "Annotations", "type": "number", "default": 6.3, "min": 4, "max": 20, "step": 0.1, "required": True},
    {"path": "reference.x", "label": "Reference level", "group": "Reference", "type": "number", "default": 1, "min": 0, "max": 2, "step": 0.05, "required": True},
    {"path": "reference.color", "label": "Reference color", "group": "Reference", "type": "color", "default": "#777777", "required": True},
    {"path": "reference.line_width", "label": "Reference width", "group": "Reference", "type": "number", "default": 0.7, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "legend.labels", "label": "Legend labels", "group": "Legend", "type": "string_list", "default": ["AI Specialist-led", "Domain Specialist-led", "Home mean", "Outside-audience mean"], "required": True},
    {"path": "legend.anchor", "label": "Legend anchor", "group": "Legend", "type": "number_pair", "default": [0.5, 0.985], "min": -1, "max": 2, "step": 0.01, "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7, "min": 4, "max": 24, "step": 0.1, "required": True},
    {"path": "legend.handle_length", "label": "Legend handle length", "group": "Legend", "type": "number", "default": 1.35, "min": 0, "max": 5, "step": 0.05, "required": True},
    {"path": "legend.handle_text_pad", "label": "Legend handle-text pad", "group": "Legend", "type": "number", "default": 0.55, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "legend.column_spacing", "label": "Legend column spacing", "group": "Legend", "type": "number", "default": 0.9, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "legend.label_spacing", "label": "Legend label spacing", "group": "Legend", "type": "number", "default": 0.35, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [3.8, 2.4], "figure.facecolor": "#FFFFFF",
    "layout.left": 0.31, "layout.right": 0.98, "layout.bottom": 0.2, "layout.top": 0.73,
    "axes.x_label": "Mean normalized citations",
    "axes.y_tick_labels": ["All outside", "Outside w/o CS", "Computer Science"],
    "axes.x_range": [0.7, 1.3], "axes.y_range": [-0.48, 2.48], "axes.spine_width": 0.6,
    "series.ai.color": "#3B6FB6", "series.domain.color": "#D55E5E",
    "series.group_offset": 0.12, "series.connector_width": 1, "series.marker_size": 24,
    "series.home_edge_width": 1.1, "series.outside_edge_width": 0.35,
    "annotation.vertical_offset": 0.07, "annotation.font_size": 6.3,
    "reference.x": 1, "reference.color": "#777777", "reference.line_width": 0.7,
    "legend.labels": ["AI Specialist-led", "Domain Specialist-led", "Home mean", "Outside-audience mean"],
    "legend.anchor": [0.5, 0.985], "legend.font_size": 7, "legend.handle_length": 1.35,
    "legend.handle_text_pad": 0.55, "legend.column_spacing": 0.9, "legend.label_spacing": 0.35,
    "typography.font_family": "Arial", "typography.axis_label_size": 9,
    "typography.tick_label_size": 8, "typography.tick_width": 0.6,
    "typography.tick_length": 3,
}

_CSV_GZIP_B64 = "H4sIAAAAAAAAA4WRTW7DIBCF9z6FD2DRGX4GZhmli3bVRQ5gIZsFkm0q/6hST1+iNFVkO+4GPeDNvG+gC74NY910fpqqtMxTbEPtlzaGoQnVn+iDH+ohjb3v4ndo6ybOfo5pmIrTe3XquvK3tHpLfahAOEByVmqtpXPAuLY9ahRAYAkNKLIKFbniNfU+DtvGKBANo7WSFFtppN6zPmoQTBa1Q2KDDgH4ivJxuy2/XlJ5vhxBr5yrba7RiohRapJkpZV3nr2E5/THKfmBnDY5AECrnKHoSnZO/ecyh7G8NLc/Ophi490coJAIDAotgzEGme5s+znPZ/k/KzM64yQqA8x5sar4AZDGBrmHAgAA"


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
    audience_keys = ["All outside", "Outside w/o CS", "Computer Science"]
    audience_labels = s["axes.y_tick_labels"]
    base_positions = np.arange(len(audience_keys))[::-1]
    colors = {"AI": s["series.ai.color"], "Domain": s["series.domain.color"]}
    fig, ax = plt.subplots(figsize=s["figure.size"], facecolor=s["figure.facecolor"])
    text_items = []
    for base_y, audience in zip(base_positions, audience_keys):
        for leader, sign in [("AI", 1), ("Domain", -1)]:
            subset = data[(data["leader_class"] == leader) & (data["outside_audience"] == audience)]
            home = float(subset.loc[subset["audience"] == "Home", "mean_normalized_citations"].iloc[0])
            outside = float(subset.loc[subset["audience"] == audience, "mean_normalized_citations"].iloc[0])
            y = base_y + sign * s["series.group_offset"]
            ax.plot([home, outside], [y, y], color=colors[leader],
                    lw=s["series.connector_width"], zorder=1)
            ax.scatter(home, y, s=s["series.marker_size"], facecolor="white",
                       edgecolor=colors[leader], linewidth=s["series.home_edge_width"], zorder=3)
            ax.scatter(outside, y, s=s["series.marker_size"], facecolor=colors[leader],
                       edgecolor="white", linewidth=s["series.outside_edge_width"], zorder=3)
            text_offset = sign * s["annotation.vertical_offset"]
            vertical_align = "bottom" if leader == "AI" else "top"
            home_x, outside_x = home, outside
            home_ha = outside_ha = "center"
            if abs(home - outside) < 0.075:
                midpoint = (home + outside) / 2
                home_x += -0.008 if home < midpoint else 0.008
                outside_x += -0.008 if outside < midpoint else 0.008
                home_ha = "right" if home < midpoint else "left"
                outside_ha = "right" if outside < midpoint else "left"
            text_items.append(ax.text(home_x, y + text_offset, f"{home:.2f}", color=colors[leader],
                                      fontsize=s["annotation.font_size"], ha=home_ha, va=vertical_align))
            text_items.append(ax.text(outside_x, y + text_offset, f"{outside:.2f}", color=colors[leader],
                                      fontsize=s["annotation.font_size"], ha=outside_ha, va=vertical_align))
    ax.axvline(s["reference.x"], color=s["reference.color"],
               lw=s["reference.line_width"], ls="--", zorder=0)
    ax.set_yticks(base_positions, audience_labels)
    ax.set_xlim(s["axes.x_range"])
    ax.set_ylim(s["axes.y_range"])
    ax.set_xlabel(s["axes.x_label"], fontsize=s["typography.axis_label_size"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    for spine in ax.spines.values():
        spine.set_linewidth(s["axes.spine_width"])
    ax.tick_params(axis="y", length=0, labelsize=s["typography.tick_label_size"])
    ax.tick_params(axis="x", direction="out", labelsize=s["typography.tick_label_size"],
                   width=s["typography.tick_width"], length=s["typography.tick_length"])
    legend_labels = s["legend.labels"]
    legend = fig.legend(handles=[
        Line2D([0], [0], color=colors["AI"], lw=1.2, label=legend_labels[0]),
        Line2D([0], [0], color=colors["Domain"], lw=1.2, label=legend_labels[1]),
        Line2D([0], [0], marker="o", color="#555555", lw=0, markerfacecolor="white",
               markeredgewidth=1, markersize=4.5, label=legend_labels[2]),
        Line2D([0], [0], marker="o", color="#555555", lw=0, markerfacecolor="#555555",
               markersize=4.5, label=legend_labels[3]),
    ], frameon=False, loc="upper center", bbox_to_anchor=s["legend.anchor"], ncol=2,
       fontsize=s["legend.font_size"], handlelength=s["legend.handle_length"],
       handletextpad=s["legend.handle_text_pad"], columnspacing=s["legend.column_spacing"],
       labelspacing=s["legend.label_spacing"])
    for item in [ax.xaxis.label, *ax.get_xticklabels(), *ax.get_yticklabels(),
                 *legend.get_texts(), *text_items]:
        item.set_fontfamily(s["typography.font_family"])
    fig.subplots_adjust(left=s["layout.left"], right=s["layout.right"],
                        bottom=s["layout.bottom"], top=s["layout.top"])
    return fig
