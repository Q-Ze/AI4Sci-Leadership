"""Matplot Studio figure for Figure S1b."""

from __future__ import annotations

from csv import DictReader
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
import pandas as pd


PLOT_META = {
    "id": "fig-s1-b-line-annual-active-role-counts",
    "name": "Figure S1b — Annual active-role counts",
    "description": "Annual counts of AI-, AI4Sci-, and Domain-active AI4Sci participants.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "Each annual AI4Sci participant receives a role only when AI, AI4Sci, or Domain papers form a unique annual plurality. Tied author-years remain in the exported table but are not plotted. Lines show 5-year EWMAs for 1995–2024.",
    "data_export": {"csv": True, "json": True, "note": "Complete embedded calculation table, including excluded ties."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.45, 2.15], "min": 1.5, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.main.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Year", "required": True},
    {"path": "axes.main.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "AI4Sci participants", "required": True},
    {"path": "axes.main.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2024], "min": 1995, "max": 2024, "step": 1, "required": True},
    {"path": "axes.main.y_min", "label": "Y-axis minimum", "group": "Axes", "type": "number", "default": 0, "min": 0, "max": 1000000, "step": 1000, "required": True},
    {"path": "axes.main.y_tick_step", "label": "Y-axis tick interval", "group": "Axes", "type": "number", "default": 20000, "min": 1000, "max": 100000, "step": 1000, "required": True},
    {"path": "axes.main.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 3, "step": 0.1, "required": True},
    {"path": "axes.main.tick_length", "label": "Tick length", "group": "Axes", "type": "number", "default": 3.0, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "series.ai.color", "label": "AI-active color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.ai4sci.color", "label": "AI4Sci-active color", "group": "Series", "type": "color", "default": "#7A5195", "required": True},
    {"path": "series.domain.color", "label": "Domain-active color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.linewidth", "label": "Line width", "group": "Series", "type": "number", "default": 1.35, "min": 0.2, "max": 5, "step": 0.05, "required": True},
    {"path": "legend.ai_label", "label": "AI-active legend label", "group": "Legend", "type": "string", "default": "AI-active", "required": True},
    {"path": "legend.ai4sci_label", "label": "AI4Sci-active legend label", "group": "Legend", "type": "string", "default": "AI4Sci-active", "required": True},
    {"path": "legend.domain_label", "label": "Domain-active legend label", "group": "Legend", "type": "string", "default": "Domain-active", "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "default": "best", "options": ["best", "upper left", "upper right", "lower left", "lower right"], "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.2, "min": 4, "max": 16, "step": 0.1, "required": True},
    {"path": "legend.frame", "label": "Legend frame", "group": "Legend", "type": "boolean", "default": False, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.label_size", "label": "Axis-label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "typography.tick_size", "label": "Tick-label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 20, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [2.45, 2.15], "figure.facecolor": "#FFFFFF",
    "axes.main.x_label": "Year", "axes.main.y_label": "AI4Sci participants",
    "axes.main.x_range": [1995, 2024], "axes.main.y_min": 0,
    "axes.main.y_tick_step": 20000,
    "axes.main.spine_width": 0.6, "axes.main.tick_length": 3.0,
    "series.ai.color": "#3B6FB6", "series.ai4sci.color": "#7A5195",
    "series.domain.color": "#D55E5E", "series.linewidth": 1.35,
    "legend.ai_label": "AI-active", "legend.ai4sci_label": "AI4Sci-active",
    "legend.domain_label": "Domain-active",
    "legend.location": "best", "legend.font_size": 7.2, "legend.frame": False,
    "typography.font_family": "Arial", "typography.label_size": 9, "typography.tick_size": 8,
}


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}; values.update(settings or {}); return values


_CSV_DATA = """year,role,n,n_ewma5
1995,AI,645,645.0
1995,AI4Sci,3493,3493.0
1995,Domain,893,893.0
1995,Tie (excluded),1577,1577.0
1996,AI,869,719.6666666666667
1996,AI4Sci,3937,3641.0
1996,Domain,1067,951.0
1996,Tie (excluded),1699,1617.6666666666667
1997,AI,773,737.4444444444446
1997,AI4Sci,3859,3713.666666666667
1997,Domain,1015,972.3333333333335
1997,Tie (excluded),1760,1665.1111111111113
1998,AI,1061,845.2962962962964
1998,AI4Sci,4338,3921.7777777777783
1998,Domain,1232,1058.8888888888891
1998,Tie (excluded),2098,1809.4074074074076
1999,AI,952,880.8641975308644
1999,AI4Sci,4772,4205.185185185186
1999,Domain,1294,1137.2592592592596
1999,Tie (excluded),2161,1926.604938271605
2000,AI,1265,1008.9094650205764
2000,AI4Sci,5151,4520.456790123458
2000,Domain,1562,1278.8395061728397
2000,Tie (excluded),2579,2144.069958847737
2001,AI,1352,1123.2729766803843
2001,AI4Sci,5400,4813.637860082305
2001,Domain,1768,1441.8930041152266
2001,Tie (excluded),2682,2323.379972565158
2002,AI,2146,1464.1819844535894
2002,AI4Sci,7576,5734.42524005487
2002,Domain,2889,1924.2620027434846
2002,Tie (excluded),3615,2753.9199817101053
2003,AI,2163,1697.1213229690597
2003,AI4Sci,7403,6290.616826703247
2003,Domain,2815,2221.1746684956565
2003,Tie (excluded),3735,3080.9466544734037
2004,AI,2626,2006.7475486460398
2004,AI4Sci,9898,7493.077884468832
2004,Domain,3796,2746.116445663771
2004,Tie (excluded),4767,3642.9644363156026
2005,AI,3248,2420.498365764027
2005,AI4Sci,10603,8529.718589645889
2005,Domain,4638,3376.744297109181
2005,Tie (excluded),5442,4242.642957543736
2006,AI,3873,2904.665577176018
2006,AI4Sci,13082,10047.145726430594
2006,Domain,6409,4387.496198072788
2006,Tie (excluded),6995,5160.095305029157
2007,AI,3081,2963.4437181173453
2007,AI4Sci,14659,11584.430484287062
2007,Domain,7919,5564.664132048525
2007,Tie (excluded),7726,6015.396870019438
2008,AI,3850,3258.962478744897
2008,AI4Sci,14805,12657.953656191376
2008,Domain,8367,6498.77608803235
2008,Tie (excluded),8038,6689.597913346292
2009,AI,4214,3577.308319163265
2009,AI4Sci,15397,13570.969104127584
2009,Domain,9500,7499.184058688234
2009,Tie (excluded),8380,7253.065275564195
2010,AI,4633,3929.205546108844
2010,AI4Sci,17895,15012.312736085058
2010,Domain,10933,8643.789372458823
2010,Tie (excluded),9542,8016.043517042797
2011,AI,5175,4344.470364072563
2011,AI4Sci,18573,16199.208490723373
2011,Domain,11041,9442.859581639215
2011,Tie (excluded),10072,8701.362344695199
2012,AI,5355,4681.313576048376
2012,AI4Sci,20809,17735.80566048225
2012,Domain,12980,10621.906387759478
2012,Tie (excluded),11275,9559.241563130134
2013,AI,5126,4829.542384032251
2013,AI4Sci,24023,19831.537106988166
2013,Domain,15142,12128.604258506319
2013,Tie (excluded),12476,10531.49437542009
2014,AI,5652,5103.694922688168
2014,AI4Sci,26017,21893.35807132544
2014,Domain,17000,13752.402839004213
2014,Tie (excluded),13759,11607.329583613395
2015,AI,5555,5254.129948458779
2015,AI4Sci,26792,23526.23871421696
2015,Domain,17591,15031.93522600281
2015,Tie (excluded),14085,12433.21972240893
2016,AI,6133,5547.086632305853
2016,AI4Sci,31030,26027.492476144642
2016,Domain,19722,16595.29015066854
2016,Tie (excluded),15894,13586.813148272622
2017,AI,6430,5841.391088203902
2017,AI4Sci,35926,29326.99498409643
2017,Domain,23727,18972.526767112362
2017,Tie (excluded),17984,15052.542098848415
2018,AI,7918,6533.5940588026015
2018,AI4Sci,47867,35506.996656064286
2018,Domain,33977,23974.017844741575
2018,Tie (excluded),24003,18036.028065898943
2019,AI,8469,7178.729372535068
2019,AI4Sci,65693,45568.997770709524
2019,Domain,48536,32161.34522982772
2019,Tie (excluded),31725,22599.018710599295
2020,AI,9312,7889.819581690046
2020,AI4Sci,83664,58267.331847139685
2020,Domain,66478,43600.23015321848
2020,Tie (excluded),39608,28268.67914039953
2021,AI,9529,8436.213054460031
2021,AI4Sci,113641,76725.22123142646
2021,Domain,93746,60315.48676881232
2021,Tie (excluded),52662,36399.78609359969
2022,AI,9485,8785.808702973354
2022,AI4Sci,139685,97711.81415428431
2022,Domain,110984,77204.99117920821
2022,Tie (excluded),60204,44334.524062399796
2023,AI,10319,9296.872468648904
2023,AI4Sci,158514,117979.20943618954
2023,Domain,125388,93265.99411947215
2023,Tie (excluded),66528,51732.3493749332
2024,AI,20648,13080.581645765935
2024,AI4Sci,156039,130665.80629079304
2024,Domain,115165,100565.66274631477
2024,Tie (excluded),71261,58241.8995832888
"""


def prepare_data():
    rows = []
    for row in DictReader(StringIO(_CSV_DATA)):
        rows.append({"year": int(row["year"]), "role": row["role"], "n": int(row["n"]), "n_ewma5": float(row["n_ewma5"])})
    return pd.DataFrame(rows)


def render(data, settings):
    config = _resolved(settings); fig, ax = plt.subplots(figsize=tuple(config["figure.size"]), facecolor=config["figure.facecolor"]); ax.set_facecolor(config["figure.facecolor"])
    for role in ["AI", "AI4Sci", "Domain"]:
        subset=data[data["role"]==role]; ax.plot(subset["year"], subset["n_ewma5"], color=config[f"series.{role.lower()}.color"], linewidth=config["series.linewidth"], label=config[f"legend.{role.lower()}_label"])
    ax.set_xlabel(config["axes.main.x_label"], family=config["typography.font_family"], fontsize=config["typography.label_size"]); ax.set_ylabel(config["axes.main.y_label"], family=config["typography.font_family"], fontsize=config["typography.label_size"])
    ax.set_xlim(*config["axes.main.x_range"]); ax.set_ylim(bottom=config["axes.main.y_min"]); ax.yaxis.set_major_locator(MultipleLocator(config["axes.main.y_tick_step"])); ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value / 1000:.0f}k" if value >= 1000 else f"{value:.0f}"))
    ax.tick_params(axis="both", direction="out", labelsize=config["typography.tick_size"], width=config["axes.main.spine_width"], length=config["axes.main.tick_length"])
    for label in [*ax.get_xticklabels(), *ax.get_yticklabels()]: label.set_fontfamily(config["typography.font_family"])
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False); ax.spines["left"].set_linewidth(config["axes.main.spine_width"]); ax.spines["bottom"].set_linewidth(config["axes.main.spine_width"]); ax.grid(False)
    legend=ax.legend(loc=config["legend.location"], frameon=config["legend.frame"], fontsize=config["legend.font_size"], labelspacing=0.3, borderaxespad=0.2)
    for text in legend.get_texts(): text.set_fontfamily(config["typography.font_family"])
    fig.tight_layout(); return fig


