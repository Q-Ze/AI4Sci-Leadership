"""Matplot Studio conversion of global-normalized citation entropy."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, MultipleLocator
import pandas as pd


PLOT_META = {
    "id": "line-entropy-global",
    "name": "Global-normalized cited-knowledge diversity",
    "description": "EWMA-smoothed cited-work entropy for AI and Domain papers, with a Domain-minus-AI inset.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original all-metrics result table is embedded; the entropy query is not rerun. The inset gap is recomputed from these values.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result; inset values are derived during rendering."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "AI4Sci publication year", "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Diversity of cited knowledge", "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2024], "required": True},
    {"path": "axes.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0.5, 0.9], "required": True},
    {"path": "axes.x_tick_interval", "label": "X tick interval", "group": "Axes", "type": "number", "default": 10, "min": 1, "max": 30, "step": 1, "required": True},
    {"path": "axes.y_tick_interval", "label": "Y tick interval", "group": "Axes", "type": "number", "default": 0.1, "min": 0.01, "max": 1, "step": 0.01, "required": True},
    {"path": "axes.y_decimals", "label": "Y tick decimals", "group": "Axes", "type": "integer", "default": 1, "min": 0, "max": 4, "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "series.ai.color", "label": "AI papers color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.domain.color", "label": "Domain papers color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.line_width", "label": "Line width", "group": "Series", "type": "number", "default": 1.3, "min": 0.1, "max": 8, "step": 0.05, "required": True},
    {"path": "legend.labels", "label": "Legend labels", "group": "Legend", "type": "string_list", "default": ["AI papers", "Domain papers"], "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.2, "min": 4, "max": 24, "step": 0.1, "required": True},
    {"path": "legend.handle_length", "label": "Legend handle length", "group": "Legend", "type": "number", "default": 1.8, "min": 0, "max": 8, "step": 0.1, "required": True},
    {"path": "legend.label_spacing", "label": "Legend label spacing", "group": "Legend", "type": "number", "default": 0.3, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "legend.border_axes_pad", "label": "Legend axes padding", "group": "Legend", "type": "number", "default": 0.2, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "inset.origin", "label": "Inset origin", "group": "Inset", "type": "number_pair", "default": [0.53, 0.095], "min": 0, "max": 1, "step": 0.005, "required": True},
    {"path": "inset.size", "label": "Inset size", "group": "Inset", "type": "number_pair", "default": [0.42, 0.27], "min": 0.05, "max": 1, "step": 0.005, "required": True},
    {"path": "inset.y_label", "label": "Inset Y-axis label", "group": "Inset", "type": "string", "default": "Domain − AI", "required": True},
    {"path": "inset.y_range", "label": "Inset Y-axis range", "group": "Inset", "type": "number_pair", "default": [-0.05, 0.05], "required": True},
    {"path": "inset.color", "label": "Inset line color", "group": "Inset", "type": "color", "default": "#7A5195", "required": True},
    {"path": "inset.line_width", "label": "Inset line width", "group": "Inset", "type": "number", "default": 1.15, "min": 0.1, "max": 8, "step": 0.05, "required": True},
    {"path": "inset.zero_color", "label": "Inset zero-line color", "group": "Inset", "type": "color", "default": "#777777", "required": True},
    {"path": "inset.zero_line_width", "label": "Inset zero-line width", "group": "Inset", "type": "number", "default": 0.6, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "inset.facecolor", "label": "Inset background", "group": "Inset", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "inset.label_size", "label": "Inset label size", "group": "Inset", "type": "number", "default": 6.5, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "inset.tick_size", "label": "Inset tick size", "group": "Inset", "type": "number", "default": 6, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "inset.tick_width", "label": "Inset tick width", "group": "Inset", "type": "number", "default": 0.55, "min": 0, "max": 5, "step": 0.05, "required": True},
    {"path": "inset.tick_length", "label": "Inset tick length", "group": "Inset", "type": "number", "default": 2.2, "min": 0, "max": 10, "step": 0.1, "required": True},
    {"path": "inset.spine_width", "label": "Inset spine width", "group": "Inset", "type": "number", "default": 0.55, "min": 0, "max": 5, "step": 0.05, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [3.8, 2.4], "figure.facecolor": "#FFFFFF",
    "axes.x_label": "AI4Sci publication year", "axes.y_label": "Diversity of cited knowledge",
    "axes.x_range": [1995, 2024], "axes.y_range": [0.5, 0.9],
    "axes.x_tick_interval": 10, "axes.y_tick_interval": 0.1, "axes.y_decimals": 1,
    "axes.grid": False, "axes.spine_width": 0.6,
    "series.ai.color": "#3B6FB6", "series.domain.color": "#D55E5E", "series.line_width": 1.3,
    "legend.labels": ["AI papers", "Domain papers"], "legend.font_size": 7.2,
    "legend.handle_length": 1.8, "legend.label_spacing": 0.3, "legend.border_axes_pad": 0.2,
    "inset.origin": [0.53, 0.095], "inset.size": [0.42, 0.27],
    "inset.y_label": "Domain − AI", "inset.y_range": [-0.05, 0.05],
    "inset.color": "#7A5195", "inset.line_width": 1.15,
    "inset.zero_color": "#777777", "inset.zero_line_width": 0.6,
    "inset.facecolor": "#FFFFFF", "inset.label_size": 6.5, "inset.tick_size": 6,
    "inset.tick_width": 0.55, "inset.tick_length": 2.2, "inset.spine_width": 0.55,
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


def _gap_data(data):
    pivot = data.pivot(index="year", columns="cited_type", values="entropy_global").rename_axis(None, axis=1)
    gap = pivot.index.to_frame(index=False).assign(gap_global=pivot["Domain"].values - pivot["AI"].values)
    gap["gap_global_ewma5"] = gap["gap_global"].ewm(span=5, adjust=False).mean()
    return gap


def render(data, settings):
    s = _resolved(settings)
    fig, ax = plt.subplots(figsize=s["figure.size"], facecolor=s["figure.facecolor"])
    labels = s["legend.labels"]
    for cited_type, color, label in [("AI", s["series.ai.color"], labels[0]),
                                      ("Domain", s["series.domain.color"], labels[1])]:
        subset = data[data["cited_type"] == cited_type]
        ax.plot(subset["year"], subset["entropy_global_ewma5"],
                color=color, lw=s["series.line_width"], label=label)
    ax.set(xlabel=s["axes.x_label"], ylabel=s["axes.y_label"],
           xlim=s["axes.x_range"], ylim=s["axes.y_range"])
    ax.xaxis.set_major_locator(MultipleLocator(s["axes.x_tick_interval"]))
    ax.yaxis.set_major_locator(MultipleLocator(s["axes.y_tick_interval"]))
    ax.yaxis.set_major_formatter(FormatStrFormatter(f"%.{s['axes.y_decimals']}f"))
    origin, size = s["inset.origin"], s["inset.size"]
    inset = ax.inset_axes([origin[0], origin[1], size[0], size[1]])
    gap = _gap_data(data)
    inset.axhline(0, color=s["inset.zero_color"], lw=s["inset.zero_line_width"])
    inset.plot(gap["year"], gap["gap_global_ewma5"], color=s["inset.color"], lw=s["inset.line_width"])
    inset.set(xlim=s["axes.x_range"], ylim=s["inset.y_range"], ylabel=s["inset.y_label"])
    inset.set_yticks([-0.05, 0, 0.05])
    inset.xaxis.set_major_locator(MultipleLocator(s["axes.x_tick_interval"]))
    inset.xaxis.label.set_visible(False)
    inset.yaxis.label.set_size(s["inset.label_size"])
    inset.tick_params(labelsize=s["inset.tick_size"], width=s["inset.tick_width"], length=s["inset.tick_length"])
    inset.spines["top"].set_visible(False)
    inset.spines["right"].set_visible(False)
    inset.spines["left"].set_linewidth(s["inset.spine_width"])
    inset.spines["bottom"].set_linewidth(s["inset.spine_width"])
    inset.set_facecolor(s["inset.facecolor"])
    inset.grid(False)
    legend = ax.legend(frameon=False, fontsize=s["legend.font_size"],
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
    for item in [ax.xaxis.label, ax.yaxis.label, inset.yaxis.label,
                 *ax.get_xticklabels(), *ax.get_yticklabels(),
                 *inset.get_xticklabels(), *inset.get_yticklabels(), *legend.get_texts()]:
        item.set_fontfamily(s["typography.font_family"])
    fig.tight_layout()
    return fig
