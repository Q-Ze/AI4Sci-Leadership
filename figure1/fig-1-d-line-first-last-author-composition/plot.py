"""Matplot Studio figure for Figure 1d."""

from __future__ import annotations

from csv import DictReader
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "fig-1-d-line-first-last-author-composition",
    "name": "Figure 1d — First- and last-author composition",
    "description": "AI and Domain Specialist shares in first- and last-author positions.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "Annual first- and last-author positions on AI4Sci papers are classified using fixed venue-based author classes. Each position-specific denominator includes AI and Domain Specialists only. Lines show 5-year EWMAs for 1995–2024.",
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
    {"path": "axes.main.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Share of author positions", "required": True},
    {"path": "axes.main.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2024], "min": 1995, "max": 2024, "step": 1, "required": True},
    {"path": "axes.main.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0.25, 0.80], "min": 0, "max": 1, "step": 0.05, "required": True},
    {"path": "axes.main.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 3, "step": 0.1, "required": True},
    {"path": "axes.main.tick_length", "label": "Tick length", "group": "Axes", "type": "number", "default": 3.0, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "series.ai.color", "label": "AI Specialist color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.domain.color", "label": "Domain Specialist color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.first.linestyle", "label": "First-author line style", "group": "Series", "type": "select", "default": "-", "options": ["-", "--", ":", "-."], "required": True},
    {"path": "series.last.linestyle", "label": "Last-author line style", "group": "Series", "type": "select", "default": "--", "options": ["-", "--", ":", "-."], "required": True},
    {"path": "series.linewidth", "label": "Line width", "group": "Series", "type": "number", "default": 1.35, "min": 0.2, "max": 5, "step": 0.05, "required": True},
    {"path": "legend.ai_label", "label": "AI legend label", "group": "Legend", "type": "string", "default": "AI-origin", "required": True},
    {"path": "legend.domain_label", "label": "Domain legend label", "group": "Legend", "type": "string", "default": "Domain-origin", "required": True},
    {"path": "legend.first_label", "label": "First-author legend label", "group": "Legend", "type": "string", "default": "First author", "required": True},
    {"path": "legend.last_label", "label": "Last-author legend label", "group": "Legend", "type": "string", "default": "Last author", "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "default": "upper left", "options": ["upper left", "upper right", "lower left", "lower right"], "required": True},
    {"path": "legend.columns", "label": "Legend columns", "group": "Legend", "type": "integer", "default": 2, "min": 1, "max": 4, "step": 1, "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.2, "min": 4, "max": 16, "step": 0.1, "required": True},
    {"path": "legend.frame", "label": "Legend frame", "group": "Legend", "type": "boolean", "default": False, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.label_size", "label": "Axis-label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "typography.tick_size", "label": "Tick-label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 20, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [2.45, 2.15],
    "figure.facecolor": "#FFFFFF",
    "axes.main.x_label": "Year",
    "axes.main.y_label": "Share of author positions",
    "axes.main.x_range": [1995, 2024],
    "axes.main.y_range": [0.25, 0.80],
    "axes.main.spine_width": 0.6,
    "axes.main.tick_length": 3.0,
    "series.ai.color": "#3B6FB6",
    "series.domain.color": "#D55E5E",
    "series.first.linestyle": "-",
    "series.last.linestyle": "--",
    "series.linewidth": 1.35,
    "legend.ai_label": "AI-origin",
    "legend.domain_label": "Domain-origin",
    "legend.first_label": "First author",
    "legend.last_label": "Last author",
    "legend.location": "upper left",
    "legend.columns": 2,
    "legend.font_size": 7.2,
    "legend.frame": False,
    "typography.font_family": "Arial",
    "typography.label_size": 9,
    "typography.tick_size": 8,
}


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


_CSV_DATA = """year,first_ai_n,first_domain_n,first_ai_share,first_domain_share,first_ai_share_ewma5,first_domain_share_ewma5,last_ai_n,last_domain_n,last_ai_share,last_domain_share,last_ai_share_ewma5,last_domain_share_ewma5
1995,1348,1957,0.40786686838124053,0.5921331316187595,0.40786686838124053,0.5921331316187595,846,1311,0.39221140472878996,0.60778859527121,0.39221140472878996,0.60778859527121
1996,1543,2254,0.4063734527258362,0.5936265472741639,0.40736906316277244,0.5926309368372276,991,1571,0.3868071818891491,0.6131928181108509,0.3904099971155764,0.6095900028844237
1997,1583,2177,0.42101063829787233,0.5789893617021277,0.4119162548744725,0.5880837451255276,948,1514,0.3850528025995126,0.6149471974004874,0.3886242656102218,0.6113757343897783
1998,1812,2546,0.41578705828361634,0.5842129417163837,0.41320652267752045,0.5867934773224797,1163,1676,0.4096512856639662,0.5903487143360339,0.3956332722948033,0.6043667277051968
1999,1894,2613,0.4202351897049035,0.5797648102950965,0.41554941168664816,0.584450588313352,1190,1791,0.3991949010399195,0.6008050989600805,0.3968204818765087,0.6031795181234914
2000,2111,3059,0.40831721470019344,0.5916827852998066,0.41313867935783,0.5868613206421702,1259,2086,0.3763826606875934,0.6236173393124066,0.39000787481353694,0.6099921251864632
2001,2184,3350,0.3946512468377304,0.6053487531622697,0.40697620185113015,0.5930237981488701,1397,2167,0.39197530864197533,0.6080246913580247,0.3906636860896831,0.6093363139103171
2002,3351,4450,0.4295603127804128,0.5704396872195873,0.4145042388275577,0.5854957611724425,2257,3115,0.4201414743112435,0.5798585256887565,0.4004896154968699,0.5995103845031302
2003,3036,4419,0.4072434607645875,0.5927565392354125,0.41208397947323433,0.587916020526766,2091,2978,0.41250739790885776,0.5874926020911423,0.40449554296753254,0.5955044570324676
2004,4447,5755,0.4358949225642031,0.5641050774357969,0.4200209605035573,0.5799790394964429,3072,4114,0.4274979126078486,0.5725020873921514,0.4121629995143046,0.5878370004856955
2005,4589,6364,0.4189719711494568,0.5810280288505433,0.41967129738552383,0.5803287026144764,3167,4452,0.41567134794592464,0.5843286520540754,0.41333244899151134,0.5866675510084889
2006,6362,7540,0.45763199539634586,0.5423680046036542,0.43232486338913123,0.567675136610869,4491,5851,0.4342486946432025,0.5657513053567975,0.4203045308754084,0.5796954691245918
2007,7194,8438,0.4602098259979529,0.5397901740020471,0.4416198509254052,0.558380149074595,5081,6640,0.43349543554304243,0.5665045644569576,0.4247014990979531,0.575298500902047
2008,7179,8721,0.4515094339622642,0.5484905660377358,0.4449163786043582,0.555083621395642,4960,6514,0.4322816803207251,0.5677183196792749,0.42722822617221046,0.5727717738277897
2009,7178,9363,0.43395199806541324,0.5660480019345868,0.4412615850913766,0.5587384149086236,5159,7041,0.4228688524590164,0.5771311475409836,0.42577510160114584,0.5742248983988544
2010,8453,10766,0.4398251730058796,0.5601748269941204,0.4407827810628776,0.5592172189371225,6221,8391,0.42574596222283057,0.5742540377771694,0.42576538847504075,0.5742346115249595
2011,8480,11188,0.4311572096806996,0.5688427903193004,0.4375742572688183,0.5624257427311818,6228,8632,0.4191117092866756,0.5808882907133244,0.4235474954122524,0.5764525045877478
2012,9082,11803,0.4348575532678956,0.5651424467321043,0.43666868926851077,0.5633313107314893,6707,9870,0.40459673040960364,0.5954032695903964,0.41723057374470285,0.5827694262552974
2013,9837,13415,0.423060381902632,0.5769396180973679,0.43213258681321787,0.5678674131867822,7495,11161,0.4017474271012007,0.5982525728987993,0.4120695248635355,0.5879304751364647
2014,10177,14488,0.41260896006486925,0.5873910399351308,0.42562471123043505,0.5743752887695651,8116,12099,0.40148404650012365,0.5985159534998763,0.40854103207573156,0.5914589679242686
2015,9732,14582,0.4002632228345809,0.5997367771654191,0.4171708817651503,0.5828291182348498,8060,12355,0.3948077394072986,0.6051922605927015,0.4039632678529206,0.5960367321470795
2016,10509,16433,0.39006012916635735,0.6099398708336427,0.40813396423221937,0.5918660357677807,9135,14191,0.39162308153991254,0.6083769184600875,0.3998498724152513,0.6001501275847488
2017,10958,18990,0.3659008948844664,0.6340991051155336,0.3940562744496351,0.605943725550365,9742,16362,0.3731995096536929,0.626800490346307,0.39096641816139854,0.6090335818386016
2018,13855,25240,0.3543931449034403,0.6456068550965597,0.38083523126757024,0.61916476873243,12709,21689,0.3694691551834409,0.6305308448165591,0.38380066383541267,0.6161993361645874
2019,16948,35356,0.32402875497093914,0.6759712450290609,0.3618997391686932,0.638100260831307,16056,30629,0.3439220306308236,0.6560779693691764,0.3705077861005497,0.6294922138994505
2020,20693,44794,0.31598637897598,0.6840136210240201,0.3465952857711222,0.653404714228878,19627,38907,0.33530939283151673,0.6646906071684833,0.3587749883442054,0.6412250116557948
2021,27499,61357,0.30947825695507336,0.6905217430449266,0.33422294283243925,0.665777057167561,26436,52897,0.33322829087517175,0.6667717091248283,0.35025942252119424,0.6497405774788061
2022,31917,69954,0.3133080071855582,0.6866919928144418,0.32725129761681226,0.672748702383188,30098,61465,0.3287135633389033,0.6712864366610968,0.3430774694604306,0.6569225305395697
2023,31002,80560,0.27789032107706924,0.7221096789229308,0.31079763877023125,0.6892023612297689,29277,68699,0.29881807789662773,0.7011819221033723,0.328324338939163,0.6716756610608372
2024,24993,82673,0.23213456430070775,0.7678654356992922,0.2845766139470568,0.7154233860529433,22357,66383,0.251938246562993,0.748061753437007,0.30286230814710635,0.6971376918528939
"""


def prepare_data():
    """Parse and return the complete CSV embedded in this module."""
    integer_columns = {"year", "first_ai_n", "first_domain_n", "last_ai_n", "last_domain_n"}
    rows = []
    for row in DictReader(StringIO(_CSV_DATA)):
        rows.append(
            {
                key: int(value) if key in integer_columns else float(value)
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
    series = [
        ("first_ai_share_ewma5", "series.ai.color", "series.first.linestyle"),
        ("last_ai_share_ewma5", "series.ai.color", "series.last.linestyle"),
        ("first_domain_share_ewma5", "series.domain.color", "series.first.linestyle"),
        ("last_domain_share_ewma5", "series.domain.color", "series.last.linestyle"),
    ]
    for column, color_path, linestyle_path in series:
        ax.plot(
            data["year"],
            data[column],
            color=config[color_path],
            linewidth=config["series.linewidth"],
            linestyle=config[linestyle_path],
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
    legend = ax.legend(
        handles=[
            Line2D([], [], color=config["series.ai.color"], linewidth=config["series.linewidth"], label=config["legend.ai_label"]),
            Line2D([], [], color=config["series.domain.color"], linewidth=config["series.linewidth"], label=config["legend.domain_label"]),
            Line2D([], [], color="#333333", linewidth=config["series.linewidth"], linestyle=config["series.first.linestyle"], label=config["legend.first_label"]),
            Line2D([], [], color="#333333", linewidth=config["series.linewidth"], linestyle=config["series.last.linestyle"], label=config["legend.last_label"]),
        ],
        loc=config["legend.location"],
        frameon=config["legend.frame"],
        fontsize=config["legend.font_size"],
        handlelength=2.3,
        labelspacing=0.3,
        borderaxespad=0.2,
        ncols=config["legend.columns"],
    )
    for text in legend.get_texts():
        text.set_fontfamily(config["typography.font_family"])
    fig.tight_layout()
    return fig


