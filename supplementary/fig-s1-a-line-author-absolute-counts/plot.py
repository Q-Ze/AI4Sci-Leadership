"""Matplot Studio figure for Figure S1a."""

from __future__ import annotations

from csv import DictReader
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd


PLOT_META = {
    "id": "fig-s1-a-line-author-absolute-counts",
    "name": "Figure S1a — Annual author counts",
    "description": "Annual distinct AI- and Domain-origin authors on AI4Sci papers.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "Authors are deduplicated within year among AI4Sci papers and classified by fixed venue-based origin. Lines show 5-year EWMAs for 1995–2024.",
    "data_export": {"csv": True, "json": True, "note": "Complete embedded calculation table."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.45, 2.15], "min": 1.5, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.main.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Year", "required": True},
    {"path": "axes.main.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Distinct authors", "required": True},
    {"path": "axes.main.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2024], "min": 1995, "max": 2024, "step": 1, "required": True},
    {"path": "axes.main.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 3, "step": 0.1, "required": True},
    {"path": "axes.main.tick_length", "label": "Tick length", "group": "Axes", "type": "number", "default": 3.0, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "series.ai.color", "label": "AI Specialist color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.domain.color", "label": "Domain Specialist color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.linewidth", "label": "Line width", "group": "Series", "type": "number", "default": 1.3, "min": 0.2, "max": 5, "step": 0.1, "required": True},
    {"path": "legend.ai_label", "label": "AI legend label", "group": "Legend", "type": "string", "default": "AI Specialist", "required": True},
    {"path": "legend.domain_label", "label": "Domain legend label", "group": "Legend", "type": "string", "default": "Domain Specialist", "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "default": "best", "options": ["best", "upper left", "upper right", "lower left", "lower right"], "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 8, "min": 4, "max": 16, "step": 0.5, "required": True},
    {"path": "legend.frame", "label": "Legend frame", "group": "Legend", "type": "boolean", "default": False, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.label_size", "label": "Axis-label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "typography.tick_size", "label": "Tick-label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 20, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [2.45, 2.15], "figure.facecolor": "#FFFFFF",
    "axes.main.x_label": "Year", "axes.main.y_label": "Distinct authors",
    "axes.main.x_range": [1995, 2024],
    "axes.main.spine_width": 0.6, "axes.main.tick_length": 3.0,
    "series.ai.color": "#3B6FB6", "series.domain.color": "#D55E5E",
    "series.linewidth": 1.3,
    "legend.ai_label": "AI Specialist", "legend.domain_label": "Domain Specialist",
    "legend.location": "best",
    "legend.font_size": 8, "legend.frame": False,
    "typography.font_family": "Arial", "typography.label_size": 9,
    "typography.tick_size": 8,
}


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


_CSV_DATA = """year,AI,Domain,AI_ewma5,Domain_ewma5
1995,2347,3716,2347.0,3716.0
1996,2690,4181,2461.3333333333335,3871.0
1997,2720,4061,2547.5555555555557,3934.3333333333335
1998,3267,4681,2787.3703703703704,4183.222222222223
1999,3363,5018,2979.246913580247,4461.481481481482
2000,3759,5892,3239.164609053498,4938.3209876543215
2001,3978,6301,3485.4430727023323,5392.547325102882
2002,6310,8501,4426.962048468222,6428.698216735254
2003,5951,8811,4934.974698978815,7222.798811156837
2004,8216,11144,6028.64979931921,8529.865874104558
2005,8902,12921,6986.43319954614,9993.577249403039
2006,12076,15589,8682.955466364094,11858.718166268693
2007,13081,17302,10148.970310909397,13673.145444179128
2008,13707,18222,11334.980207272933,15189.43029611942
2009,13987,20004,12218.986804848622,16794.286864079615
2010,16213,22726,13550.32453656575,18771.524576053078
2011,16326,24313,14475.549691043834,20618.683050702053
2012,18233,27275,15728.033127362556,22837.455367134702
2013,19806,31285,17087.355418241707,25653.303578089803
2014,21680,34644,18618.23694549447,28650.202385393204
2015,21394,36129,19543.491296996315,31143.134923595473
2016,23407,41966,20831.327531330877,34750.756615730315
2017,25843,49480,22501.885020887254,39660.50441048688
2018,32604,69253,25869.256680591505,49524.66960699126
2019,41105,97648,30947.837787061006,65565.77973799418
2020,50579,128660,37491.55852470733,86597.18649199612
2021,66241,177281,47074.70568313822,116825.12432799742
2022,81163,210883,58437.470455425486,148177.74955199828
2023,81090,247041,65988.31363695033,181132.16636799887
2024,68858,262746,66944.87575796689,208336.77757866593
"""


def prepare_data():
    rows = []
    for row in DictReader(StringIO(_CSV_DATA)):
        rows.append({key: int(value) if key in {"year", "AI", "Domain"} else float(value) for key, value in row.items()})
    return pd.DataFrame(rows)


def render(data, settings):
    config = _resolved(settings)
    fig, ax = plt.subplots(figsize=tuple(config["figure.size"]), facecolor=config["figure.facecolor"])
    ax.set_facecolor(config["figure.facecolor"])
    ax.plot(data["year"], data["AI_ewma5"], color=config["series.ai.color"], linewidth=config["series.linewidth"], label=config["legend.ai_label"])
    ax.plot(data["year"], data["Domain_ewma5"], color=config["series.domain.color"], linewidth=config["series.linewidth"], label=config["legend.domain_label"])
    ax.set_xlabel(config["axes.main.x_label"], family=config["typography.font_family"], fontsize=config["typography.label_size"])
    ax.set_ylabel(config["axes.main.y_label"], family=config["typography.font_family"], fontsize=config["typography.label_size"])
    ax.set_xlim(*config["axes.main.x_range"])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value / 1000:.0f}k" if value >= 1000 else f"{value:.0f}"))
    ax.tick_params(axis="both", direction="out", labelsize=config["typography.tick_size"], width=config["axes.main.spine_width"], length=config["axes.main.tick_length"])
    for label in [*ax.get_xticklabels(), *ax.get_yticklabels()]: label.set_fontfamily(config["typography.font_family"])
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(config["axes.main.spine_width"]); ax.spines["bottom"].set_linewidth(config["axes.main.spine_width"])
    ax.grid(False)
    legend = ax.legend(loc=config["legend.location"], frameon=config["legend.frame"], fontsize=config["legend.font_size"])
    for text in legend.get_texts(): text.set_fontfamily(config["typography.font_family"])
    fig.tight_layout()
    return fig


