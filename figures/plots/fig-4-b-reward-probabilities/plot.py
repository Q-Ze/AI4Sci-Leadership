"""Matplot Studio figure for Figure 4b."""

from __future__ import annotations

from csv import DictReader
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd


PLOT_META = {
    "id": "fig-4-b-reward-probabilities",
    "name": "Figure 4b — Raw and adjusted reward probabilities",
    "description": "Raw and year- plus field-adjusted NIH, NSF, and news probabilities for AI-led and Domain-led AI4Sci papers.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "Complete raw probabilities and adjusted marginal probabilities with 95% confidence intervals.",
    "data_export": {"csv": True, "json": True, "note": "Complete embedded plotting table."},
}

PLOT_SCHEMA = [
    {'path': 'layout.mode', 'label': '布局模式', 'group': '坐标轴对齐', 'type': 'select', 'default': 'auto', 'options': [{'value': 'auto', 'label': '自动布局（原外观）'}, {'value': 'fixed', 'label': '固定边距（毫米）'}], 'required': True},
    {'path': 'layout.left_mm', 'label': '左边距 / Y 轴位置（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 16.404167, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.right_mm', 'label': '右边距（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 3.048, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.bottom_mm', 'label': '下边距 / X 轴位置（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 7.989645, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.top_mm', 'label': '上边距（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 3.048, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'axes.main.x_label_pad', 'label': 'X 轴标题间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 4.0, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.y_label_pad', 'label': 'Y 轴标题间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 4.0, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.x_tick_pad', 'label': 'X 刻度文字间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 3.5, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.y_tick_pad', 'label': 'Y 刻度文字间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 3.5, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},

    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.80, 2.40], "min": 1.5, "max": 12, "step": 0.01, "required": True},
    {"path": "figure.facecolor", "label": "Background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.main.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Outcome probability", "required": True},
    {"path": "axes.main.x_labels", "label": "Outcome labels", "group": "Axes", "type": "string_list", "default": ["NIH", "NSF", "News"], "required": True},
    {"path": "axes.main.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0, 0.0145], "min": 0, "max": 0.1, "step": 0.0005, "required": True},
    {"path": "axes.main.y_percent_decimals", "label": "Y tick decimals", "group": "Axes", "type": "integer", "default": 1, "min": 0, "max": 3, "step": 1, "required": True},
    {"path": "axes.main.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 3, "step": 0.1, "required": True},
    {"path": "axes.main.tick_length", "label": "Tick length", "group": "Axes", "type": "number", "default": 3, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "bars.width", "label": "Bar width", "group": "Raw bars", "type": "number", "default": 0.34, "min": 0.05, "max": 0.9, "step": 0.01, "required": True},
    {"path": "bars.ai.color", "label": "AI-led raw color", "group": "Raw bars", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "bars.domain.color", "label": "Domain-led raw color", "group": "Raw bars", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "adjusted.marker_shape", "label": "Adjusted marker shape", "group": "Adjusted estimates", "type": "select", "default": "D", "options": ["o", "s", "D", "^", "v", "X"], "required": True},
    {"path": "adjusted.marker_size", "label": "Adjusted marker size", "group": "Adjusted estimates", "type": "number", "default": 3.6, "min": 0.5, "max": 15, "step": 0.1, "required": True},
    {"path": "adjusted.marker_facecolor", "label": "Marker fill", "group": "Adjusted estimates", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "adjusted.color", "label": "Marker and interval color", "group": "Adjusted estimates", "type": "color", "default": "#202020", "required": True},
    {"path": "adjusted.linewidth", "label": "Error-bar width", "group": "Adjusted estimates", "type": "number", "default": 0.8, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "adjusted.capsize", "label": "Error-bar cap size", "group": "Adjusted estimates", "type": "number", "default": 2, "min": 0, "max": 15, "step": 0.5, "required": True},
    {"path": "legend.ai_label", "label": "AI-led raw label", "group": "Legend", "type": "string", "default": "AI-led (Raw)", "required": True},
    {"path": "legend.domain_label", "label": "Domain-led raw label", "group": "Legend", "type": "string", "default": "Domain-led (Raw)", "required": True},
    {"path": "legend.adjusted_label", "label": "Adjusted label", "group": "Legend", "type": "string", "default": "Adjusted", "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "default": "upper left", "options": ["upper left", "upper right", "lower left", "lower right", "best"], "required": True},
    {"path": "legend.columns", "label": "Legend columns", "group": "Legend", "type": "integer", "default": 1, "min": 1, "max": 3, "step": 1, "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 6.7, "min": 4, "max": 16, "step": 0.1, "required": True},
    {"path": "legend.frame", "label": "Legend frame", "group": "Legend", "type": "boolean", "default": False, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.label_size", "label": "Axis-label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "typography.tick_size", "label": "Tick-label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 20, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {'layout.mode': 'fixed',
 'layout.left_mm': 18,
 'layout.right_mm': 4,
 'layout.bottom_mm': 15,
 'layout.top_mm': 5,
 'axes.main.x_label_pad': 4.0,
 'axes.main.y_label_pad': 4.0,
 'axes.main.x_tick_pad': 3.5,
 'axes.main.y_tick_pad': 3.5,
 'figure.size': [3.8, 2.4],
 'figure.facecolor': '#FFFFFF',
 'axes.main.y_label': 'Percentage',
 'axes.main.x_labels': ['NIH funding', 'NSF funding', 'News outcome'],
 'axes.main.y_range': [0, 0.0145],
 'axes.main.y_percent_decimals': 1,
 'axes.main.spine_width': 0.6,
 'axes.main.tick_length': 3,
 'bars.width': 0.34,
 'bars.ai.color': '#3B6FB6',
 'bars.domain.color': '#D55E5E',
 'adjusted.marker_shape': 'D',
 'adjusted.marker_size': 3.6,
 'adjusted.marker_facecolor': '#FFFFFF',
 'adjusted.color': '#202020',
 'adjusted.linewidth': 0.8,
 'adjusted.capsize': 2,
 'legend.ai_label': 'AI-led (Raw)',
 'legend.domain_label': 'Domain-led (Raw)',
 'legend.adjusted_label': 'Adjusted',
 'legend.location': 'upper left',
 'legend.columns': 1,
 'legend.font_size': 6.7,
 'legend.frame': False,
 'typography.font_family': 'Arial',
 'typography.label_size': 9,
 'typography.tick_size': 8}

OUTCOMES = ["NIH", "NSF", "News"]


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


_CSV_DATA = """outcome,leader_class,specification,estimate,std_error,ci_low,ci_high
NIH,AI,Raw,0.0019547042430427,8.750674110066331e-05,0.0017831910304854,0.0021262174556
NIH,Domain,Raw,0.006019341652681,0.0001114778978180357,0.0058008449729577,0.0062378383324044
NSF,AI,Raw,0.0115594457746202,0.00021177253740515292,0.0111443716013061,0.0119745199479343
NSF,Domain,Raw,0.0132226117877735,0.00016462414211785702,0.0128999484692225,0.0135452751063245
News,AI,Raw,0.0038230560898064,0.00012226423485604604,0.0035834181894886,0.0040626939901243
News,Domain,Raw,0.0080008640600854,0.00012839538066997453,0.0077492091139722,0.0082525190061985
NIH,AI,Year + field adjusted,0.0025218310618156,0.0002858133255448,0.0019616369437477,0.0030820251798835
NIH,Domain,Year + field adjusted,0.0053827192477236,0.0001961912613184,0.0049981843755393,0.0057672541199078
NSF,AI,Year + field adjusted,0.0124028491330349,0.0004121398387927,0.0115950550490012,0.0132106432170686
NSF,Domain,Year + field adjusted,0.0127637574526752,0.0002769288698413,0.0122209768677862,0.0133065380375642
News,AI,Year + field adjusted,0.0043869044730029,0.00015860510102,0.0040760384750036,0.0046977704710021
News,Domain,Year + field adjusted,0.0074937136888475,0.0001381911536403,0.0072228590277125,0.0077645683499826
"""


def prepare_data():
    rows = []
    for row in DictReader(StringIO(_CSV_DATA)):
        if not row or "outcome" not in row:
            continue
        rows.append({
            "outcome": row["outcome"], "leader_class": row["leader_class"],
            "specification": row["specification"],
            "estimate": float(row["estimate"]),
            "std_error": float(row["std_error"]),
            "ci_low": float(row["ci_low"]), "ci_high": float(row["ci_high"]),
        })
    return pd.DataFrame(rows)


def _apply_axis_alignment(fig, axes, c):
    """Apply main-axis text spacing and optional physical margins; leave insets attached."""
    for axis in axes:
        axis.xaxis.labelpad = c["axes.main.x_label_pad"]
        axis.yaxis.labelpad = c["axes.main.y_label_pad"]
        axis.tick_params(axis="x", which="major", pad=c["axes.main.x_tick_pad"])
        axis.tick_params(axis="y", which="major", pad=c["axes.main.y_tick_pad"])
    if c["layout.mode"] != "fixed":
        fig.tight_layout()
        return
    width_mm, height_mm = fig.get_size_inches() * 25.4
    left, right = c["layout.left_mm"], c["layout.right_mm"]
    bottom, top = c["layout.bottom_mm"], c["layout.top_mm"]
    if min(left, right, bottom, top) < 0 or left + right >= width_mm or bottom + top >= height_mm:
        raise ValueError("固定边距无效：左右边距之和须小于画布宽度，上下边距之和须小于画布高度。")
    fig.set_layout_engine(None)
    fig.subplots_adjust(left=left / width_mm, right=1 - right / width_mm,
                        bottom=bottom / height_mm, top=1 - top / height_mm,
                        wspace=c.get("layout.wspace", 0.2))


def render(data, settings):
    c = _resolved(settings)
    style = {
        "font.family": c["typography.font_family"], "font.size": 8,
        "axes.labelsize": c["typography.label_size"],
        "xtick.labelsize": c["typography.tick_size"],
        "ytick.labelsize": c["typography.tick_size"],
        "legend.fontsize": c["legend.font_size"],
        "axes.linewidth": c["axes.main.spine_width"],
        "xtick.major.width": c["axes.main.spine_width"],
        "ytick.major.width": c["axes.main.spine_width"],
        "xtick.major.size": c["axes.main.tick_length"],
        "ytick.major.size": c["axes.main.tick_length"],
    }
    with plt.rc_context(style):
        return _draw(data, c)


def _draw(data, c):
    x = np.arange(len(OUTCOMES))
    fig, ax = plt.subplots(figsize=tuple(c["figure.size"]), facecolor=c["figure.facecolor"])
    ax.set_facecolor(c["figure.facecolor"])
    centers = {"AI": x - c["bars.width"] / 2, "Domain": x + c["bars.width"] / 2}
    colors = {"AI": c["bars.ai.color"], "Domain": c["bars.domain.color"]}
    for leader in ("AI", "Domain"):
        raw = data[data.specification.eq("Raw") & data.leader_class.eq(leader)].set_index("outcome").loc[OUTCOMES]
        ax.bar(centers[leader], raw.estimate.to_numpy(), width=c["bars.width"], color=colors[leader], edgecolor="none", zorder=1)
        adjusted = data[data.specification.eq("Year + field adjusted") & data.leader_class.eq(leader)].set_index("outcome").loc[OUTCOMES]
        y = adjusted.estimate.to_numpy()
        error = np.vstack([y - adjusted.ci_low.to_numpy(), adjusted.ci_high.to_numpy() - y])
        ax.errorbar(
            centers[leader], y, yerr=error, fmt=c["adjusted.marker_shape"],
            ms=c["adjusted.marker_size"], lw=c["adjusted.linewidth"],
            capsize=c["adjusted.capsize"], mfc=c["adjusted.marker_facecolor"],
            mec=c["adjusted.color"], color=c["adjusted.color"], zorder=3,
        )
    labels = c["axes.main.x_labels"]
    if len(labels) != len(OUTCOMES):
        raise ValueError("Outcome labels must contain exactly three entries")
    ax.set_xticks(x, labels)
    ax.set_ylim(*c["axes.main.y_range"])
    ax.set_ylabel(c["axes.main.y_label"], family=c["typography.font_family"], fontsize=c["typography.label_size"])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=c["axes.main.y_percent_decimals"]))
    handles = [
        Patch(facecolor=c["bars.ai.color"], edgecolor="none", label=c["legend.ai_label"]),
        Patch(facecolor=c["bars.domain.color"], edgecolor="none", label=c["legend.domain_label"]),
        Line2D([], [], marker=c["adjusted.marker_shape"], ls="none",
               ms=c["adjusted.marker_size"] + 0.2, color=c["adjusted.color"],
               markerfacecolor=c["adjusted.marker_facecolor"], label=c["legend.adjusted_label"]),
    ]
    legend = ax.legend(
        handles=handles, frameon=c["legend.frame"], ncol=c["legend.columns"],
        fontsize=c["legend.font_size"], loc=c["legend.location"],
    )
    for text in legend.get_texts():
        text.set_fontfamily(c["typography.font_family"])
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(c["axes.main.spine_width"])
    ax.spines["bottom"].set_linewidth(c["axes.main.spine_width"])
    ax.tick_params(direction="out", labelsize=c["typography.tick_size"], width=c["axes.main.spine_width"], length=c["axes.main.tick_length"])
    for tick in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        tick.set_fontfamily(c["typography.font_family"])
    ax.grid(False)
    _apply_axis_alignment(fig, [ax], c)
    return fig
