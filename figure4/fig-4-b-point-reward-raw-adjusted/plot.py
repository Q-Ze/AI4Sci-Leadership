"""Manuscript Figure 4B: raw and adjusted external rewards."""

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd

PLOT_META = {
    "id": "fig-4-b-point-reward-raw-adjusted",
    "name": "Figure 4B — External rewards",
    "description": "Raw outcome shares and adjusted marginal probabilities for NIH, NSF, and news.",
    "version": 1, "data_mode": "inline",
    "data_note": "Final raw and adjusted estimates with confidence intervals are embedded.",
    "data_export": {"csv": True, "json": True, "note": "Outcome-by-leader-by-specification estimates."},
}
PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 16, "step": 0.1, "required": True},
    {"path": "axes.main.ylabel", "label": "Y label", "group": "Axes", "type": "string", "default": "Outcome probability"},
    {"path": "axes.main.y_range", "label": "Y range", "group": "Axes", "type": "number_pair", "default": [0, 0.0145]},
    {"path": "series.ai.color", "label": "AI-led raw color", "group": "Series", "type": "color", "default": "#3B6FB6"},
    {"path": "series.domain.color", "label": "Domain-led raw color", "group": "Series", "type": "color", "default": "#D55E5E"},
    {"path": "series.adjusted.color", "label": "Adjusted marker color", "group": "Series", "type": "color", "default": "#202020"},
    {"path": "series.bars.width", "label": "Bar width", "group": "Series", "type": "number", "default": 0.34, "min": 0.05, "max": 0.9, "step": 0.01},
    {"path": "series.adjusted.marker_size", "label": "Diamond size", "group": "Series", "type": "number", "default": 3.6, "min": 1, "max": 20, "step": 0.2},
    {"path": "legend.visible", "label": "Show legend", "group": "Legend", "type": "boolean", "default": True},
    {"path": "typography.tick_size", "label": "Tick size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5},
]
PLOT_SETTINGS = {
    "figure.size": [3.8, 2.4], "axes.main.ylabel": "Outcome probability", "axes.main.y_range": [0, 0.0145],
    "series.ai.color": "#3B6FB6", "series.domain.color": "#D55E5E", "series.adjusted.color": "#202020",
    "series.bars.width": 0.34, "series.adjusted.marker_size": 3.6, "legend.visible": True,
    "typography.tick_size": 8,
}
_DATA = [{'outcome': 'NIH',
  'leader_class': 'AI',
  'specification': 'Raw',
  'estimate': 0.0019547042430427,
  'std_error': 8.750674110066331e-05,
  'ci_low': 0.0017831910304854,
  'ci_high': 0.0021262174556},
 {'outcome': 'NIH',
  'leader_class': 'Domain',
  'specification': 'Raw',
  'estimate': 0.006019341652681,
  'std_error': 0.000111477897818,
  'ci_low': 0.0058008449729577,
  'ci_high': 0.0062378383324044},
 {'outcome': 'NSF',
  'leader_class': 'AI',
  'specification': 'Raw',
  'estimate': 0.0115594457746202,
  'std_error': 0.0002117725374051,
  'ci_low': 0.0111443716013061,
  'ci_high': 0.0119745199479343},
 {'outcome': 'NSF',
  'leader_class': 'Domain',
  'specification': 'Raw',
  'estimate': 0.0132226117877735,
  'std_error': 0.0001646241421178,
  'ci_low': 0.0128999484692225,
  'ci_high': 0.0135452751063245},
 {'outcome': 'News',
  'leader_class': 'AI',
  'specification': 'Raw',
  'estimate': 0.0038230560898064,
  'std_error': 0.000122264234856,
  'ci_low': 0.0035834181894886,
  'ci_high': 0.0040626939901243},
 {'outcome': 'News',
  'leader_class': 'Domain',
  'specification': 'Raw',
  'estimate': 0.0080008640600854,
  'std_error': 0.0001283953806699,
  'ci_low': 0.0077492091139722,
  'ci_high': 0.0082525190061985},
 {'outcome': 'NIH',
  'leader_class': 'AI',
  'specification': 'Year + field adjusted',
  'estimate': 0.0025218310618156,
  'std_error': 0.0002858133255448,
  'ci_low': 0.0019616369437477,
  'ci_high': 0.0030820251798835},
 {'outcome': 'NIH',
  'leader_class': 'Domain',
  'specification': 'Year + field adjusted',
  'estimate': 0.0053827192477236,
  'std_error': 0.0001961912613184,
  'ci_low': 0.0049981843755393,
  'ci_high': 0.0057672541199078},
 {'outcome': 'NSF',
  'leader_class': 'AI',
  'specification': 'Year + field adjusted',
  'estimate': 0.0124028491330349,
  'std_error': 0.0004121398387927,
  'ci_low': 0.0115950550490012,
  'ci_high': 0.0132106432170686},
 {'outcome': 'NSF',
  'leader_class': 'Domain',
  'specification': 'Year + field adjusted',
  'estimate': 0.0127637574526752,
  'std_error': 0.0002769288698413,
  'ci_low': 0.0122209768677862,
  'ci_high': 0.0133065380375642},
 {'outcome': 'News',
  'leader_class': 'AI',
  'specification': 'Year + field adjusted',
  'estimate': 0.0043869044730029,
  'std_error': 0.00015860510102,
  'ci_low': 0.0040760384750036,
  'ci_high': 0.0046977704710021},
 {'outcome': 'News',
  'leader_class': 'Domain',
  'specification': 'Year + field adjusted',
  'estimate': 0.0074937136888475,
  'std_error': 0.0001381911536403,
  'ci_low': 0.0072228590277125,
  'ci_high': 0.0077645683499826}]


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


