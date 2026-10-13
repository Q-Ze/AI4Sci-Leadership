"""Matplot Studio figure for Figure 1b."""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from csv import DictReader
from io import StringIO

import pandas as pd


PLOT_META = {
    "id": "fig-1-b-area-author-composition",
    "name": "Figure 1b — Annual author composition",
    "description": "100% stacked area chart of AI and Domain Specialists among annual AI4Sci authors.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "Annual distinct authors on AI4Sci papers, classified by fixed venue-based author class. The plotted values are 5-year EWMA shares for 1995–2024; unclassifiable authors are outside the denominator. Each year's two raw shares use AI + Domain classified authors as their common denominator.",
    "data_export": {
        "csv": True,
        "json": True,
        "note": "Exports the complete embedded calculation table used by the figure.",
    },
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.45, 2.15], "min": 1.5, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.main.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Year", "required": True},
    {"path": "axes.main.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Share of author in AI4Sci", "required": True},
    {"path": "axes.main.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2024], "min": 1995, "max": 2024, "step": 1, "required": True},
    {"path": "axes.main.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0, 1], "min": 0, "max": 1, "step": 0.05, "required": True},
    {"path": "axes.main.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 3, "step": 0.1, "required": True},
    {"path": "axes.main.tick_length", "label": "Tick length", "group": "Axes", "type": "number", "default": 3.0, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "series.ai.color", "label": "AI Specialist color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.domain.color", "label": "Domain Specialist color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.area.alpha", "label": "Area opacity", "group": "Series", "type": "number", "default": 0.88, "min": 0, "max": 1, "step": 0.05, "required": True},
    {"path": "series.area.edgecolor", "label": "Boundary color", "group": "Series", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "series.area.linewidth", "label": "Boundary width", "group": "Series", "type": "number", "default": 0.35, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "legend.ai_label", "label": "AI legend label", "group": "Legend", "type": "string", "default": "AI-origin", "required": True},
    {"path": "legend.domain_label", "label": "Domain legend label", "group": "Legend", "type": "string", "default": "Domain-origin", "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "default": "upper left", "options": ["best", "upper left", "upper right", "lower left", "lower right"], "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.0, "min": 4, "max": 16, "step": 0.5, "required": True},
    {"path": "legend.frame", "label": "Legend frame", "group": "Legend", "type": "boolean", "default": True, "required": True},
    {"path": "legend.facecolor", "label": "Legend background", "group": "Legend", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "legend.frame_alpha", "label": "Legend opacity", "group": "Legend", "type": "number", "default": 0.88, "min": 0, "max": 1, "step": 0.05, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.label_size", "label": "Axis-label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "typography.tick_size", "label": "Tick-label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 20, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [2.45, 2.15],
    "figure.facecolor": "#FFFFFF",
    "axes.main.x_label": "Year",
    "axes.main.y_label": "Share of author in AI4Sci",
    "axes.main.x_range": [1995, 2024],
    "axes.main.y_range": [0, 1],
    "axes.main.spine_width": 0.6,
    "axes.main.tick_length": 3.0,
    "series.ai.color": "#3B6FB6",
    "series.domain.color": "#D55E5E",
    "series.area.alpha": 0.88,
    "series.area.edgecolor": "#FFFFFF",
    "series.area.linewidth": 0.35,
    "legend.ai_label": "AI-origin",
    "legend.domain_label": "Domain-origin",
    "legend.location": "upper left",
    "legend.font_size": 7.0,
    "legend.frame": True,
    "legend.facecolor": "#FFFFFF",
    "legend.frame_alpha": 0.88,
    "typography.font_family": "Arial",
    "typography.label_size": 9,
    "typography.tick_size": 8,
}


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


_CSV_DATA = """year,AI,Domain,total_classified,AI_share,Domain_share,AI_share_ewma5,Domain_share_ewma5
1995,2347,3716,6063,0.3871020946726043,0.6128979053273956,0.3871020946726043,0.6128979053273956
1996,2690,4181,6871,0.39150050938727987,0.6084994906127201,0.38856823291082954,0.6114317670891705
1997,2720,4061,6781,0.40112077864621737,0.5988792213537826,0.39275241482262546,0.6072475851773745
1998,3267,4681,7948,0.41104680422747863,0.5889531957725214,0.3988505446242432,0.6011494553757568
1999,3363,5018,8381,0.4012647655411049,0.5987352344588951,0.3996552849298638,0.6003447150701362
2000,3759,5892,9651,0.3894933167547404,0.6105066832452596,0.3962679622048227,0.6037320377951774
2001,3978,6301,10279,0.38700262671466096,0.612997373285339,0.3931795170414355,0.6068204829585646
2002,6310,8501,14811,0.4260347039362636,0.5739652960637364,0.40413124600637823,0.5958687539936218
2003,5951,8811,14762,0.40312965722801786,0.5968703427719821,0.40379738308025814,0.596202616919742
2004,8216,11144,19360,0.4243801652892562,0.5756198347107438,0.4106583104832575,0.5893416895167426
2005,8902,12921,21823,0.40791825138615223,0.5920817486138478,0.4097449574508891,0.590255042549111
2006,12076,15589,27665,0.436508223386951,0.563491776613049,0.4186660460962431,0.581333953903757
2007,13081,17302,30383,0.4305368133495705,0.5694631866504295,0.4226229685140189,0.5773770314859812
2008,13707,18222,31929,0.4292962510570328,0.5707037489429672,0.4248473960283569,0.5751526039716433
2009,13987,20004,33991,0.4114912771027625,0.5885087228972375,0.4203953563864921,0.579604643613508
2010,16213,22726,38939,0.4163691928400832,0.5836308071599168,0.4190533018710225,0.5809466981289777
2011,16326,24313,40639,0.40173232609070103,0.5982676739092989,0.41327964327758204,0.5867203567224182
2012,18233,27275,45508,0.40065482992001406,0.5993451700799859,0.40907137215839273,0.5909286278416075
2013,19806,31285,51091,0.3876612319195162,0.6123387680804838,0.4019346587454339,0.5980653412545663
2014,21680,34644,56324,0.38491584404516727,0.6150841559548328,0.3962617205120117,0.6037382794879885
2015,21394,36129,57523,0.37192079689863183,0.6280792031013681,0.3881480793075518,0.6118519206924484
2016,23407,41966,65373,0.35805301883040397,0.641946981169596,0.37811639248183593,0.6218836075181643
2017,25843,49480,75323,0.3430957343706438,0.6569042656293562,0.36644283977810527,0.633557160221895
2018,32604,69253,101857,0.3200958206112491,0.6799041793887509,0.35099383338915324,0.649006166610847
2019,41105,97648,138753,0.2962458469366428,0.7037541530633572,0.3327445045716498,0.6672554954283505
2020,50579,128660,179239,0.28218747036080316,0.7178125296391968,0.3158921598347009,0.6841078401652994
2021,66241,177281,243522,0.27201238491799506,0.7279876150820049,0.30126556819579897,0.6987344318042013
2022,81163,210883,292046,0.27791169884196326,0.7220883011580368,0.29348094507785377,0.7065190549221465
2023,81090,247041,328131,0.24712690967936587,0.7528730903206341,0.27802959994502446,0.7219704000549758
2024,68858,262746,331604,0.20765129491803477,0.7923487050819652,0.2545701649360279,0.7454298350639723
"""


def prepare_data():
    """Parse and return the complete CSV embedded in this module."""
    rows = []
    for row in DictReader(StringIO(_CSV_DATA)):
        rows.append(
            {
                key: int(value) if key in {"year", "AI", "Domain", "total_classified"} else float(value)
                for key, value in row.items()
            }
        )
    return pd.DataFrame(rows)

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
        data["AI_share_ewma5"],
        data["Domain_share_ewma5"],
        labels=[config["legend.ai_label"], config["legend.domain_label"]],
        colors=[config["series.ai.color"], config["series.domain.color"]],
        alpha=config["series.area.alpha"],
        edgecolor=config["series.area.edgecolor"],
        linewidth=config["series.area.linewidth"],
    )
    ax.set_xlabel(
        config["axes.main.x_label"],
        family=config["typography.font_family"],
        fontsize=config["typography.label_size"],
    )
    ax.set_ylabel(
        config["axes.main.y_label"],
        family=config["typography.font_family"],
        fontsize=config["typography.label_size"],
    )
    ax.set_xlim(*config["axes.main.x_range"])
    ax.set_ylim(*config["axes.main.y_range"])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.tick_params(
        axis="both",
        direction="out",
        labelsize=config["typography.tick_size"],
        width=config["axes.main.spine_width"],
        length=config["axes.main.tick_length"],
    )
    for label in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        label.set_fontfamily(config["typography.font_family"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(config["axes.main.spine_width"])
    ax.spines["bottom"].set_linewidth(config["axes.main.spine_width"])
    ax.grid(False)
    legend = ax.legend(
        loc=config["legend.location"],
        frameon=config["legend.frame"],
        facecolor=config["legend.facecolor"],
        edgecolor="none",
        framealpha=config["legend.frame_alpha"],
        fontsize=config["legend.font_size"],
        labelspacing=0.25,
        borderaxespad=0.2,
        handlelength=1.5,
    )
    for text in legend.get_texts():
        text.set_fontfamily(config["typography.font_family"])
    fig.tight_layout()
    return fig


