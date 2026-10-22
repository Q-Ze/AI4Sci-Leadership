"""Matplot Studio figure for Figure 3c."""

from __future__ import annotations

from csv import DictReader
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "fig-3-c-outsider-author-share",
    "name": "Figure 3c — Outsider-author share",
    "description": "Complementary-specialist shares in AI-led and Domain-led AI4Sci teams, shown as five-year EWMAs.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "Annual team-level author counts for AI4Sci papers led by AI or Domain Specialists. Shares use all classifiable AI and Domain author records as the denominator.",
    "data_export": {"csv": True, "json": True, "note": "Complete embedded annual counts, raw shares, and EWMA values."},
}

PLOT_SCHEMA = [
    {'path': 'layout.mode', 'label': '布局模式', 'group': '坐标轴对齐', 'type': 'select', 'default': 'auto', 'options': [{'value': 'auto', 'label': '自动布局（原外观）'}, {'value': 'fixed', 'label': '固定边距（毫米）'}], 'required': True},
    {'path': 'layout.left_mm', 'label': '左边距 / Y 轴位置（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 15.548343, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.right_mm', 'label': '右边距（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 3.048, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.bottom_mm', 'label': '下边距 / X 轴位置（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 7.989645, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.top_mm', 'label': '上边距（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 4.075327, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'axes.main.x_label_pad', 'label': 'X 轴标题间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 4.0, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.y_label_pad', 'label': 'Y 轴标题间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 4.0, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.x_tick_pad', 'label': 'X 刻度文字间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 3.5, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.y_tick_pad', 'label': 'Y 刻度文字间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 3.5, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},

    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.83, 2.43], "min": 1.5, "max": 12, "step": 0.01, "required": True},
    {"path": "figure.facecolor", "label": "Background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.main.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Year", "required": True},
    {"path": "axes.main.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Share of outsider authors", "required": True},
    {"path": "axes.main.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2024], "min": 1995, "max": 2024, "step": 1, "required": True},
    {"path": "axes.main.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0.10, 0.50], "min": 0, "max": 1, "step": 0.01, "required": True},
    {"path": "axes.main.x_tick_step", "label": "X tick interval", "group": "Axes", "type": "number", "default": 10, "min": 1, "max": 30, "step": 1, "required": True},
    {"path": "axes.main.y_tick_step", "label": "Y tick interval", "group": "Axes", "type": "number", "default": 0.10, "min": 0.01, "max": 0.5, "step": 0.01, "required": True},
    {"path": "axes.main.y_percent_decimals", "label": "Y tick decimals", "group": "Axes", "type": "integer", "default": 0, "min": 0, "max": 3, "step": 1, "required": True},
    {"path": "axes.main.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 3, "step": 0.1, "required": True},
    {"path": "axes.main.tick_length", "label": "Tick length", "group": "Axes", "type": "number", "default": 3, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "series.domain_in_ai.color", "label": "Domain-in-AI color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.domain_in_ai.linewidth", "label": "Domain-in-AI width", "group": "Series", "type": "number", "default": 1.3, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "series.domain_in_ai.linestyle", "label": "Domain-in-AI style", "group": "Series", "type": "select", "default": "-", "options": ["-", "--", ":", "-."], "required": True},
    {"path": "series.ai_in_domain.color", "label": "AI-in-Domain color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.ai_in_domain.linewidth", "label": "AI-in-Domain width", "group": "Series", "type": "number", "default": 1.3, "min": 0.1, "max": 5, "step": 0.1, "required": True},
    {"path": "series.ai_in_domain.linestyle", "label": "AI-in-Domain style", "group": "Series", "type": "select", "default": "-", "options": ["-", "--", ":", "-."], "required": True},
    {"path": "annotation.domain_in_ai.text", "label": "Domain-in-AI label", "group": "Annotations", "type": "text", "default": "Domain Specialists\nin AI-led teams", "required": True},
    {"path": "annotation.domain_in_ai.offset", "label": "Domain-in-AI label offset", "group": "Annotations", "type": "number_pair", "default": [-20, 8], "min": -100, "max": 100, "step": 1, "required": True},
    {"path": "annotation.domain_in_ai.horizontal_alignment", "label": "Domain-in-AI horizontal alignment", "group": "Annotations", "type": "select", "default": "right", "options": ["left", "center", "right"], "required": True},
    {"path": "annotation.domain_in_ai.vertical_alignment", "label": "Domain-in-AI vertical alignment", "group": "Annotations", "type": "select", "default": "top", "options": ["top", "center", "bottom"], "required": True},
    {"path": "annotation.ai_in_domain.text", "label": "AI-in-Domain label", "group": "Annotations", "type": "text", "default": "AI Specialists\nin Domain-led teams", "required": True},
    {"path": "annotation.ai_in_domain.offset", "label": "AI-in-Domain label offset", "group": "Annotations", "type": "number_pair", "default": [-20, -8], "min": -100, "max": 100, "step": 1, "required": True},
    {"path": "annotation.ai_in_domain.horizontal_alignment", "label": "AI-in-Domain horizontal alignment", "group": "Annotations", "type": "select", "default": "right", "options": ["left", "center", "right"], "required": True},
    {"path": "annotation.ai_in_domain.vertical_alignment", "label": "AI-in-Domain vertical alignment", "group": "Annotations", "type": "select", "default": "bottom", "options": ["top", "center", "bottom"], "required": True},
    {"path": "annotation.font_size", "label": "Annotation font size", "group": "Annotations", "type": "number", "default": 7.2, "min": 4, "max": 16, "step": 0.1, "required": True},
    {"path": "annotation.box_facecolor", "label": "Annotation background", "group": "Annotations", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "annotation.box_alpha", "label": "Annotation background opacity", "group": "Annotations", "type": "number", "default": 0.82, "min": 0, "max": 1, "step": 0.05, "required": True},
    {"path": "annotation.box_padding", "label": "Annotation background padding", "group": "Annotations", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.label_size", "label": "Axis-label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "typography.tick_size", "label": "Tick-label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 20, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {'layout.mode': 'auto',
 'layout.left_mm': 15.548343,
 'layout.right_mm': 3.048,
 'layout.bottom_mm': 7.989645,
 'layout.top_mm': 4.075327,
 'axes.main.x_label_pad': 4.0,
 'axes.main.y_label_pad': 4.0,
 'axes.main.x_tick_pad': 3.5,
 'axes.main.y_tick_pad': 3.5,
 'figure.size': [3.83, 1.6],
 'figure.facecolor': '#FFFFFF',
 'axes.main.x_label': '',
 'axes.main.y_label': 'Percent of authors',
 'axes.main.x_range': [1995, 2024],
 'axes.main.y_range': [0.1, 0.5],
 'axes.main.x_tick_step': 10,
 'axes.main.y_tick_step': 0.1,
 'axes.main.y_percent_decimals': 0,
 'axes.main.spine_width': 0.6,
 'axes.main.tick_length': 3,
 'series.domain_in_ai.color': '#D55E5E',
 'series.domain_in_ai.linewidth': 1.3,
 'series.domain_in_ai.linestyle': '-',
 'series.ai_in_domain.color': '#3B6FB6',
 'series.ai_in_domain.linewidth': 1.3,
 'series.ai_in_domain.linestyle': '-',
 'annotation.domain_in_ai.text': 'Domain Specialists\nin AI-led teams',
 'annotation.domain_in_ai.offset': [-30, 8],
 'annotation.domain_in_ai.horizontal_alignment': 'right',
 'annotation.domain_in_ai.vertical_alignment': 'top',
 'annotation.ai_in_domain.text': 'AI Specialists\nin Domain-led teams',
 'annotation.ai_in_domain.offset': [-40, -8],
 'annotation.ai_in_domain.horizontal_alignment': 'right',
 'annotation.ai_in_domain.vertical_alignment': 'bottom',
 'annotation.font_size': 7.2,
 'annotation.box_facecolor': '#FFFFFF',
 'annotation.box_alpha': 0.82,
 'annotation.box_padding': 0.6,
 'typography.font_family': 'Arial',
 'typography.label_size': 9,
 'typography.tick_size': 8}


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


_CSV_DATA = """year,leader_class,n_papers,n_ai,n_domain,complementary_share,complementary_share_ewma5
1995,AI,846,1654,510,0.2356746765249538,0.2356746765249538
1995,Domain,1311,560,2812,0.166073546856465,0.166073546856465
1996,AI,991,1930,606,0.23895899053627762,0.23676944786206175
1996,Domain,1571,677,3288,0.1707440100882724,0.16763036793373415
1997,AI,948,1861,577,0.23666940114848237,0.2367360989575353
1997,Domain,1514,786,3192,0.1975867269984917,0.17761582095532
1998,AI,1163,2373,739,0.23746786632390746,0.23698002141299268
1998,Domain,1676,880,3490,0.20137299771167047,0.1855348798741035
1999,AI,1190,2384,764,0.24269377382465057,0.238884605550212
1999,Domain,1791,924,3930,0.1903584672435105,0.1871427423305725
2000,AI,1259,2554,840,0.24749558043606365,0.24175493051216257
2000,Domain,2086,1124,4543,0.19834127404270338,0.19087558623461615
2001,AI,1397,2816,944,0.251063829787234,0.2448578969371864
2001,Domain,2167,1093,4801,0.1854428232100441,0.18906466522642548
2002,AI,2257,4602,1604,0.2584595552690944,0.24939178304782242
2002,Domain,3115,1923,6710,0.22274991312405884,0.2002930811923033
2003,AI,2091,4415,1517,0.2557316250842886,0.2515050637266445
2003,Domain,2978,1732,6807,0.20283405551001288,0.20114007263153982
2004,AI,3072,6487,2211,0.25419636698091513,0.2524021648114014
2004,Domain,4114,2617,9080,0.22373258100367616,0.20867090875558528
2005,AI,3167,6659,2340,0.2600288920991221,0.2549444072406416
2005,Domain,4452,2893,10118,0.22235031896087926,0.21323071215734996
2006,AI,4491,9540,3305,0.25729855975087584,0.25572912474405307
2006,Domain,5851,3975,13041,0.2336036671368124,0.22002169715050413
2007,AI,5081,10844,3870,0.2630148158216664,0.25815768843659087
2007,Domain,6640,4871,14748,0.24827972883429328,0.22944104104510052
2008,AI,4960,10771,3886,0.26512928975915945,0.26048155554411373
2008,Domain,6514,4686,14827,0.24014759391175114,0.23300989200065075
2009,AI,5159,11071,4339,0.28157040882543805,0.2675111733045552
2009,Domain,7041,4888,16591,0.2275711159737418,0.2311969666583478
2010,AI,6221,13326,5193,0.28041470921756034,0.2718123519422236
2010,Domain,8391,6053,19557,0.23635298711440844,0.23291564014370136
2011,AI,6228,13286,5301,0.2851993328670576,0.2762746789171683
2011,Domain,8632,6167,20770,0.22894160448453799,0.2315909615906469
2012,AI,6707,14314,5821,0.28909858455425874,0.28054931412953177
2012,Domain,9870,7307,23628,0.23620494585421045,0.23312895634516811
2013,AI,7495,15990,6826,0.29917601683029454,0.28675821502978605
2013,Domain,11161,8164,27499,0.228920730168522,0.2317262142862861
2014,AI,8116,17499,7762,0.30727207949012314,0.29359616984989845
2014,Domain,12099,8479,30478,0.2176502297404831,0.2270342194376851
2015,AI,8060,17069,8063,0.32082603851663216,0.3026727927388097
2015,Domain,12355,8810,32040,0.21566707466340268,0.22324517117959097
2016,AI,9135,19495,10025,0.33960027100271,0.3149819521601098
2016,Domain,14191,10214,38254,0.21073698110093259,0.21907577448670484
2017,AI,9742,20251,11615,0.3644950731186845,0.3314863258129681
2017,Domain,16362,11714,45484,0.20479737053743138,0.21431630650361372
2018,AI,12709,26444,16171,0.37946732371230785,0.3474799917794147
2018,Domain,21689,15517,64502,0.19391644484434947,0.2075163526171923
2019,AI,16056,33319,23036,0.40876585928489045,0.36790861428124
2019,Domain,30629,21715,94717,0.1865037103201869,0.20051213851819052
2020,AI,19627,41006,29209,0.41599373353272096,0.383936987365067
2020,Domain,38907,27476,128337,0.1763395865556789,0.19245462119735332
2021,AI,26436,55866,41763,0.4277724856343914,0.3985488201215085
2021,Domain,52897,37699,181308,0.17213605044587615,0.18568176428019428
2022,AI,30098,66649,49171,0.42454671041270936,0.4072147835519088
2022,Domain,61465,44720,215497,0.17185656586618092,0.1810733648088565
2023,AI,29277,63971,51171,0.4444164596758785,0.4196153422598987
2023,Domain,68699,46606,252108,0.15602214827560812,0.1727229592977737
2024,AI,22357,47619,40153,0.45746935241307024,0.4322333456442893
2024,Domain,66383,36462,253940,0.1255569865221314,0.1570009683725596
"""


def prepare_data():
    integer_columns = {"year", "n_papers", "n_ai", "n_domain"}
    rows = []
    for row in DictReader(StringIO(_CSV_DATA)):
        if not row or "year" not in row:
            continue
        rows.append({key: (value if key == "leader_class" else int(float(value)) if key in integer_columns else float(value)) for key, value in row.items()})
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
    specs = [
        ("AI", "domain_in_ai"),
        ("Domain", "ai_in_domain"),
    ]
    for leader_class, key in specs:
        subset = data.loc[data.leader_class.eq(leader_class)]
        color = c[f"series.{key}.color"]
        ax.plot(subset.year, subset.complementary_share_ewma5, color=color,
                lw=c[f"series.{key}.linewidth"], ls=c[f"series.{key}.linestyle"])
        last = subset.sort_values("year").iloc[-1]
        ax.annotate(
            c[f"annotation.{key}.text"],
            xy=(last.year, last.complementary_share_ewma5),
            xytext=tuple(c[f"annotation.{key}.offset"]), textcoords="offset points",
            ha=c[f"annotation.{key}.horizontal_alignment"],
            va=c[f"annotation.{key}.vertical_alignment"], color=color,
            family=c["typography.font_family"], fontsize=c["annotation.font_size"],
            bbox={"facecolor": c["annotation.box_facecolor"], "edgecolor": "none",
                  "alpha": c["annotation.box_alpha"], "pad": c["annotation.box_padding"]},
        )
    ax.set_xlabel(c["axes.main.x_label"], family=c["typography.font_family"], fontsize=c["typography.label_size"])
    ax.set_ylabel(c["axes.main.y_label"], family=c["typography.font_family"], fontsize=c["typography.label_size"])
    ax.set_xlim(*c["axes.main.x_range"]); ax.set_ylim(*c["axes.main.y_range"])
    ax.xaxis.set_major_locator(MultipleLocator(c["axes.main.x_tick_step"]))
    ax.yaxis.set_major_locator(MultipleLocator(c["axes.main.y_tick_step"]))
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=c["axes.main.y_percent_decimals"]))
    ax.tick_params(labelsize=c["typography.tick_size"], direction="out",
                   width=c["axes.main.spine_width"], length=c["axes.main.tick_length"])
    for tick in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        tick.set_fontfamily(c["typography.font_family"])
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(c["axes.main.spine_width"])
    ax.spines["bottom"].set_linewidth(c["axes.main.spine_width"])
    ax.grid(False); _apply_axis_alignment(fig, [ax], c)
    return fig
