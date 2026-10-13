"""Supplementary figure: absolute AI4Sci citation-audience composition."""

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd

PLOT_META = {
    "id": "fig-s7-bar-citation-audience-composition",
    "name": "Supplementary — Citation-audience composition",
    "description": "AI and Domain shares of citation events to AI4Sci by JCR quartile.",
    "version": 1, "data_mode": "inline",
    "data_note": "Final citation-event counts and normalized shares are embedded.",
    "data_export": {"csv": True, "json": True, "note": "Quartile-level counts and AI/Domain shares."},
}
PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 16, "step": 0.1, "required": True},
    {"path": "axes.main.xlabel", "label": "X label", "group": "Axes", "type": "string", "default": "JCR quartile"},
    {"path": "axes.main.ylabel", "label": "Y label", "group": "Axes", "type": "string", "default": "Citing-paper share"},
    {"path": "series.ai.color", "label": "AI citing color", "group": "Series", "type": "color", "default": "#3B6FB6"},
    {"path": "series.domain.color", "label": "Domain citing color", "group": "Series", "type": "color", "default": "#D55E5E"},
    {"path": "series.bars.width", "label": "Bar width", "group": "Series", "type": "number", "default": 0.34, "min": 0.05, "max": 0.9, "step": 0.01},
    {"path": "reference.majority.color", "label": "50% line color", "group": "Reference", "type": "color", "default": "#777777"},
    {"path": "legend.visible", "label": "Show legend", "group": "Legend", "type": "boolean", "default": True},
]
PLOT_SETTINGS = {
    "figure.size": [3.8, 2.4], "axes.main.xlabel": "JCR quartile", "axes.main.ylabel": "Citing-paper share",
    "series.ai.color": "#3B6FB6", "series.domain.color": "#D55E5E", "series.bars.width": 0.34,
    "reference.majority.color": "#777777", "legend.visible": True,
}
_DATA = [{'jcr': 'Q1',
  'AI': 1437466,
  'Domain': 2918674,
  'n_ai_domain': 4356140,
  'domain_share': 0.6700138195742102,
  'ai_share': 0.3299861804257898},
 {'jcr': 'Q2',
  'AI': 300718,
  'Domain': 662977,
  'n_ai_domain': 963695,
  'domain_share': 0.6879531387005224,
  'ai_share': 0.3120468612994775},
 {'jcr': 'Q3',
  'AI': 117156,
  'Domain': 238309,
  'n_ai_domain': 355465,
  'domain_share': 0.670414808771609,
  'ai_share': 0.329585191228391},
 {'jcr': 'Q4',
  'AI': 65634,
  'Domain': 105494,
  'n_ai_domain': 171128,
  'domain_share': 0.6164625309709691,
  'ai_share': 0.3835374690290309},
 {'jcr': 'Overall',
  'AI': 1920974,
  'Domain': 3925454,
  'n_ai_domain': 5846428,
  'domain_share': 0.6714277504144411,
  'ai_share': 0.3285722495855589}]


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


def prepare_data():
    return pd.DataFrame(_DATA)


def render(data, settings):
    cfg = _resolved(settings)
    order = ["Q1", "Q2", "Q3", "Q4", "Overall"]
    plot_data = data.set_index("jcr").loc[order]
    x = np.array([0, 1, 2, 3, 4.45])
    width = cfg["series.bars.width"]
    fig, ax = plt.subplots(figsize=cfg["figure.size"])
    ax.axhline(0.5, color=cfg["reference.majority.color"], lw=0.7, ls="--", zorder=0)
    ax.axvline(3.72, color="#C7C7C7", lw=0.6, zorder=0)
    ax.bar(x - width / 2, plot_data["ai_share"], width=width,
           color=cfg["series.ai.color"], label="AI citing papers")
    ax.bar(x + width / 2, plot_data["domain_share"], width=width,
           color=cfg["series.domain.color"], label="Domain citing papers")
    ax.set_xticks(x, order)
    ax.set(xlabel=cfg["axes.main.xlabel"], ylabel=cfg["axes.main.ylabel"],
           xlim=(-0.55, 4.95), ylim=(0, 0.8))
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    if cfg["legend.visible"]:
        ax.legend(frameon=False, fontsize=7.2, handlelength=1.8, labelspacing=0.3, borderaxespad=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(direction="out")
    ax.grid(False)
    fig.tight_layout()
    return fig

