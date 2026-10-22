"""Matplot Studio density figure corresponding to the Figure 3b ECDF."""

from __future__ import annotations

import base64
import zlib
from csv import DictReader
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
import pandas as pd


PLOT_META = {
    "id": "fig-1-d-career-age-density",
    "name": "Figure 1d — Common-window career-age density",
    "description": "Author-level density of career age at first AI4Sci paper after restricting career starts to 1995 or later.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The exact 60-row by 8-column plotting table is embedded as zlib-level-9 compressed, base64-encoded CSV. Career start is the first OpenAlex publication year; entry age is first AI4Sci year minus career start. Each researcher appears once. The displayed density uses a one-year Gaussian bandwidth with reflective boundary handling and is renormalized within each group. Group totals are 336,289 AI Specialists and 759,877 Domain Specialists.",
    "data_export": {"csv": True, "json": True, "note": "Decoded counts plus raw probabilities and derived smoothed densities."},
}

PLOT_SCHEMA = [
    {'path': 'layout.mode', 'label': '布局模式', 'group': '坐标轴对齐', 'type': 'select', 'default': 'auto', 'options': [{'value': 'auto', 'label': '自动布局（原外观）'}, {'value': 'fixed', 'label': '固定边距（用于对齐）'}], 'required': True},
    {'path': 'layout.left_mm', 'label': '左边距 / Y 轴位置（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 13.864167, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.right_mm', 'label': '右边距（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 3.048, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.bottom_mm', 'label': '下边距 / X 轴位置（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 12.702756, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.top_mm', 'label': '上边距（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 4.075327, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'axes.main.x_label_pad', 'label': 'X 轴标题间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 4, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.x_tick_pad', 'label': 'X 刻度文字间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 3.5, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.y_label_pad', 'label': 'Y 轴标题间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 4, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.y_tick_pad', 'label': 'Y 刻度文字间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 3.5, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},

    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.80, 2.40], "min": 1.5, "max": 12, "step": 0.01, "required": True},
    {"path": "figure.facecolor", "label": "Background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.main.title", "label": "Title", "group": "Axes", "type": "string", "default": "", "required": True},
    {"path": "axes.main.title_size", "label": "Title size", "group": "Axes", "type": "number", "default": 9, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "axes.main.title_pad", "label": "Title padding", "group": "Axes", "type": "number", "default": 4, "min": 0, "max": 30, "step": 0.5, "required": True},
    {"path": "axes.main.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Career age at first AI4Sci paper (years)", "required": True},
    {"path": "axes.main.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Density", "required": True},
    {"path": "axes.main.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [0, 29], "min": 0, "max": 80, "step": 1, "required": True},
    {"path": "axes.main.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0, 0.40], "min": 0, "max": 1, "step": 0.01, "required": True},
    {"path": "axes.main.x_tick_step", "label": "X tick interval", "group": "Axes", "type": "number", "default": 5, "min": 1, "max": 20, "step": 1, "required": True},
    {"path": "axes.main.y_tick_step", "label": "Y tick interval", "group": "Axes", "type": "number", "default": 0.10, "min": 0.01, "max": 0.5, "step": 0.01, "required": True},
    {"path": "axes.main.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 3, "step": 0.1, "required": True},
    {"path": "axes.main.tick_length", "label": "Tick length", "group": "Axes", "type": "number", "default": 3, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "series.ai.color", "label": "AI Specialist color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.domain.color", "label": "Domain Specialist color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.linewidth", "label": "Density-line width", "group": "Series", "type": "number", "default": 1.5, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "series.linestyle", "label": "Density-line style", "group": "Series", "type": "select", "default": "-", "options": ["-", "--", ":", "-."], "required": True},
    {"path": "series.fill_alpha", "label": "Density-fill opacity", "group": "Series", "type": "number", "default": 0.16, "min": 0, "max": 1, "step": 0.01, "required": True},
    {"path": "median.visible", "label": "Show medians", "group": "Median markers", "type": "boolean", "default": True, "required": True},
    {"path": "median.linewidth", "label": "Median-line width", "group": "Median markers", "type": "number", "default": 0.8, "min": 0.1, "max": 3, "step": 0.1, "required": True},
    {"path": "median.linestyle", "label": "Median-line style", "group": "Median markers", "type": "select", "default": ":", "options": ["-", "--", ":", "-."], "required": True},
    {"path": "annotation.ai_median.text", "label": "AI median label", "group": "Median labels", "type": "string", "default": "Median: 1 y", "required": True},
    {"path": "annotation.ai_median.offset", "label": "AI median-label offset", "group": "Median labels", "type": "number_pair", "default": [4, 3], "min": -50, "max": 50, "step": 1, "required": True},
    {"path": "annotation.domain_median.text", "label": "Domain median label", "group": "Median labels", "type": "string", "default": "Median: 5 y", "required": True},
    {"path": "annotation.domain_median.offset", "label": "Domain median-label offset", "group": "Median labels", "type": "number_pair", "default": [4, 3], "min": -50, "max": 50, "step": 1, "required": True},
    {"path": "annotation.median_font_size", "label": "Median-label size", "group": "Median labels", "type": "number", "default": 6.5, "min": 4, "max": 16, "step": 0.1, "required": True},
    {"path": "legend.visible", "label": "Show legend", "group": "Legend", "type": "boolean", "default": True, "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "default": "upper right", "options": ["upper right", "upper left", "lower right", "lower left", "best"], "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.2, "min": 4, "max": 16, "step": 0.1, "required": True},
    {"path": "legend.frame", "label": "Legend frame", "group": "Legend", "type": "boolean", "default": False, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.label_size", "label": "Axis-label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "typography.tick_size", "label": "Tick-label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 20, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {'layout.mode': 'fixed',
 'layout.left_mm': 18,
 'layout.right_mm': 4,
 'layout.bottom_mm': 14,
 'layout.top_mm': 5,
 'axes.main.x_label_pad': 4,
 'axes.main.x_tick_pad': 3.5,
 'axes.main.y_label_pad': 4,
 'axes.main.y_tick_pad': 3.5,
 'figure.size': [2.67, 2.4],
 'figure.facecolor': '#FFFFFF',
 'axes.main.title': '',
 'axes.main.title_size': 9,
 'axes.main.title_pad': 4,
 'axes.main.x_label': 'Career age',
 'axes.main.y_label': 'Density',
 'axes.main.x_range': [0, 29],
 'axes.main.y_range': [0, 0.4],
 'axes.main.x_tick_step': 5,
 'axes.main.y_tick_step': 0.1,
 'axes.main.spine_width': 0.6,
 'axes.main.tick_length': 3,
 'series.ai.color': '#3B6FB6',
 'series.domain.color': '#D55E5E',
 'series.linewidth': 1.5,
 'series.linestyle': '-',
 'series.fill_alpha': 0.16,
 'median.visible': True,
 'median.linewidth': 0.8,
 'median.linestyle': ':',
 'annotation.ai_median.text': 'AI-origin\nMedian: 1 year',
 'annotation.ai_median.offset': [4, 3],
 'annotation.domain_median.text': 'Domain-origin\nMedian: 5 years',
 'annotation.domain_median.offset': [4, 3],
 'annotation.median_font_size': 6.5,
 'legend.visible': False,
 'legend.location': 'upper right',
 'legend.font_size': 7.2,
 'legend.frame': False,
 'typography.font_family': 'Arial',
 'typography.label_size': 9,
 'typography.tick_size': 8}

_DATA_ZLIB_BASE64 = (
    "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"
)

_BANDWIDTH_YEARS = 1.0


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


def prepare_data():
    csv_text = zlib.decompress(base64.b64decode(_DATA_ZLIB_BASE64)).decode("utf-8")
    rows = []
    for row in DictReader(StringIO(csv_text)):
        if not row or "leader_class" not in row:
            continue
        rows.append({
            "leader_class": row["leader_class"],
            "career_age": int(row["career_age"]),
            "n": int(row["n"]),
            "total": int(row["total"]),
            "cdf": float(row["cdf"]),
            "probability": float(row["probability"]),
            "smoothed_density": float(row["smoothed_density"]),
            "bandwidth_years": float(row["bandwidth_years"]),
        })
    return pd.DataFrame(rows)


def _median_age(group):
    return float(group.loc[group.cdf.ge(0.5), "career_age"].iloc[0])


def _apply_axis_alignment(fig, ax, config):
    """Keep the original auto layout, or place axes at physical canvas margins."""
    ax.xaxis.labelpad = config["axes.main.x_label_pad"]
    ax.yaxis.labelpad = config["axes.main.y_label_pad"]
    ax.tick_params(axis="x", which="major", pad=config["axes.main.x_tick_pad"])
    ax.tick_params(axis="y", which="major", pad=config["axes.main.y_tick_pad"])
    if config["layout.mode"] == "auto":
        fig.tight_layout()
        return
    width_mm, height_mm = fig.get_size_inches() * 25.4
    left = config["layout.left_mm"]
    right = config["layout.right_mm"]
    bottom = config["layout.bottom_mm"]
    top = config["layout.top_mm"]
    if min(left, right, bottom, top) < 0 or left + right >= width_mm or bottom + top >= height_mm:
        raise ValueError("固定边距无效：左右边距之和须小于画布宽度，上下边距之和须小于画布高度。请减小边距或增大画布。")
    fig.set_layout_engine(None)
    fig.subplots_adjust(left=left / width_mm, right=1 - right / width_mm,
                        bottom=bottom / height_mm, top=1 - top / height_mm)


def render(data, settings):
    c = _resolved(settings)
    style = {
        "font.family": c["typography.font_family"], "font.size": 8,
        "axes.labelsize": c["typography.label_size"],
        "xtick.labelsize": c["typography.tick_size"],
        "ytick.labelsize": c["typography.tick_size"],
        "axes.linewidth": c["axes.main.spine_width"],
        "xtick.major.width": c["axes.main.spine_width"],
        "ytick.major.width": c["axes.main.spine_width"],
        "xtick.major.size": c["axes.main.tick_length"],
        "ytick.major.size": c["axes.main.tick_length"],
    }
    with plt.rc_context(style):
        return _draw(data, c)


def _draw(data, c):
    fig, ax = plt.subplots(figsize=tuple(c["figure.size"]), facecolor=c["figure.facecolor"])
    ax.set_facecolor(c["figure.facecolor"])
    labels = {"AI": "AI Specialists", "Domain": "Domain Specialists"}
    for leader in ("AI", "Domain"):
        key = leader.lower()
        color = c[f"series.{key}.color"]
        group = data.loc[data.leader_class.eq(leader)].sort_values("career_age")
        x = group["career_age"].to_numpy(dtype=float)
        y = group["smoothed_density"].to_numpy(dtype=float)
        ax.fill_between(x, 0, y, color=color, alpha=c["series.fill_alpha"], linewidth=0)
        ax.plot(x, y, color=color, lw=c["series.linewidth"],
                ls=c["series.linestyle"], label=labels[leader])
        if c["median.visible"]:
            median = _median_age(group)
            height = float(np.interp(median, x, y))
            ax.vlines(median, 0, height, color=color,
                      lw=c["median.linewidth"], ls=c["median.linestyle"])
            annotation_key = f"annotation.{key}_median"
            ax.annotate(c[f"{annotation_key}.text"], xy=(median, height),
                        xytext=tuple(c[f"{annotation_key}.offset"]),
                        textcoords="offset points", ha="left", va="bottom",
                        color=color, family=c["typography.font_family"],
                        fontsize=c["annotation.median_font_size"])
    if c["axes.main.title"]:
        ax.set_title(c["axes.main.title"], family=c["typography.font_family"],
                     fontsize=c["axes.main.title_size"], pad=c["axes.main.title_pad"])
    ax.set_xlabel(c["axes.main.x_label"], family=c["typography.font_family"],
                  fontsize=c["typography.label_size"])
    ax.set_ylabel(c["axes.main.y_label"], family=c["typography.font_family"],
                  fontsize=c["typography.label_size"])
    ax.set_xlim(*c["axes.main.x_range"])
    ax.set_ylim(*c["axes.main.y_range"])
    ax.xaxis.set_major_locator(MultipleLocator(c["axes.main.x_tick_step"]))
    ax.yaxis.set_major_locator(MultipleLocator(c["axes.main.y_tick_step"]))
    ax.tick_params(labelsize=c["typography.tick_size"], direction="out",
                   width=c["axes.main.spine_width"], length=c["axes.main.tick_length"])
    for tick in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        tick.set_fontfamily(c["typography.font_family"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(c["axes.main.spine_width"])
    ax.spines["bottom"].set_linewidth(c["axes.main.spine_width"])
    ax.grid(False)
    if c["legend.visible"]:
        ax.legend(frameon=c["legend.frame"], loc=c["legend.location"],
                  prop={"family": c["typography.font_family"],
                        "size": c["legend.font_size"]})
    _apply_axis_alignment(fig, ax, c)
    return fig