def prepare_data():
    return pd.DataFrame(_DATA)


def render(data, settings):
    cfg = _resolved(settings)
    outcomes = ["NIH", "NSF", "News"]
    x = np.arange(len(outcomes))
    width = cfg["series.bars.width"]
    centers = {"AI": x - width / 2, "Domain": x + width / 2}
    fig, ax = plt.subplots(figsize=cfg["figure.size"])
    for leader, color_path in [("AI", "series.ai.color"), ("Domain", "series.domain.color")]:
        raw = data.loc[(data["specification"].eq("Raw")) & (data["leader_class"].eq(leader))].set_index("outcome").loc[outcomes]
        ax.bar(centers[leader], raw["estimate"], width=width, color=cfg[color_path], edgecolor="none", zorder=1)
        adjusted = data.loc[(data["specification"].eq("Year + field adjusted")) & (data["leader_class"].eq(leader))].set_index("outcome").loc[outcomes]
        y = adjusted["estimate"].to_numpy()
        err = np.vstack([y - adjusted["ci_low"].to_numpy(), adjusted["ci_high"].to_numpy() - y])
        ax.errorbar(centers[leader], y, yerr=err, fmt="D", ms=cfg["series.adjusted.marker_size"],
                    lw=0.8, capsize=2, mfc="white", mec=cfg["series.adjusted.color"],
                    color=cfg["series.adjusted.color"], zorder=3)
    ax.set_xticks(x, outcomes)
    ax.set(ylabel=cfg["axes.main.ylabel"], ylim=cfg["axes.main.y_range"])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=1))
    if cfg["legend.visible"]:
        handles = [
            Patch(facecolor=cfg["series.ai.color"], edgecolor="none", label="AI-led (Raw)"),
            Patch(facecolor=cfg["series.domain.color"], edgecolor="none", label="Domain-led (Raw)"),
            Line2D([], [], marker="D", ls="none", ms=3.8, color=cfg["series.adjusted.color"],
                   markerfacecolor="white", label="Adjusted"),
        ]
        ax.legend(handles=handles, frameon=False, ncol=1, fontsize=6.7, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=cfg["typography.tick_size"], direction="out")
    ax.grid(False)
    fig.tight_layout()
    return fig

