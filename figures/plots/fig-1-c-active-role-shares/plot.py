"""Matplot Studio figure for Figure 1c."""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from csv import DictReader
from io import StringIO

import pandas as pd


PLOT_META = {'id': "fig-1-c-active-role-shares",
 'name': "Figure 1c — Annual active-role shares · Direct labels",
 'description': 'Annual active-role composition with labels placed directly inside the stacked areas.',
 'version': 1,
 'data_mode': 'inline',
 'data_note': 'Annual AI4Sci participants are assigned AI-, AI4Sci-, or Domain-active only when one paper '
              'type is their unique annual plurality. Tied author-years are excluded from the denominator. '
              'Plotted values are 5-year EWMAs for 1995–2024.',
 'data_export': {'csv': True,
                 'json': True,
                 'note': 'Exports the complete embedded calculation table used by the figure.'}}

PLOT_SCHEMA = [
    {'path': 'layout.mode', 'label': '布局模式', 'group': '坐标轴对齐', 'type': 'select', 'default': 'auto', 'options': [{'value': 'auto', 'label': '自动布局（原外观）'}, {'value': 'fixed', 'label': '固定边距（用于对齐）'}], 'required': True},
    {'path': 'layout.left_mm', 'label': '左边距 / Y 轴位置（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 17.674167, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.right_mm', 'label': '右边距（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 3.81, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.bottom_mm', 'label': '下边距 / X 轴位置（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 13.205396, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.top_mm', 'label': '上边距（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 4.77312, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'axes.main.x_label_pad', 'label': 'X 轴标题间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 4, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.x_tick_pad', 'label': 'X 刻度文字间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 3.5, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.y_label_pad', 'label': 'Y 轴标题间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 4, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.y_tick_pad', 'label': 'Y 刻度文字间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 3.5, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
{'path': 'figure.size',
  'label': 'Figure size',
  'group': 'Figure',
  'type': 'number_pair',
  'default': [2.45, 2.15],
  'min': 1.5,
  'max': 12,
  'step': 0.01,
  'required': True},
 {'path': 'figure.facecolor',
  'label': 'Background',
  'group': 'Figure',
  'type': 'color',
  'default': '#FFFFFF',
  'required': True},
 {'path': 'axes.main.x_label',
  'label': 'X-axis label',
  'group': 'Axes',
  'type': 'string',
  'default': 'Year',
  'required': True},
 {'path': 'axes.main.y_label',
  'label': 'Y-axis label',
  'group': 'Axes',
  'type': 'string',
  'default': 'Share of author in AI4Sci',
  'required': True},
 {'path': 'axes.main.x_range',
  'label': 'X-axis range',
  'group': 'Axes',
  'type': 'number_pair',
  'default': [1995, 2024],
  'min': 1995,
  'max': 2024,
  'step': 1,
  'required': True},
 {'path': 'axes.main.y_range',
  'label': 'Y-axis range',
  'group': 'Axes',
  'type': 'number_pair',
  'default': [0, 1],
  'min': 0,
  'max': 1,
  'step': 0.05,
  'required': True},
 {'path': 'axes.main.spine_width',
  'label': 'Spine width',
  'group': 'Axes',
  'type': 'number',
  'default': 0.6,
  'min': 0,
  'max': 3,
  'step': 0.1,
  'required': True},
 {'path': 'axes.main.tick_length',
  'label': 'Tick length',
  'group': 'Axes',
  'type': 'number',
  'default': 3.0,
  'min': 0,
  'max': 10,
  'step': 0.5,
  'required': True},
 {'path': 'series.ai.color',
  'label': 'AI-active color',
  'group': 'Series',
  'type': 'color',
  'default': '#3B6FB6',
  'required': True},
 {'path': 'series.ai4sci.color',
  'label': 'AI4Sci-active color',
  'group': 'Series',
  'type': 'color',
  'default': '#7A5195',
  'required': True},
 {'path': 'series.domain.color',
  'label': 'Domain-active color',
  'group': 'Series',
  'type': 'color',
  'default': '#D55E5E',
  'required': True},
 {'path': 'series.area.alpha',
  'label': 'Area opacity',
  'group': 'Series',
  'type': 'number',
  'default': 0.88,
  'min': 0,
  'max': 1,
  'step': 0.05,
  'required': True},
 {'path': 'series.area.edgecolor',
  'label': 'Boundary color',
  'group': 'Series',
  'type': 'color',
  'default': '#FFFFFF',
  'required': True},
 {'path': 'series.area.linewidth',
  'label': 'Boundary width',
  'group': 'Series',
  'type': 'number',
  'default': 0.35,
  'min': 0,
  'max': 3,
  'step': 0.05,
  'required': True},
 {'path': 'typography.font_family',
  'label': 'Font family',
  'group': 'Typography',
  'type': 'string',
  'default': 'Arial',
  'required': True},
 {'path': 'typography.label_size',
  'label': 'Axis-label size',
  'group': 'Typography',
  'type': 'number',
  'default': 9,
  'min': 4,
  'max': 20,
  'step': 0.5,
  'required': True},
 {'path': 'typography.tick_size',
  'label': 'Tick-label size',
  'group': 'Typography',
  'type': 'number',
  'default': 8,
  'min': 4,
  'max': 20,
  'step': 0.5,
  'required': True},
 {'path': 'annotations.ai.text',
  'label': 'AI-active text',
  'group': 'Direct labels',
  'type': 'string',
  'default': 'AI-active',
  'required': True},
 {'path': 'annotations.ai.position',
  'label': 'AI-active position',
  'group': 'Direct labels',
  'type': 'number_pair',
  'default': [0.32, 0.075],
  'required': True,
  'min': 0,
  'max': 1,
  'step': 0.01},
 {'path': 'annotations.ai.color',
  'label': 'AI-active color',
  'group': 'Direct labels',
  'type': 'color',
  'default': '#FFFFFF',
  'required': True},
 {'path': 'annotations.ai.font_size',
  'label': 'AI-active font_size',
  'group': 'Direct labels',
  'type': 'number',
  'default': 7,
  'required': True,
  'min': 3,
  'max': 20,
  'step': 0.5},
 {'path': 'annotations.ai4sci.text',
  'label': 'AI4Sci-active text',
  'group': 'Direct labels',
  'type': 'string',
  'default': 'AI4Sci-active',
  'required': True},
 {'path': 'annotations.ai4sci.position',
  'label': 'AI4Sci-active position',
  'group': 'Direct labels',
  'type': 'number_pair',
  'default': [0.5, 0.43],
  'required': True,
  'min': 0,
  'max': 1,
  'step': 0.01},
 {'path': 'annotations.ai4sci.color',
  'label': 'AI4Sci-active color',
  'group': 'Direct labels',
  'type': 'color',
  'default': '#FFFFFF',
  'required': True},
 {'path': 'annotations.ai4sci.font_size',
  'label': 'AI4Sci-active font_size',
  'group': 'Direct labels',
  'type': 'number',
  'default': 7,
  'required': True,
  'min': 3,
  'max': 20,
  'step': 0.5},
 {'path': 'annotations.domain.text',
  'label': 'Domain-active text',
  'group': 'Direct labels',
  'type': 'string',
  'default': 'Domain-active',
  'required': True},
 {'path': 'annotations.domain.position',
  'label': 'Domain-active position',
  'group': 'Direct labels',
  'type': 'number_pair',
  'default': [0.52, 0.87],
  'required': True,
  'min': 0,
  'max': 1,
  'step': 0.01},
 {'path': 'annotations.domain.color',
  'label': 'Domain-active color',
  'group': 'Direct labels',
  'type': 'color',
  'default': '#FFFFFF',
  'required': True},
 {'path': 'annotations.domain.font_size',
  'label': 'Domain-active font_size',
  'group': 'Direct labels',
  'type': 'number',
  'default': 7,
  'required': True,
  'min': 3,
  'max': 20,
  'step': 0.5}]

PLOT_SETTINGS = {
    'layout.mode': 'auto',
    'layout.left_mm': 17.674167,
    'layout.right_mm': 3.81,
    'layout.bottom_mm': 13.205396,
    'layout.top_mm': 4.77312,
    'axes.main.x_label_pad': 4,
    'axes.main.x_tick_pad': 3.5,
    'axes.main.y_label_pad': 4,
    'axes.main.y_tick_pad': 3.5,
'figure.size': [2.67, 2.4],
 'figure.facecolor': '#FFFFFF',
 'axes.main.x_label': 'Year',
 'axes.main.y_label': 'Percent of dominant activity',
 'axes.main.x_range': [1995, 2024],
 'axes.main.y_range': [0, 1],
 'axes.main.spine_width': 0.6,
 'axes.main.tick_length': 3.0,
 'series.ai.color': '#3B6FB6',
 'series.ai4sci.color': '#7A5195',
 'series.domain.color': '#D55E5E',
 'series.area.alpha': 0.88,
 'series.area.edgecolor': '#FFFFFF',
 'series.area.linewidth': 0.35,
 'typography.font_family': 'Arial',
 'typography.label_size': 9,
 'typography.tick_size': 7.5,
 'annotations.ai.text': 'AI-active',
 'annotations.ai.position': [0.32, 0.075],
 'annotations.ai.color': '#FFFFFF',
 'annotations.ai.font_size': 7,
 'annotations.ai4sci.text': 'AI4Sci-active',
 'annotations.ai4sci.position': [0.5, 0.43],
 'annotations.ai4sci.color': '#FFFFFF',
 'annotations.ai4sci.font_size': 7,
 'annotations.domain.text': 'Domain-active',
 'annotations.domain.position': [0.52, 0.87],
 'annotations.domain.color': '#FFFFFF',
 'annotations.domain.font_size': 7}


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


_CSV_DATA = """year,AI,AI4Sci,Domain,AI_ewma5,AI4Sci_ewma5,Domain_ewma5,tie_excluded_n
1995,0.1282051282051282,0.6942953687139733,0.17749950308089843,0.1282051282051282,0.6942953687139733,0.17749950308089843,1577
1996,0.14796526477098587,0.6703558658266644,0.18167886940234973,0.13479184039374742,0.6863155344182037,0.17889262518804888,1699
1997,0.13688684257127678,0.6833717017885603,0.17974145564016292,0.13549017445292388,0.6853342568749893,0.1791755686720869,1760
1998,0.16000603227265872,0.6541999698386367,0.18579399788870457,0.14366212705950215,0.6749561611962052,0.1813817117442928,2098
1999,0.13565118267312626,0.6799658022228555,0.18438301510401825,0.14099181226404353,0.676626041538422,0.18238214619753462,2161
2000,0.1585610428678867,0.645650538982201,0.19578841814991227,0.14684822246532458,0.6663008740196817,0.18685090351499384,2579
2001,0.15868544600938966,0.6338028169014085,0.20751173708920187,0.15079396364667963,0.6554681883135907,0.19373784803972985,2682
2002,0.17016890016652128,0.6007453810165728,0.22908571881690587,0.15725227581996018,0.6372272525479181,0.2055204716321219,3615
2003,0.1747031742185607,0.5979323156449399,0.22736451013649947,0.16306924195282702,0.6241289402469254,0.21280181780024776,3735
2004,0.16090686274509805,0.6064950980392156,0.23259803921568628,0.16234844888358405,0.6182509928443556,0.21940055827206062,4767
2005,0.17567202120179568,0.5734761209367732,0.2508518578614311,0.16678963965632126,0.6033260355418282,0.22988432480185078,5442
2006,0.1657678479712378,0.5599212463619243,0.27431090566683786,0.1664490424279601,0.5888577724818602,0.24469318509017982,6995
2007,0.12007482754589033,0.571300518336646,0.30862465411746365,0.15099097080060353,0.5830053544334555,0.2660036747659411,7726
2008,0.14247650062911701,0.5478869069646954,0.30963659240618757,0.14815281407677472,0.5712992052772021,0.28054798064602327,8038
2009,0.1447562776957164,0.5289065988801483,0.32633712342413523,0.14702063528308862,0.5571683364781843,0.2958110282387273,8380
2010,0.1384596993514838,0.5348017094527958,0.3267385911957204,0.14416698997255367,0.5497127941363882,0.30612021589105837,9542
2011,0.14875391646784902,0.5338756503492483,0.31737043318290264,0.14569596547098546,0.5444337462073416,0.3098702883216731,10072
2012,0.13680257510729613,0.5316012671162885,0.33159615777641527,0.14273150201642235,0.5401562531769906,0.3171122448065872,11275
2013,0.11573457361540719,0.5423901018265562,0.3418753245580366,0.13373252588275064,0.5409008693935125,0.325366604723737,12476
2014,0.11613141835665414,0.5345702603299842,0.3492983213133617,0.12786549004071848,0.5387906663723364,0.33334384358694524,13759
2015,0.11123793503944891,0.5365052665304978,0.35225679843005325,0.12232297170696196,0.5380288664250569,0.3396481618679813,14085
2016,0.1078140107233893,0.5454865078667487,0.346699481409862,0.11748665137910441,0.5405147469056208,0.3419986017152749,15894
2017,0.09730187794137675,0.5436496527094714,0.3590484693491518,0.11075839356652853,0.5415597155069044,0.3476818909265672,17984
2018,0.08821104699093157,0.5332657471981462,0.3785232058109222,0.1032426113746629,0.538795059403985,0.3579623292213522,24003
2019,0.06902312996136856,0.5354040000652007,0.3955728699734307,0.09183611757023147,0.5376647062910569,0.37049917613871175,31725
2020,0.05839928756882863,0.5246905063529294,0.416910206078242,0.08069050756976387,0.5333399729783477,0.3859695194518885,39608
2021,0.043929447343672205,0.5238940419332829,0.43217651072304486,0.06843682082773332,0.5301913292966595,0.4013718498756073,52662
2022,0.036459174181446376,0.5369319710632933,0.42660885475526034,0.05777760527897101,0.5324382098855374,0.40978418483549167,60204
2023,0.035072275602353334,0.5387582803402884,0.42616944405735824,0.05020916205343179,0.5345449000371211,0.41524593790944725,66528
2024,0.0707481874374683,0.5346511245425764,0.3946006880199553,0.05705550384811063,0.5345803082056062,0.40836418794628326,71261
"""


def prepare_data():
    """Parse and return the complete CSV embedded in this module."""
    rows = []
    for row in DictReader(StringIO(_CSV_DATA)):
        rows.append(
            {
                key: int(value) if key in {"year", "tie_excluded_n"} else float(value)
                for key, value in row.items()
            }
        )
    return pd.DataFrame(rows)

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
    """Render and return one Matplotlib Figure without external I/O."""
    config = _resolved(settings)
    fig, ax = plt.subplots(
        figsize=tuple(config["figure.size"]),
        facecolor=config["figure.facecolor"],
    )
    ax.set_facecolor(config["figure.facecolor"])
    ax.stackplot(
        data["year"],
        data["AI_ewma5"],
        data["AI4Sci_ewma5"],
        data["Domain_ewma5"],
        labels=["AI-active", "AI4Sci-active", "Domain-active"],
        colors=[
            config["series.ai.color"],
            config["series.ai4sci.color"],
            config["series.domain.color"],
        ],
        alpha=config["series.area.alpha"],
        edgecolor=config["series.area.edgecolor"],
        linewidth=config["series.area.linewidth"],
    )
    ax.set_xlabel(config["axes.main.x_label"], family=config["typography.font_family"], fontsize=config["typography.label_size"])
    ax.set_ylabel(config["axes.main.y_label"], family=config["typography.font_family"], fontsize=config["typography.label_size"])
    ax.set_xlim(*config["axes.main.x_range"])
    ax.set_ylim(*config["axes.main.y_range"])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.tick_params(axis="both", direction="out", labelsize=config["typography.tick_size"], width=config["axes.main.spine_width"], length=config["axes.main.tick_length"])
    for label in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        label.set_fontfamily(config["typography.font_family"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(config["axes.main.spine_width"])
    ax.spines["bottom"].set_linewidth(config["axes.main.spine_width"])
    ax.grid(False)
    for role in ("ai", "ai4sci", "domain"):
        prefix = f"annotations.{role}"
        ax.text(
            *config[f"{prefix}.position"], config[f"{prefix}.text"],
            transform=ax.transAxes, ha="center", va="center",
            color=config[f"{prefix}.color"],
            fontsize=config[f"{prefix}.font_size"],
            fontfamily=config["typography.font_family"],
        )
    _apply_axis_alignment(fig, ax, config)
    return fig
