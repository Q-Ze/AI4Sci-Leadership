"""Matplot Studio conversion of annual distinct-author counts."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd


PLOT_META = {
    "id": "line-author-absolute-counts",
    "name": "Annual distinct-author counts",
    "description": "EWMA-smoothed annual counts of AI and Domain Specialists on AI4Sci papers.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original result table is embedded; the upstream database query is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.45, 2.15], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Year", "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Distinct authors", "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2024], "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.top_spine", "label": "Show top spine", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.right_spine", "label": "Show right spine", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "series.ai.color", "label": "AI Specialist color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.domain.color", "label": "Domain Specialist color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.line_width", "label": "Line width", "group": "Series", "type": "number", "default": 1.3, "min": 0.1, "max": 8, "step": 0.05, "required": True},
    {"path": "legend.labels", "label": "Legend labels", "group": "Legend", "type": "string_list", "default": ["AI Specialist", "Domain Specialist"], "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 8, "min": 4, "max": 24, "step": 0.5, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [2.45, 2.15], "figure.facecolor": "#FFFFFF",
    "axes.x_label": "Year", "axes.y_label": "Distinct authors", "axes.x_range": [1995, 2024],
    "axes.grid": False, "axes.top_spine": False, "axes.right_spine": False,
    "axes.spine_width": 0.6, "series.ai.color": "#3B6FB6",
    "series.domain.color": "#D55E5E", "series.line_width": 1.3,
    "legend.labels": ["AI Specialist", "Domain Specialist"], "legend.font_size": 8,
    "typography.font_family": "Arial", "typography.axis_label_size": 9,
    "typography.tick_label_size": 8, "typography.tick_width": 0.6,
    "typography.tick_length": 3,
}

_CSV_GZIP_B64 = "H4sIAAAAAAAAA1WUOw5sRQxEc9bSarX/dohEwirQCwgIAIkEsXuO5/EdjUZ3+rbtclXZf/z45bfz7ffnu19//vLTLzz98OPvP3+Jv/5//fONzMRR8zpWkp+n+z7P9+1LjnLecWk56inX/vOJY13y9WIdLeXiSy4GWeI/H7KP+f9jN6iPadbx3OzVda3eP1/fqnb1349tzByztBNP+ujUXGCNWPRTuvDF6C1/f/UbfW8bijnRoxS0uZKeb16YA8HH+pq+6cpwU4mNESBXn7R98o7rbq+0nhopTtjopU3TkKf9tY5yXd5psAFE807q86Y9wJ907ZvTKlkWcLQhZJqQ0y2yQPxO0U5TuiVOEXdr9q1EttWG+NkUhyP3k2+TOjyMySiZQud2RpfL84jekDg9oBPdG6TP62YrPWz5gVO7UaU+/uzZbAgF9BW/pJjTtHAnuJ+W/sYp39G38EWmZufYRtURe4gpZVvvoQAdPViZNxDKa5q/4uHuUiP6wdec1wZ/iBKxJQJBl3AdM1BID6CfToqMf+geohDtrMIAUhWKgXQp79xEWeNXOQJzEbnKIpCkih0lN/1ZxEN+D8vIqABEYergpBKLvFqIyCOJWRkCIxbqK9B/sN5za3NQJPUR6cXDJURumG5PNECtTR2FXA/utSw1gnyKrBehIEaYvretbQX6z8PFJqzezgb0kwzaYErBahexovo1dz/VQCH0j2ETb0gvIrUc6B4QH6igWcXDjYHx/HoQn0EHklpiEAozBNeRhuYGQzPlWA3RmBY17IrrN+yzLYDiMsnza2M70CX84IFi5uHo3YqEePxgX+lf7O2G2x2kqgzLbUaGBF1MBXOX+W48XwOj3Yf+z6ZA5RwN2wzJ4JO5X4wEBvdBsZs5+YAtmhs1gBNeTqWTAd/WhW42DWKtxxMJ4lZNGRMEvUSxxUhYMAFdubsDMlhnTBbyFGLC4tSFXl5AkaxkO1iJOIiFxgwzV/3W27EV64+tGaK4goOUYvUxMecMN/tMhf7ZBlCDHWpH12GjcSiLrOqCImJ35mdkWEG9Q3UWE1VB1Gwxxgu54+3IkNeUVccJ5SB3w2AQstmcqSwaIOOL24XvmY9k0ldHSyjhhPaDuf4TAl9BEkkGAAA="


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
    labels = s["legend.labels"]
    for column, color, label in [("AI_ewma5", s["series.ai.color"], labels[0]),
                                  ("Domain_ewma5", s["series.domain.color"], labels[1])]:
        ax.plot(data["year"], data[column], color=color, lw=s["series.line_width"], label=label)
    ax.set_xlabel(s["axes.x_label"])
    ax.set_ylabel(s["axes.y_label"])
    ax.set_xlim(s["axes.x_range"])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x / 1000:.0f}k" if x >= 1000 else f"{x:.0f}"))
    ax.legend(frameon=False, fontsize=s["legend.font_size"])
    ax.xaxis.label.set_size(s["typography.axis_label_size"])
    ax.yaxis.label.set_size(s["typography.axis_label_size"])
    ax.tick_params(labelsize=s["typography.tick_label_size"], direction="out",
                   width=s["typography.tick_width"], length=s["typography.tick_length"])
    ax.spines["top"].set_visible(s["axes.top_spine"])
    ax.spines["right"].set_visible(s["axes.right_spine"])
    for spine in ax.spines.values():
        spine.set_linewidth(s["axes.spine_width"])
    ax.grid(s["axes.grid"])
    for item in [ax.xaxis.label, ax.yaxis.label, *ax.get_xticklabels(), *ax.get_yticklabels(), *ax.get_legend().get_texts()]:
        item.set_fontfamily(s["typography.font_family"])
    fig.tight_layout()
    return fig
