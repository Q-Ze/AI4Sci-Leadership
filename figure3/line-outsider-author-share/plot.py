"""Matplot Studio conversion of complementary-specialist author shares."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "line-outsider-author-share",
    "name": "Outsider author share",
    "description": "EWMA-smoothed complementary-Specialist shares in AI-led and Domain-led AI4Sci teams.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original result table is embedded; the upstream database query is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Year", "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Share of outsider authors", "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2024], "required": True},
    {"path": "axes.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0.1, 0.5], "required": True},
    {"path": "axes.x_tick_interval", "label": "X tick interval", "group": "Axes", "type": "number", "default": 10, "min": 1, "max": 30, "step": 1, "required": True},
    {"path": "axes.y_tick_interval", "label": "Y tick interval", "group": "Axes", "type": "number", "default": 0.1, "min": 0.01, "max": 1, "step": 0.01, "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "series.ai_led.color", "label": "AI-led line color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.domain_led.color", "label": "Domain-led line color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.line_width", "label": "Line width", "group": "Series", "type": "number", "default": 1.3, "min": 0.1, "max": 8, "step": 0.05, "required": True},
    {"path": "annotation.labels", "label": "Line labels", "group": "Annotations", "type": "string_list", "default": ["Domain Specialists\nin AI-led teams", "AI Specialists\nin Domain-led teams"], "required": True},
    {"path": "annotation.ai_led_offset", "label": "AI-led label offset", "group": "Annotations", "type": "number_pair", "default": [-20, 8], "min": -50, "max": 50, "step": 1, "required": True},
    {"path": "annotation.domain_led_offset", "label": "Domain-led label offset", "group": "Annotations", "type": "number_pair", "default": [-20, -8], "min": -50, "max": 50, "step": 1, "required": True},
    {"path": "annotation.font_size", "label": "Label font size", "group": "Annotations", "type": "number", "default": 7.2, "min": 4, "max": 24, "step": 0.1, "required": True},
    {"path": "annotation.background", "label": "Label background", "group": "Annotations", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "annotation.background_alpha", "label": "Label background opacity", "group": "Annotations", "type": "number", "default": 0.82, "min": 0, "max": 1, "step": 0.01, "required": True},
    {"path": "annotation.background_pad", "label": "Label background padding", "group": "Annotations", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [3.8, 2.4], "figure.facecolor": "#FFFFFF",
    "axes.x_label": "Year", "axes.y_label": "Share of outsider authors",
    "axes.x_range": [1995, 2024], "axes.y_range": [0.1, 0.5],
    "axes.x_tick_interval": 10, "axes.y_tick_interval": 0.1,
    "axes.grid": False, "axes.spine_width": 0.6,
    "series.ai_led.color": "#D55E5E", "series.domain_led.color": "#3B6FB6",
    "series.line_width": 1.3,
    "annotation.labels": ["Domain Specialists\nin AI-led teams", "AI Specialists\nin Domain-led teams"],
    "annotation.ai_led_offset": [-20, 8], "annotation.domain_led_offset": [-20, -8],
    "annotation.font_size": 7.2, "annotation.background": "#FFFFFF",
    "annotation.background_alpha": 0.82, "annotation.background_pad": 0.6,
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
    labels = s["annotation.labels"]
    specs = [
        ("AI", s["series.ai_led.color"], labels[0], s["annotation.ai_led_offset"], "top"),
        ("Domain", s["series.domain_led.color"], labels[1], s["annotation.domain_led_offset"], "bottom"),
    ]
    text_items = []
    for leader_class, color, label, offset, vertical_alignment in specs:
        subset = data[data["leader_class"] == leader_class]
        ax.plot(subset["year"], subset["complementary_share_ewma5"],
                color=color, lw=s["series.line_width"])
        last = subset.sort_values("year").iloc[-1]
        text_items.append(ax.annotate(
            label, xy=(last["year"], last["complementary_share_ewma5"]),
            xytext=offset, textcoords="offset points", ha="right", va=vertical_alignment,
            color=color, fontsize=s["annotation.font_size"],
            bbox={"facecolor": s["annotation.background"], "edgecolor": "none",
                  "alpha": s["annotation.background_alpha"], "pad": s["annotation.background_pad"]}))
    ax.set(xlabel=s["axes.x_label"], ylabel=s["axes.y_label"],
           xlim=s["axes.x_range"], ylim=s["axes.y_range"])
    ax.xaxis.set_major_locator(MultipleLocator(s["axes.x_tick_interval"]))
    ax.yaxis.set_major_locator(MultipleLocator(s["axes.y_tick_interval"]))
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.xaxis.label.set_size(s["typography.axis_label_size"])
    ax.yaxis.label.set_size(s["typography.axis_label_size"])
    ax.tick_params(labelsize=s["typography.tick_label_size"], direction="out",
                   width=s["typography.tick_width"], length=s["typography.tick_length"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for spine in ax.spines.values():
        spine.set_linewidth(s["axes.spine_width"])
    ax.grid(s["axes.grid"])
    for item in [ax.xaxis.label, ax.yaxis.label, *ax.get_xticklabels(), *ax.get_yticklabels(), *text_items]:
        item.set_fontfamily(s["typography.font_family"])
    fig.tight_layout()
    return fig
