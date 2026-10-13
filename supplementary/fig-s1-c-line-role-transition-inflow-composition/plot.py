"""Matplot Studio figure for Figure S1c."""

from __future__ import annotations

from csv import DictReader
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "fig-s1-c-line-role-transition-inflow-composition",
    "name": "Figure S1c — AI4Sci-active inflow composition",
    "description": "Line chart of AI-active and Domain-active sources among transitions into AI4Sci-active.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "Among authors ever observed on AI4Sci papers, unique-plurality annual roles are sequenced after tied years are removed. Shares use transitions from AI-active or Domain-active into AI4Sci-active as the denominator. Lines show 5-year EWMAs for 1996–2024.",
    "data_export": {"csv": True, "json": True, "note": "Complete embedded calculation table."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.45, 2.15], "min": 1.5, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.main.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Year", "required": True},
    {"path": "axes.main.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "AI4Sci-active inflows share", "required": True},
    {"path": "axes.main.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1996, 2024], "min": 1996, "max": 2024, "step": 1, "required": True},
    {"path": "axes.main.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0, 1], "min": 0, "max": 1, "step": 0.05, "required": True},
    {"path": "axes.main.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 3, "step": 0.1, "required": True},
    {"path": "axes.main.tick_length", "label": "Tick length", "group": "Axes", "type": "number", "default": 3.0, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "series.ai.color", "label": "AI-active source color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.domain.color", "label": "Domain-active source color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.linewidth", "label": "Line width", "group": "Series", "type": "number", "default": 1.35, "min": 0.2, "max": 5, "step": 0.05, "required": True},
    {"path": "legend.ai_label", "label": "AI-source legend label", "group": "Legend", "type": "string", "default": "AI-active source", "required": True},
    {"path": "legend.domain_label", "label": "Domain-source legend label", "group": "Legend", "type": "string", "default": "Domain-active source", "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "default": "upper left", "options": ["upper left", "upper right", "lower left", "lower right"], "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.2, "min": 4, "max": 16, "step": 0.1, "required": True},
    {"path": "legend.frame", "label": "Legend frame", "group": "Legend", "type": "boolean", "default": True, "required": True},
    {"path": "legend.facecolor", "label": "Legend background", "group": "Legend", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "legend.frame_alpha", "label": "Legend opacity", "group": "Legend", "type": "number", "default": 0.88, "min": 0, "max": 1, "step": 0.05, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.label_size", "label": "Axis-label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "typography.tick_size", "label": "Tick-label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 20, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [2.45, 2.15], "figure.facecolor": "#FFFFFF",
    "axes.main.x_label": "Year", "axes.main.y_label": "AI4Sci-active inflows share",
    "axes.main.x_range": [1996, 2024], "axes.main.y_range": [0, 1],
    "axes.main.spine_width": 0.6, "axes.main.tick_length": 3.0,
    "series.ai.color": "#3B6FB6", "series.domain.color": "#D55E5E", "series.linewidth": 1.35,
    "legend.ai_label": "AI-active source", "legend.domain_label": "Domain-active source",
    "legend.location": "upper left", "legend.font_size": 7.2, "legend.frame": True,
    "legend.facecolor": "#FFFFFF", "legend.frame_alpha": 0.88,
    "typography.font_family": "Arial", "typography.label_size": 9, "typography.tick_size": 8,
}


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}; values.update(settings or {}); return values


_CSV_DATA = """year,n_from_ai,n_from_domain,n_total_inflow,ai_source_share,domain_source_share,ai_source_share_ewma5,domain_source_share_ewma5
1996,330,520,850,0.38823529411764707,0.611764705882353,0.38823529411764707,0.611764705882353
1997,586,679,1265,0.4632411067193676,0.5367588932806324,0.4132372316515539,0.5867627683484462
1998,785,937,1722,0.45586527293844364,0.5441347270615563,0.42744657874718384,0.5725534212528163
1999,876,1200,2076,0.42196531791907516,0.5780346820809249,0.425619491804481,0.5743805081955192
2000,1019,1277,2296,0.44381533101045295,0.556184668989547,0.431684771539805,0.5683152284601952
2001,1036,1434,2470,0.4194331983805668,0.5805668016194332,0.42760091382005894,0.5723990861799413
2002,1489,1947,3436,0.43335273573923166,0.5666472642607684,0.42951818779311657,0.5704818122068838
2003,1395,2005,3400,0.4102941176470588,0.5897058823529412,0.4231101644110974,0.5768898355889029
2004,1933,2532,4465,0.43292273236282197,0.567077267637178,0.4263810203950056,0.5736189796049946
2005,1936,2865,4801,0.40324932305769634,0.5967506769423037,0.4186704546159025,0.5813295453840976
2006,2539,3522,6061,0.41890777099488535,0.5810922290051147,0.4187495600755635,0.5812504399244367
2007,3351,4139,7490,0.4473965287049399,0.55260347129506,0.42829854961868896,0.5717014503813111
2008,2705,4610,7315,0.3697881066302119,0.6302118933697881,0.40879506862252996,0.5912049313774701
2009,2633,5120,7753,0.339610473365149,0.6603895266348511,0.3857335368700696,0.6142664631299304
2010,3216,5743,8959,0.3589686348922871,0.641031365107713,0.37681190287747546,0.6231880971225245
2011,3072,5939,9011,0.34091665741871047,0.6590833425812895,0.3648468210578872,0.6351531789421129
2012,3547,6777,10324,0.34356838434715226,0.6564316156528477,0.3577540088209756,0.6422459911790246
2013,4128,7970,12098,0.34121342370639773,0.6587865762936023,0.35224048044944967,0.6477595195505506
2014,4235,8893,13128,0.32259293113954907,0.677407068860451,0.34235796401281615,0.6576420359871841
2015,4436,9295,13731,0.3230645983540893,0.6769354016459107,0.33592684212657387,0.6640731578734262
2016,5007,10937,15944,0.31403662819869543,0.6859633718013045,0.32863010415061444,0.6713698958493857
2017,5247,12875,18122,0.2895375786337049,0.7104624213662951,0.3155992623116446,0.6844007376883555
2018,6715,17250,23965,0.2802002920926351,0.7197997079073649,0.3037996055719748,0.6962003944280254
2019,8820,23319,32139,0.2744329319518342,0.7255670680481657,0.29401071436526127,0.705989285634739
2020,10305,29880,40185,0.2564389697648376,0.7435610302351624,0.2814867994984534,0.7185132005015468
2021,13188,40229,53417,0.2468876949285808,0.7531123050714192,0.2699537646418292,0.7300462353581709
2022,12335,46398,58733,0.2100182180375598,0.7899817819624402,0.24997524910707275,0.7500247508929274
2023,12618,58926,71544,0.1763669909426367,0.8236330090573633,0.22543916305226075,0.7745608369477395
2024,10355,60053,70408,0.14707135552778094,0.852928644472219,0.19931656054410082,0.8006834394558995
"""


def prepare_data():
    integers = {"year", "n_from_ai", "n_from_domain", "n_total_inflow"}; rows = []
    for row in DictReader(StringIO(_CSV_DATA)):
        rows.append({key: int(value) if key in integers else float(value) for key, value in row.items()})
    return pd.DataFrame(rows)


def render(data, settings):
    config = _resolved(settings); fig, ax = plt.subplots(figsize=tuple(config["figure.size"]), facecolor=config["figure.facecolor"]); ax.set_facecolor(config["figure.facecolor"])
    ax.plot(data["year"], data["ai_source_share_ewma5"], color=config["series.ai.color"], linewidth=config["series.linewidth"], label=config["legend.ai_label"])
    ax.plot(data["year"], data["domain_source_share_ewma5"], color=config["series.domain.color"], linewidth=config["series.linewidth"], label=config["legend.domain_label"])
    ax.set_xlabel(config["axes.main.x_label"], family=config["typography.font_family"], fontsize=config["typography.label_size"]); ax.set_ylabel(config["axes.main.y_label"], family=config["typography.font_family"], fontsize=config["typography.label_size"])
    ax.set_xlim(*config["axes.main.x_range"]); ax.set_ylim(*config["axes.main.y_range"]); ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.tick_params(axis="both", direction="out", labelsize=config["typography.tick_size"], width=config["axes.main.spine_width"], length=config["axes.main.tick_length"])
    for label in [*ax.get_xticklabels(), *ax.get_yticklabels()]: label.set_fontfamily(config["typography.font_family"])
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False); ax.spines["left"].set_linewidth(config["axes.main.spine_width"]); ax.spines["bottom"].set_linewidth(config["axes.main.spine_width"]); ax.grid(False)
    legend=ax.legend(loc=config["legend.location"], frameon=config["legend.frame"], facecolor=config["legend.facecolor"], edgecolor="none", framealpha=config["legend.frame_alpha"], fontsize=config["legend.font_size"])
    for text in legend.get_texts(): text.set_fontfamily(config["typography.font_family"])
    fig.tight_layout(); return fig


