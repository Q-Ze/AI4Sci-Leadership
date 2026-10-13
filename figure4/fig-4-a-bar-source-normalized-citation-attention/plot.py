"""Manuscript Figure 4A: source-normalized citation attention by JCR quartile."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PLOT_META = {
    "id": "fig-4-a-bar-source-normalized-citation-attention",
    "name": "Figure 4A — Per-paper citing rates",
    "description": "AI and Domain per-paper citing rates toward AI4Sci, by JCR quartile.",
    "version": 1, "data_mode": "inline",
    "data_note": "Final pooled edge and source-paper counts are embedded.",
    "data_export": {"csv": True, "json": True, "note": "Quartile/source counts and per-paper rates, including Overall."},
}
PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 16, "step": 0.1, "required": True},
    {"path": "axes.main.xlabel", "label": "X label", "group": "Axes", "type": "string", "default": "JCR quartile"},
    {"path": "axes.main.ylabel", "label": "Y label", "group": "Axes", "type": "string", "default": "Per-paper citing rate"},
    {"path": "series.ai.color", "label": "AI papers color", "group": "Series", "type": "color", "default": "#3B6FB6"},
    {"path": "series.domain.color", "label": "Domain papers color", "group": "Series", "type": "color", "default": "#D55E5E"},
    {"path": "series.bars.width", "label": "Bar width", "group": "Series", "type": "number", "default": 0.34, "min": 0.05, "max": 0.9, "step": 0.01},
    {"path": "legend.visible", "label": "Show legend", "group": "Legend", "type": "boolean", "default": True},
    {"path": "typography.label_size", "label": "Label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5},
    {"path": "typography.tick_size", "label": "Tick size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5},
]
PLOT_SETTINGS = {
    "figure.size": [3.8, 2.4], "axes.main.xlabel": "JCR quartile", "axes.main.ylabel": "Per-paper citing rate",
    "series.ai.color": "#3B6FB6", "series.domain.color": "#D55E5E", "series.bars.width": 0.34,
    "legend.visible": True, "typography.label_size": 9, "typography.tick_size": 8,
}
_DATA = [{'jcr': 'Q1',
  'source_type': 'AI',
  'n_edges': 1376180,
  'n_source_papers': 3600564,
  'per_paper_citing_rate': 0.382212342288597},
 {'jcr': 'Q1',
  'source_type': 'Domain',
  'n_edges': 2850174,
  'n_source_papers': 56530762,
  'per_paper_citing_rate': 0.0504181068707334},
 {'jcr': 'Q2',
  'source_type': 'AI',
  'n_edges': 281405,
  'n_source_papers': 3600564,
  'per_paper_citing_rate': 0.0781558111451428},
 {'jcr': 'Q2',
  'source_type': 'Domain',
  'n_edges': 639579,
  'n_source_papers': 56530762,
  'per_paper_citing_rate': 0.0113138223751521},
 {'jcr': 'Q3',
  'source_type': 'AI',
  'n_edges': 112189,
  'n_source_papers': 3600564,
  'per_paper_citing_rate': 0.0311587295768107},
 {'jcr': 'Q3',
  'source_type': 'Domain',
  'n_edges': 231693,
  'n_source_papers': 56530762,
  'per_paper_citing_rate': 0.0040985295758086},
 {'jcr': 'Q4',
  'source_type': 'AI',
  'n_edges': 63701,
  'n_source_papers': 3600564,
  'per_paper_citing_rate': 0.0176919504833131},
 {'jcr': 'Q4',
  'source_type': 'Domain',
  'n_edges': 103317,
  'n_source_papers': 56530762,
  'per_paper_citing_rate': 0.001827624400322},
 {'jcr': 'Overall',
  'source_type': 'AI',
  'n_edges': 1833475,
  'n_source_papers': 3600564,
  'per_paper_citing_rate': 0.5092188334938638},
 {'jcr': 'Overall',
  'source_type': 'Domain',
  'n_edges': 3824763,
  'n_source_papers': 56530762,
  'per_paper_citing_rate': 0.0676580832220163}]


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


def prepare_data():
    return pd.DataFrame(_DATA)


def render(data, settings):
    cfg = _resolved(settings)
    order = ["Q1", "Q2", "Q3", "Q4"]
    wide = data.loc[data["jcr"].isin(order)].pivot(index="jcr", columns="source_type",
                                                   values="per_paper_citing_rate").reindex(order)
    x = np.arange(len(order))
    width = cfg["series.bars.width"]
    fig, ax = plt.subplots(figsize=cfg["figure.size"])
    ax.bar(x - width / 2, wide["AI"], width=width, color=cfg["series.ai.color"], label="AI papers")
    ax.bar(x + width / 2, wide["Domain"], width=width, color=cfg["series.domain.color"], label="Domain papers")
    ax.set_xticks(x, order)
    ax.set(xlabel=cfg["axes.main.xlabel"], ylabel=cfg["axes.main.ylabel"], xlim=(-0.55, 3.55), ylim=(0, None))
    if cfg["legend.visible"]:
        ax.legend(frameon=False, fontsize=7.2, handlelength=1.8, labelspacing=0.3, borderaxespad=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=cfg["typography.tick_size"], direction="out")
    ax.xaxis.label.set_size(cfg["typography.label_size"])
    ax.yaxis.label.set_size(cfg["typography.label_size"])
    ax.grid(False)
    fig.tight_layout()
    return fig

