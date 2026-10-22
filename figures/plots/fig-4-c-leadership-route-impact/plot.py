from csv import DictReader
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, MultipleLocator
import numpy as np
import pandas as pd


PLOT_META = {
    "id": "fig-4-c-leadership-route-impact",
    "name": "Figure 4c — Origin-normalized · Leadership routes",
    "description": "Origin-normalized citation impact before the pivot and across post-pivot team-origin and leadership-route combinations, shown for AI-active and Domain-active transition cohorts.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "Fourteen cohort-by-category summaries calculated from author-level means. Single- and cross-origin post-pivot papers are each split into Domain-led, independent AI-led and chaperoned AI-led routes; chaperoning requires the AI Specialist last author to have participated in a Domain-led AI4Sci paper in a strictly earlier year.",
    "data_export": {"csv": True, "json": True, "note": "Fourteen summary rows with means, sample sizes, standard errors and 95% intervals."},
}


PLOT_SCHEMA = [
    {"path": "figure.size", "label": "画布宽高（英寸）", "group": "Figure", "type": "number_pair", "default": [7.2, 4.8], "required": True, "min": 1.5, "max": 16, "step": 0.05},
    {"path": "figure.facecolor", "label": "背景色", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.y_label", "label": "纵轴标题", "group": "Axes", "type": "string", "default": "Mean citation percentile", "required": True},
    {"path": "axes.y_range", "label": "纵轴范围（0–100 百分位）", "group": "Axes", "type": "number_pair", "default": [50, 68], "required": True, "min": 0, "max": 100, "step": 1},
    {"path": "axes.y_tick_step", "label": "纵轴刻度间隔", "group": "Axes", "type": "number", "default": 5, "required": True, "min": 0.1, "max": 50, "step": 0.5},
    {"path": "axes.y_label_pad", "label": "纵轴标题间距（pt）", "group": "Axes", "type": "number", "default": 5, "required": True, "min": 0, "max": 30, "step": 0.5},
    {"path": "axes.x_tick_pad", "label": "横轴标签间距（pt）", "group": "Axes", "type": "number", "default": 5, "required": True, "min": 0, "max": 30, "step": 0.5},
    {"path": "axes.y_tick_pad", "label": "纵轴刻度间距（pt）", "group": "Axes", "type": "number", "default": 3.5, "required": True, "min": 0, "max": 30, "step": 0.5},
    {"path": "axes.spine_width", "label": "轴线宽度", "group": "Axes", "type": "number", "default": 0.6, "required": True, "min": 0, "max": 3, "step": 0.1},
    {"path": "axes.tick_length", "label": "刻度线长度", "group": "Axes", "type": "number", "default": 3, "required": True, "min": 0, "max": 10, "step": 0.5},
    {"path": "axes.grid", "label": "显示水平网格", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.grid_color", "label": "网格/分隔线颜色", "group": "Axes", "type": "color", "default": "#ECECEC", "required": True},
    {"path": "axes.grid_width", "label": "网格线宽", "group": "Axes", "type": "number", "default": 0.45, "required": True, "min": 0, "max": 3, "step": 0.05},
    {"path": "axes.category_labels", "label": "七个类别标签", "group": "Axes", "type": "string_list", "default": ["Source-field\npapers", "Domain-led", "Independent\nAI-led", "Chaperoned\nAI-led", "Domain-led", "Independent\nAI-led", "Chaperoned\nAI-led"], "required": True},
    {"path": "series.ai.title", "label": "转向路径标题", "group": "AI cohort", "type": "string", "default": "AI-active → AI4Sci-active", "required": True},
    {"path": "series.ai.color", "label": "点颜色", "group": "AI cohort", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.ai.marker", "label": "点形状", "group": "AI cohort", "type": "select", "default": "o", "required": True, "options": ["o", "s", "D", "^"]},
    {"path": "series.domain.title", "label": "转向路径标题", "group": "Domain cohort", "type": "string", "default": "Domain-active → AI4Sci-active", "required": True},
    {"path": "series.domain.color", "label": "点颜色", "group": "Domain cohort", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.domain.marker", "label": "点形状", "group": "Domain cohort", "type": "select", "default": "s", "required": True, "options": ["o", "s", "D", "^"]},
    {"path": "series.marker_size", "label": "点大小", "group": "Series", "type": "number", "default": 4.2, "required": True, "min": 1, "max": 12, "step": 0.1},
    {"path": "series.cohort_offset", "label": "同类别两组点的横向间距", "group": "Series", "type": "number", "default": 0.1, "required": True, "min": 0, "max": 0.35, "step": 0.01},
    {"path": "series.marker_facecolor", "label": "空心点填充颜色", "group": "Series", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "series.marker_edgewidth", "label": "点边框线宽", "group": "Series", "type": "number", "default": 0.5, "required": True, "min": 0.1, "max": 3, "step": 0.1},
    {"path": "series.fill_with_color", "label": "点填充随组别颜色", "group": "Series", "type": "boolean", "default": True, "required": True},
    {"path": "interval.color", "label": "置信区间颜色", "group": "Interval", "type": "color", "default": "#333333", "required": True},
    {"path": "interval.linewidth", "label": "区间线宽", "group": "Interval", "type": "number", "default": 0.8, "required": True, "min": 0.1, "max": 4, "step": 0.1},
    {"path": "interval.capsize", "label": "区间端帽宽度", "group": "Interval", "type": "number", "default": 3, "required": True, "min": 0, "max": 8, "step": 0.5},
    {"path": "baseline.visible", "label": "显示 Pre-pivot 水平参考线", "group": "Baseline", "type": "boolean", "default": True, "required": True},
    {"path": "baseline.alpha", "label": "参考线不透明度", "group": "Baseline", "type": "number", "default": 0.45, "required": True, "min": 0, "max": 1, "step": 0.05},
    {"path": "baseline.width", "label": "参考线宽", "group": "Baseline", "type": "number", "default": 0.7, "required": True, "min": 0.1, "max": 3, "step": 0.1},
    {"path": "baseline.style", "label": "参考线样式", "group": "Baseline", "type": "select", "default": "--", "required": True, "options": ["-", "--", ":", "-."]},
    {"path": "groups.pre_label", "label": "转向前组标题", "group": "Groups", "type": "string", "default": "Pre-pivot", "required": True},
    {"path": "groups.post_label", "label": "转向后组标题", "group": "Groups", "type": "string", "default": "Post-pivot AI4Sci papers", "required": True},
    {"path": "groups.single_label", "label": "Single-origin 组标题", "group": "Groups", "type": "string", "default": "Single-origin teams", "required": True},
    {"path": "groups.cross_label", "label": "Cross-origin 组标题", "group": "Groups", "type": "string", "default": "Cross-origin teams", "required": True},
    {"path": "groups.header_y", "label": "子组标题高度", "group": "Groups", "type": "number", "default": 1.025, "required": True, "min": 0.8, "max": 1.5, "step": 0.01},
    {"path": "groups.post_header_y", "label": "Post-pivot 标题高度", "group": "Groups", "type": "number", "default": 1.095, "required": True, "min": 0.8, "max": 1.5, "step": 0.01},
    {"path": "groups.header_size", "label": "组标题字号", "group": "Groups", "type": "number", "default": 8, "required": True, "min": 4, "max": 14, "step": 0.5},
    {"path": "groups.shade", "label": "转向后区域底色", "group": "Groups", "type": "boolean", "default": True, "required": True},
    {"path": "groups.shade_color", "label": "转向后区域颜色", "group": "Groups", "type": "color", "default": "#F7F7F7", "required": True},
    {"path": "groups.separator", "label": "显示转向前后分隔线", "group": "Groups", "type": "boolean", "default": True, "required": True},
    {"path": "values.visible", "label": "显示均值数值", "group": "Value labels", "type": "boolean", "default": True, "required": True},
    {"path": "values.font_size", "label": "均值字号", "group": "Value labels", "type": "number", "default": 7, "required": True, "min": 4, "max": 14, "step": 0.5},
    {"path": "values.decimals", "label": "均值小数位数", "group": "Value labels", "type": "integer", "default": 1, "required": True, "min": 0, "max": 3, "step": 1},
    {"path": "values.ai.offset", "label": "AI cohort 数值偏移", "group": "Value labels", "type": "number_pair", "default": [0, 9], "required": True, "min": -40, "max": 40, "step": 1},
    {"path": "values.domain.offset", "label": "Domain cohort 数值偏移", "group": "Value labels", "type": "number_pair", "default": [0, -10], "required": True, "min": -40, "max": 40, "step": 1},
    {"path": "legend.visible", "label": "显示转向路径图例", "group": "Legend", "type": "boolean", "default": True, "required": True},
    {"path": "legend.anchor", "label": "图例位置 X / Y", "group": "Legend", "type": "number_pair", "default": [0.025, 0.97], "required": True, "min": 0, "max": 1, "step": 0.01},
    {"path": "legend.location", "label": "图例锚定方向", "group": "Legend", "type": "select", "default": "upper left", "required": True, "options": ["upper left", "upper right", "lower left", "lower right"]},
    {"path": "legend.font_size", "label": "图例字号", "group": "Legend", "type": "number", "default": 7.2, "required": True, "min": 4, "max": 16, "step": 0.1},
    {"path": "legend.row_spacing", "label": "图例行距", "group": "Legend", "type": "number", "default": 0.45, "required": True, "min": 0, "max": 2, "step": 0.05},
    {"path": "typography.font_family", "label": "字体", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.label_size", "label": "轴标题字号", "group": "Typography", "type": "number", "default": 9, "required": True, "min": 4, "max": 16, "step": 0.5},
    {"path": "typography.tick_size", "label": "刻度字号", "group": "Typography", "type": "number", "default": 8, "required": True, "min": 4, "max": 16, "step": 0.5},
    {"path": "layout.left_mm", "label": "左边距（mm）", "group": "Layout", "type": "number", "default": 15, "required": True, "min": 0, "max": 100, "step": 0.1},
    {"path": "layout.right_mm", "label": "右边距（mm）", "group": "Layout", "type": "number", "default": 2, "required": True, "min": 0, "max": 100, "step": 0.1},
    {"path": "layout.bottom_mm", "label": "下边距（mm）", "group": "Layout", "type": "number", "default": 14, "required": True, "min": 0, "max": 100, "step": 0.1},
    {"path": "layout.top_mm", "label": "上边距（mm）", "group": "Layout", "type": "number", "default": 19, "required": True, "min": 0, "max": 100, "step": 0.1},
]


PLOT_SETTINGS = {'figure.size': [8, 2.4],
 'figure.facecolor': '#FFFFFF',
 'axes.y_label': 'Mean citation percentile',
 'axes.y_range': [50, 68],
 'axes.y_tick_step': 5,
 'axes.y_label_pad': 5,
 'axes.x_tick_pad': 5,
 'axes.y_tick_pad': 3.5,
 'axes.spine_width': 0.6,
 'axes.tick_length': 3,
 'axes.grid': False,
 'axes.grid_color': '#ECECEC',
 'axes.grid_width': 0.45,
 'axes.category_labels': ['Source-field\npapers',
                          'Domain-led',
                          'Independent\nAI-led',
                          'Chaperoned\nAI-led',
                          'Domain-led',
                          'Independent\nAI-led',
                          'Chaperoned\nAI-led'],
 'series.ai.title': 'AI-active → AI4Sci-active',
 'series.ai.color': '#3B6FB6',
 'series.ai.marker': 'o',
 'series.domain.title': 'Domain-active → AI4Sci-active',
 'series.domain.color': '#D55E5E',
 'series.domain.marker': 's',
 'series.marker_size': 4.2,
 'series.cohort_offset': 0.1,
 'series.marker_facecolor': '#FFFFFF',
 'series.marker_edgewidth': 0.5,
 'series.fill_with_color': True,
 'interval.color': '#333333',
 'interval.linewidth': 0.8,
 'interval.capsize': 3,
 'baseline.visible': True,
 'baseline.alpha': 0.45,
 'baseline.width': 0.7,
 'baseline.style': '--',
 'groups.pre_label': 'Pre-pivot',
 'groups.post_label': 'Post-pivot AI4Sci papers',
 'groups.single_label': 'Single-origin teams',
 'groups.cross_label': 'Cross-origin teams',
 'groups.header_y': 1.025,
 'groups.post_header_y': 1.095,
 'groups.header_size': 8,
 'groups.shade': True,
 'groups.shade_color': '#F7F7F7',
 'groups.separator': True,
 'values.visible': True,
 'values.font_size': 7,
 'values.decimals': 1,
 'values.ai.offset': [0, 9],
 'values.domain.offset': [0, -10],
 'legend.visible': True,
 'legend.anchor': [0.025, 0.97],
 'legend.location': 'upper left',
 'legend.font_size': 7.2,
 'legend.row_spacing': 0.45,
 'typography.font_family': 'Arial',
 'typography.label_size': 9,
 'typography.tick_size': 8,
 'layout.left_mm': 15,
 'layout.right_mm': 2,
 'layout.bottom_mm': 14,
 'layout.top_mm': 10}


_CSV_DATA = """cohort,category,mean,sd,n_authors,n_papers,se,ci95
AI,Post-pivot cross-origin · Independent AI-led,0.6173504402122797,0.289512596659102,16250,33376,0.0022711236612241205,0.004451402375999276
AI,Pre-pivot,0.5759595244317295,0.23898040319250596,42776,362022,0.0011554793912782304,0.0022647396069053315
AI,Post-pivot cross-origin · Chaperoned AI-led,0.6544040343861304,0.268945598844958,21125,83602,0.001850401973128354,0.0036267878673315736
AI,Post-pivot cross-origin · Domain-led,0.636165124017365,0.2620896437609725,30859,125828,0.0014919660345975715,0.00292425342781124
AI,Post-pivot single-origin · Chaperoned AI-led,0.6088905708888442,0.27896239935890954,8219,24653,0.0030770615221595112,0.006031040583432642
AI,Post-pivot single-origin · Independent AI-led,0.5781982503477029,0.2805464681983,7720,18138,0.003192979686282536,0.00625824018511377
AI,Post-pivot single-origin · Domain-led,0.6049430968915719,0.28229940827380146,12942,43452,0.002481471376840065,0.0048636838986065275
Domain,Post-pivot cross-origin · Chaperoned AI-led,0.637276827889359,0.2881336710316066,33290,95499,0.0015791999257826006,0.003095231854533897
Domain,Post-pivot cross-origin · Independent AI-led,0.5889461688751627,0.30952996012406425,24674,43499,0.0019705293669040904,0.0038622375591320173
Domain,Post-pivot single-origin · Domain-led,0.5892449125132667,0.28527768931242886,49048,150254,0.0012881224713874844,0.0025247200439194695
Domain,Pre-pivot,0.5337642131590227,0.23681913765592752,93624,1251599,0.0007739683463794319,0.0015169779589036864
Domain,Post-pivot cross-origin · Domain-led,0.6172402611027843,0.28130563763884175,59879,187042,0.001149585206724911,0.002253187005180825
Domain,Post-pivot single-origin · Chaperoned AI-led,0.5934671243881087,0.3047547810158217,6286,13226,0.0038438226295257755,0.00753389235387052
Domain,Post-pivot single-origin · Independent AI-led,0.5516422421297864,0.3100786668576233,6610,11921,0.0038139163055194263,0.007475275958818075
"""


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


def prepare_data():
    rows = []
    for row in DictReader(StringIO(_CSV_DATA)):
        rows.append({key: value if key in {"cohort", "category"} else int(value) if key in {"n_authors", "n_papers"} else float(value) for key, value in row.items()})
    return pd.DataFrame(rows)


def render(data, settings):
    c = _resolved(settings)
    if len(c["axes.category_labels"]) != 7:
        raise ValueError("请保留七个类别标签。")
    if c["axes.y_range"][0] >= c["axes.y_range"][1]:
        raise ValueError("纵轴下限须小于上限。")
    width, height = np.array(c["figure.size"]) * 25.4
    left, right = c["layout.left_mm"] / width, 1 - c["layout.right_mm"] / width
    bottom, top = c["layout.bottom_mm"] / height, 1 - c["layout.top_mm"] / height
    if not (0 <= left < right <= 1 and 0 <= bottom < top <= 1):
        raise ValueError("边距过大，请增大画布或减小边距。")
    categories = [
        "Pre-pivot",
        "Post-pivot single-origin · Domain-led",
        "Post-pivot single-origin · Independent AI-led",
        "Post-pivot single-origin · Chaperoned AI-led",
        "Post-pivot cross-origin · Domain-led",
        "Post-pivot cross-origin · Independent AI-led",
        "Post-pivot cross-origin · Chaperoned AI-led",
    ]
    with plt.rc_context({"font.family": c["typography.font_family"]}):
        fig, ax = plt.subplots(figsize=tuple(c["figure.size"]), facecolor=c["figure.facecolor"])
        ax.set_facecolor(c["figure.facecolor"])
        if c["groups.shade"]:
            ax.axvspan(0.5, 6.45, color=c["groups.shade_color"], linewidth=0, zorder=0)
        if c["groups.separator"]:
            ax.axvline(0.5, color=c["axes.grid_color"], lw=0.7, zorder=1)
            ax.axvline(3.5, color=c["axes.grid_color"], lw=0.7, zorder=1)
        legend_handles = []
        for cohort, direction in [("AI", -1), ("Domain", 1)]:
            key = cohort.lower()
            color = c[f"series.{key}.color"]
            subset = data[data.cohort.eq(cohort)].set_index("category").loc[categories]
            means = subset["mean"].to_numpy() * 100
            intervals = subset["ci95"].to_numpy() * 100
            x = np.arange(7) + direction * c["series.cohort_offset"]
            if c["baseline.visible"]:
                ax.axhline(means[0], color=color, lw=c["baseline.width"], ls=c["baseline.style"], alpha=c["baseline.alpha"], zorder=1)
            errors = ax.errorbar(
                x, means, yerr=intervals, fmt=c[f"series.{key}.marker"], linestyle="none",
                color=color, markersize=c["series.marker_size"],
                markerfacecolor=color if c["series.fill_with_color"] else c["series.marker_facecolor"],
                markeredgewidth=c["series.marker_edgewidth"], ecolor=c["interval.color"],
                barsabove=False, elinewidth=c["interval.linewidth"], capsize=c["interval.capsize"],
                capthick=c["interval.linewidth"], label=c[f"series.{key}.title"], zorder=3,
            )
            legend_handles.append(errors.lines[0])
            if c["values.visible"]:
                for xi, mean in zip(x, means):
                    ax.annotate(f"{mean:.{c['values.decimals']}f}", xy=(xi, mean),
                                xytext=tuple(c[f"values.{key}.offset"]), textcoords="offset points",
                                ha="center", va="center", fontsize=c["values.font_size"], color=color, zorder=4)
        ax.set_xlim(-0.45, 6.45)
        ax.set_ylim(*c["axes.y_range"])
        ax.set_xticks(np.arange(7), c["axes.category_labels"])
        ax.yaxis.set_major_locator(MultipleLocator(c["axes.y_tick_step"]))
        ax.yaxis.set_major_formatter(FormatStrFormatter("%g"))
        for x, label in [(0, c["groups.pre_label"]), (2, c["groups.single_label"]), (5, c["groups.cross_label"])]:
            ax.text(x, c["groups.header_y"], label, transform=ax.get_xaxis_transform(),
                    ha="center", va="bottom", fontsize=c["groups.header_size"], color="#333333")
        ax.text(3.5, c["groups.post_header_y"], c["groups.post_label"],
                transform=ax.get_xaxis_transform(), ha="center", va="bottom",
                fontsize=c["groups.header_size"], color="#333333")
        for side in ["top", "right"]:
            ax.spines[side].set_visible(False)
        for side in ["left", "bottom"]:
            ax.spines[side].set_linewidth(c["axes.spine_width"])
        ax.tick_params(axis="both", labelsize=c["typography.tick_size"], width=c["axes.spine_width"])
        ax.tick_params(axis="x", length=0, pad=c["axes.x_tick_pad"])
        ax.tick_params(axis="y", length=c["axes.tick_length"], pad=c["axes.y_tick_pad"])
        ax.set_axisbelow(True)
        ax.grid(False)
        if c["axes.grid"]:
            ax.grid(axis="y", color=c["axes.grid_color"], lw=c["axes.grid_width"])
        ax.set_ylabel(c["axes.y_label"], fontsize=c["typography.label_size"], labelpad=c["axes.y_label_pad"])
        if c["legend.visible"]:
            ax.legend(handles=legend_handles, labels=[c["series.ai.title"], c["series.domain.title"]],
                      loc=c["legend.location"], bbox_to_anchor=c["legend.anchor"],
                      fontsize=c["legend.font_size"], frameon=False, borderaxespad=0,
                      labelspacing=c["legend.row_spacing"], labelcolor="linecolor")
        fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
        return fig
