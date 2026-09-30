"""Matplot Studio conversion of transition-inflow composition."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "area-role-transition-inflow-composition",
    "name": "Role-transition inflow composition",
    "description": "EWMA-smoothed source-role composition of transitions into the AI4Sci-active role.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original result table is embedded; the upstream database query is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.45, 2.15], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Year", "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "AI4Sci-active inflows share", "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1996, 2024], "required": True},
    {"path": "axes.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0, 1], "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.top_spine", "label": "Show top spine", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.right_spine", "label": "Show right spine", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "series.ai.color", "label": "AI-source color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.domain.color", "label": "Domain-source color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.alpha", "label": "Area opacity", "group": "Series", "type": "number", "default": 0.88, "min": 0, "max": 1, "step": 0.01, "required": True},
    {"path": "series.line_width", "label": "Edge width", "group": "Series", "type": "number", "default": 0, "min": 0, "max": 5, "step": 0.05, "required": True},
    {"path": "legend.labels", "label": "Legend labels", "group": "Legend", "type": "string_list", "default": ["AI-active source", "Domain-active source"], "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "options": ["upper left", "upper right", "lower left", "lower right", "best"], "default": "upper left", "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.2, "min": 4, "max": 24, "step": 0.1, "required": True},
    {"path": "legend.facecolor", "label": "Legend background", "group": "Legend", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "legend.frame_alpha", "label": "Legend opacity", "group": "Legend", "type": "number", "default": 0.88, "min": 0, "max": 1, "step": 0.01, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [2.45, 2.15], "figure.facecolor": "#FFFFFF",
    "axes.x_label": "Year", "axes.y_label": "AI4Sci-active inflows share",
    "axes.x_range": [1996, 2024], "axes.y_range": [0, 1], "axes.grid": False,
    "axes.top_spine": False, "axes.right_spine": False, "axes.spine_width": 0.6,
    "series.ai.color": "#3B6FB6", "series.domain.color": "#D55E5E",
    "series.alpha": 0.88, "series.line_width": 0,
    "legend.labels": ["AI-active source", "Domain-active source"],
    "legend.location": "upper left", "legend.font_size": 7.2,
    "legend.facecolor": "#FFFFFF", "legend.frame_alpha": 0.88,
    "typography.font_family": "Arial", "typography.axis_label_size": 9,
    "typography.tick_label_size": 8, "typography.tick_width": 0.6,
    "typography.tick_length": 3,
}

_CSV_GZIP_B64 = "H4sIAAAAAAAAA42W7YqfRQzFv/daBpkkM3m5mmXRioW2C60i3r2/5FkRxQ9Cof99JpPXc07mj4+v39bXl5+/vX15ef3016+f3r68fvrKX7++/fr6+eXT158/v/2+Xj+9fH/77duPH1++//L67eN6rP757V82Lx9///J6/8vyOfkgVb7M9rq6V9699g+WqXa1jkj4iR188/ffd87s/1m181g3fXnUEvWLzXFT7mwPKfNwPl3+50qZ5u7TthJTCzXxK/datVVireFpJ89xbe+5Iu8qiyWh2vcuZldDyzAyb1/34O2ExnZ8eSd/NHBxI+OEJKZtFkqko6JXU3yyr5VkKLr30j25cl5+TaKkdlyZ/CO3HU/duUtPjdl1qVOS+5yUMTqW++6UuldKP+B0L9nSnYlYqjX+sZJrxsE+tLdbRtKSxz0r655u9KExeSKwLJy2DX2Rq4odLu+4F9wb6R87SxnL9LUOzis7FzxOX+fXFp8zfdrje5cYJTHMem+PVe10Smfo1gEU30n+RVJGtyczAxVhN6x6fNMfd1ChftRp4jT7UJmkZESZMOSYCJtWpahuTxLsCLbE6EGnQYT9lLD/Rh2wmRLqL9D10VMCfqnpNNYqngpwS+W3sYaP9n9I3mzppe5GxFSgpVSg5ppMe1JzAE4F4RYSOf6dQW3dpEdyDwyMOVWU70OL/MNk3ShfCijXocd9cwNxsG6bhMptUisYACW8yHvbjFjAOxA4gJZsZ8YJK0DABbDUNAG8c69F4bocgD83gWbEJonMa+9XgSYYIyWR8x4gTl0GHc2Kdyu9+zBnbfJEB2CydmUx8VrYzwQOw4VlSX6F8UCU2UIyIb/98CS18p6iJd32p0ESW87ddI7pSLvPBS/pjcteAYJbWbwiydfdtoq0++cXCvF+Nm3M6FjpCmHrCVBQlZTEAmLvCVCLSdm6nKyIR7rIHnYF3q4MXZ3k4ZYS8iQNGn1jnoiYU+X2ce/C1B0Bo8qyfXBP1qaIQLN74aGdGXAkLTzR8Yx25oCWrAjHYGRyAIzUtjEgVabcVmA2kRC6SEnntn9ZtkPXpc+r9pMZw4dYhGSCXUdfBSNpqFePMOtpIzqJKAk4ywydNqKmaBeMpp3DAMhirSkOYFouRn3hcutJnp4oyJrkrrfqyO3BIz1TKA2FlBCPpIcDcJzEq6AntQ0HKBdKotRwtKW0ciKIIspoPIpfETYRMuAJIg9ltk6XCH5QBUS0+OdTKsEv6oGMbv5NiLNwdVfvEASjo3GXJpa2vEBRgDt3afaOlhc4ep9mchHKHjqRXd4kgrbA7Fv0N0/DiO/NiFWtyMDL5i5cdapFUkBjTQ1QuP+S/i4TExCVonraCzAsJw/iNdpZQCTgrdYNomYbPO11dqm3Lwty4QgRku2UMTESuTCECD0BhTNrBMZ6YwgNkTNXWbCwBSwkjADMHYNtzCJgChmU0VKLYePFglza6R4+NKxcSblj19Modie60BhtVZ1hs2JJuaHcqjp4TZBEs1jHvCW0ZWIi7N4WxfC1MTgREEoQAUyQzQnawgePGWofnp4hvOslQC/axR3GsZPBG75ZY02+eRz0Prcedq8VWtoRWOfes+6t8mwYlgNNChYiIHbWbpttBliaSGDLGhG01zLqvBCw3IsrOUU0AWA2wnvS5jEQzZO2BUPiQx0mdRBupLcSoT5TKpJivQyAEYzsENIwZXedjSYv7GTy4zR7CXQ+ubsDKBZMJZtOm2dDW3n1wBAiBEDnU9jugSFX8B/h7xAsZ3rU0sobgVcYataXhXcBosCLBdkfLiIHxS0gRgkkNIkwG6DSEEZ+4k4mjBCpAukEjZ4FHAXU0t4Z7GLwgzxWM7jhsVC9JYe0rGbQhRrv3pJPJszTEDJq034YTIw4LKQEt5Ac2naM09O4l+22UW8AOn2RfnJKo47HE5rZcZM9ABGAP4/B2Rs84foJCaZ4ByBUXVsi50AEUPEQoJMf/gRPtudvgwsAAA=="


def prepare_data():
    return pd.DataFrame(_typed_rows(decompress(b64decode(_CSV_GZIP_B64)).decode("utf-8")))


def _typed_rows(csv_text):
    rows = list(csv.DictReader(StringIO(csv_text)))
    for row in rows:
        for key, value in row.items():
            try:
                row[key] = float(value) if "." in value else int(value)
            except ValueError:
                pass
    return rows


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


def render(data, settings):
    s = _resolved(settings)
    fig, ax = plt.subplots(figsize=s["figure.size"], facecolor=s["figure.facecolor"])
    ax.stackplot(data["year"], data["ai_source_share_ewma5"], data["domain_source_share_ewma5"],
                 labels=s["legend.labels"], colors=[s["series.ai.color"], s["series.domain.color"]],
                 alpha=s["series.alpha"], linewidth=s["series.line_width"])
    ax.set(xlabel=s["axes.x_label"], ylabel=s["axes.y_label"],
           xlim=s["axes.x_range"], ylim=s["axes.y_range"])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    legend = ax.legend(frameon=True, facecolor=s["legend.facecolor"], edgecolor="none",
                       framealpha=s["legend.frame_alpha"], fontsize=s["legend.font_size"],
                       loc=s["legend.location"])
    ax.xaxis.label.set_size(s["typography.axis_label_size"])
    ax.yaxis.label.set_size(s["typography.axis_label_size"])
    ax.tick_params(labelsize=s["typography.tick_label_size"], direction="out",
                   width=s["typography.tick_width"], length=s["typography.tick_length"])
    ax.spines["top"].set_visible(s["axes.top_spine"])
    ax.spines["right"].set_visible(s["axes.right_spine"])
    for spine in ax.spines.values():
        spine.set_linewidth(s["axes.spine_width"])
    ax.grid(s["axes.grid"])
    for item in [ax.xaxis.label, ax.yaxis.label, *ax.get_xticklabels(), *ax.get_yticklabels(), *legend.get_texts()]:
        item.set_fontfamily(s["typography.font_family"])
    fig.tight_layout()
    return fig
