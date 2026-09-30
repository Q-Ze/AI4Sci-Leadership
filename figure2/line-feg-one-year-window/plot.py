"""Matplot Studio conversion of the fixed-window F/E/G figure."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import pandas as pd


PLOT_META = {
    "id": "line-feg-one-year-window",
    "name": "F/E/G indices: 1-year window",
    "description": "EWMA-smoothed Foundation, Extension, and Generalization indices using a 1-year forward-citation window.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original result table is embedded; the upstream database query is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.75, 2.4], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "AI4Sci publication year", "required": True},
    {"path": "axes.f_y_label", "label": "Left-axis label", "group": "Axes", "type": "string", "default": "Foundation index", "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1995, 2023], "required": True},
    {"path": "axes.relative_padding", "label": "Relative Y padding", "group": "Axes", "type": "number", "default": 0.08, "min": 0, "max": 0.5, "step": 0.01, "required": True},
    {"path": "axes.minimum_padding", "label": "Minimum Y padding", "group": "Axes", "type": "number", "default": 0.005, "min": 0, "max": 0.2, "step": 0.001, "required": True},
    {"path": "axes.x_tick_interval", "label": "X tick interval", "group": "Axes", "type": "number", "default": 10, "min": 1, "max": 30, "step": 1, "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "series.foundation.color", "label": "Foundation color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.extension.color", "label": "Extension color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.generalization.color", "label": "Generalization color", "group": "Series", "type": "color", "default": "#009E73", "required": True},
    {"path": "series.line_width", "label": "Line width", "group": "Series", "type": "number", "default": 1.3, "min": 0.1, "max": 8, "step": 0.05, "required": True},
    {"path": "annotation.labels", "label": "Curve labels", "group": "Annotations", "type": "string_list", "default": ["Foundation", "Extension", "Generalization"], "required": True},
    {"path": "annotation.foundation_year", "label": "Foundation label year", "group": "Annotations", "type": "integer", "default": 2008, "min": 1995, "max": 2023, "required": True},
    {"path": "annotation.extension_year", "label": "Extension label year", "group": "Annotations", "type": "integer", "default": 2010, "min": 1995, "max": 2023, "required": True},
    {"path": "annotation.generalization_year", "label": "Generalization label year", "group": "Annotations", "type": "integer", "default": 1998, "min": 1995, "max": 2023, "required": True},
    {"path": "annotation.offset", "label": "Label offset", "group": "Annotations", "type": "number_pair", "default": [4, 5], "min": -30, "max": 30, "step": 1, "required": True},
    {"path": "annotation.font_size", "label": "Label font size", "group": "Annotations", "type": "number", "default": 7.2, "min": 4, "max": 24, "step": 0.1, "required": True},
    {"path": "annotation.background", "label": "Label background", "group": "Annotations", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "annotation.background_alpha", "label": "Label background opacity", "group": "Annotations", "type": "number", "default": 0.78, "min": 0, "max": 1, "step": 0.01, "required": True},
    {"path": "annotation.background_pad", "label": "Label background padding", "group": "Annotations", "type": "number", "default": 0.5, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "header.text", "label": "Header text", "group": "Annotations", "type": "string", "default": "1-year forward-citation window", "required": True},
    {"path": "header.position", "label": "Header position", "group": "Annotations", "type": "number_pair", "default": [0.5, 1.02], "min": -1, "max": 2, "step": 0.01, "required": True},
    {"path": "header.font_size", "label": "Header font size", "group": "Annotations", "type": "number", "default": 8, "min": 4, "max": 24, "step": 0.5, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [2.75, 2.4], "figure.facecolor": "#FFFFFF",
    "axes.x_label": "AI4Sci publication year", "axes.f_y_label": "Foundation index",
    "axes.x_range": [1995, 2023], "axes.relative_padding": 0.08,
    "axes.minimum_padding": 0.005, "axes.x_tick_interval": 10,
    "axes.grid": False, "axes.spine_width": 0.6,
    "series.foundation.color": "#D55E5E", "series.extension.color": "#3B6FB6",
    "series.generalization.color": "#009E73", "series.line_width": 1.3,
    "annotation.labels": ["Foundation", "Extension", "Generalization"],
    "annotation.foundation_year": 2008, "annotation.extension_year": 2010,
    "annotation.generalization_year": 1998, "annotation.offset": [4, 5],
    "annotation.font_size": 7.2, "annotation.background": "#FFFFFF",
    "annotation.background_alpha": 0.78, "annotation.background_pad": 0.5,
    "header.text": "1-year forward-citation window", "header.position": [0.5, 1.02],
    "header.font_size": 8, "typography.font_family": "Arial",
    "typography.axis_label_size": 9, "typography.tick_label_size": 8,
    "typography.tick_width": 0.6, "typography.tick_length": 3,
}

_CSV_GZIP_B64 = "H4sIAAAAAAAAA52Y7Y5eNQyE//dajlZxvmxfAPQyUEELWgkKKpUQd88zTrbwG1Xbd0/ek8SxZ8aT/fv105fn++e75+Pz+Yc/Pv3x+uVPfvnp7eunr2+/f9bvX15/fv3y+vmnVz28/vr2y9uPb7++ff37Py99/8PrX799Ws939/Pj+fxgmetpL232OYaNHG7Zms3JoDPUt0Wfc7VwZ6gbL7btYTGadXtyxTP3Xi/t6dNX5/M+/v9FFdSu+b7W9mwjxtiWpukr27Kxg/HBWgxZjpEWszHQ94jHGq+uPkxBeVuK5j5q0WnTWh9EN8JPSKFtzCwylI3evKe1vXy7775DEXlNzpjLrUXjXD38zo5gZ/fsXoH3ZmsTep/miz38MaY8K+ZWSNHMFdJ51KqbYBZB9Bytr31X5Wcmqdsrs1ZdI/h27mVt+B6KKmr+MOtEuBnlX5wFnI1m60GgpKUWyN202JrZksQ81inhXsEaz1BF+LyPWna1vZuiCmfiuLkyKrhdR7M1a1nViFz1oACzypfnWJzKZze+T8pV85elB+8TLIebN1uEtL3tWG1SPzZ8CK+iWqMrWfexomKJTmY6cMlbwGSXmBZ7m287yWoqy+hm1GysD721Mx8ojcX/y0eesvqYjQ1GxmbWqlx1ALPS9nRfc/p4QE0+0fpUVLtF8nkfC1UBAocLqcnMimoCMhJFPtixSggMKJUK4eZmU1HZAVZL0A9qFHlTWX0HwUMNEjzIuqAefWfjhzQvskVQHCBbFO84weDzPlYBOilIDjdskuHKf+8+9uCUivignYr68gaLQEV3BdU1f+301cx8CGDM0QIAKlx4ndts9cNfKp8QA+KAgAeQ5qOiHpin6/P9+bAI7u8NtaYYdpIF/tyN4/eccUqYqhb4iQ6yq4TjQEAgJ6m2gcc5F8Xrqew0Qm7rhAVIONVGNLajT2ZK2FLJUKASq/dnrQofSYVJKi4HO8eReiFhB/4dydqk3wbiEy0U0jxSJXyQyERexrITk09IzocLmUfqQFmSOHCSIfoCPSSB9aLwBAxe/n2uqBpZ5ZSoxrJTMTBVcpqD6kCngyzSTGlsp0C8FdlRdlCMcNiSFMUV0Y0ksO6QmpQsaxkUKAMy74WCg/GunEFVYWpR4aPx+c5DQBVZIOLQYLQC2yI2eAVmcU4sDYEFOseAuIWuo+4IK0iiYALNgbyUbTDBOtg/B2vEwZopHK/otBv4/6gyhSoo0Y/Qn4E6MZwFGCAPPbEj0nwdgHyTp9GubFF7J20IIkcuLh6RJ9vLg8gaKCk5EReZuwwxtaNkxsl5iTOQMdI/HlBPPXlrF9yZbaUVZ6BEItHiMLUpbVsnVrRBIkBfXNxTdKGZ3KaROQV2dL5JqDo4X8rZmZ97jok+S+7mkT52RsRpYKCMuAmMrgh9Wz88BBAlrWegTjzpSZyiq8223Bcke5M+cIGynoURgpBkUXJrVcpS+hHLIL0yxhertMqhyTABHkJ1twJZ74IemJOM9P0ASn+Gt2o55s1Lut4HFJlxUJpYC/WSg96toxKvmvi6FkAIgcmBBJDKTmRW89k8Bq+i19S/e9EHuEESemNlbt/ItE1C007F/Nlk6aGxbvEQ2vchmXgf0Mo0U9rYgvbq/RUYvQmBZU2QXtJoIg5UT4q+6I4SDCvBB0eIWrrcEF/PE1dsWksv/9BPxmA4VEXKaVd0xTHWI2MgoSetSKgk9g5oWbqKpJBTuAxWhYV8sByn7khDnmWXuK6CynsoqlJ8lif0aqQyIH2fY80F6rFLUzksJChEuiWdFyVBLQMD8NAoS0w7Ut9K++9AFSJl64ANR4nyI6QeI0duxb9eVoZCuigNx4JOuStf48zXsegcSANyevr+VnumP+2EBtXKTS/MDYPxcwB3PtLvBwJ0kRDXFqNczh2olSVbgN0xoaNEUwsjI0SCmqKHVyBlM+Arrzbpa8FclCC/2TbNSIk7CA2pqHUJ/9q3mVFK3BNhkbNH2QdkqJrCmoPHl38HtC70R2E4EApHjudFGJ2LrejAhHxIiZ2jl45pKr5IWfYDhE1yJbdM6j3jBoacbqk5YrSue6PzdtkK0lb2eWR/XN2huIgFlY69D1RorTJMEBD8cBIcE2gCmRbX1vErlrhcBEZKce0zG56pG8m0wpjT0QbFQjiG/EAeA4akyBXhlmgJQ1LPwmSx9F7mysru3IFamfICMZkBFo4rY4g/qtTlYuapRYokdMpAIZENhVbKzz60UFhN325FYNd9AV9VHrYfv0RfwSXRY2QQcEqsRauyqfuOQA8gVpa3uCMVGpvxROsOUf96lgF8cA4tENBjO3W7INNgTXsOhRaH2C6k8pUxUiwG9fQkDAqnACEl0XRu3IdSvNQDH1llIkHuomz0FLVe/jNSBEAcCULmG+4f70KoQaOjR7TRCjydcE1xZuICIIFiO/KP4tI5sPg0IyUSDWZV0kArke/TbHr7RNkgFIo5sBZkGpehTa0a+RAUqy/doSoIxwFreGN7lzP5Z5wtmSBbJzJ1nxSiKTtd4IP06QS21N3l5MlmJZL7j+uagIMEOWVRuHMBX/AEV2g3BubpQPgMhHtVx9Qqkv1vQxVawCJK34IYZ7monXJFbMhetJxTkaCYWCKKCXmbKtrtCocuk9Pl8WikyhJdDN1Bk7laxa6rwRDUsEykjym68EgYsEEp4S2zyIvVyb8NVVHRehyF6y5Lqmp14CJLz3GkmAU4ZNbpBikvtErW+ukEkJegyOto6kuaDvBStgqfxCVHpcckijSAFXaQQ3oAt3E4wO3gONmpa4Jy923oSC7nDHUz+cfyYzog1oOmRh1GNWrsA7oFOhH0dbp6H5dNi7TAQ4JD9hhDZUAUro+0gQelfogfXJPo3WRf1yVCQTThIeSvPhX6o4F0932oggMGLIET4qZYisFNnj3Blpq4LAuLq0FIyVpdhMjcP393HXWoEQAA"


def _typed_rows(csv_text):
    rows = list(csv.DictReader(StringIO(csv_text)))
    for row in rows:
        for key, value in row.items():
            try:
                row[key] = float(value) if "." in value else int(value)
            except ValueError:
                pass
    return rows


def prepare_data():
    return pd.DataFrame(_typed_rows(decompress(b64decode(_CSV_GZIP_B64)).decode("utf-8")))


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


def _padded_limits(values, relative_padding, minimum_padding):
    low, high = float(values.min()), float(values.max())
    padding = max((high - low) * relative_padding, minimum_padding)
    return max(0, low - padding), min(1, high + padding)


def render(data, settings):
    s = _resolved(settings)
    fig, ax_f = plt.subplots(figsize=s["figure.size"], facecolor=s["figure.facecolor"])
    ax_eg = ax_f.twinx()
    ax_f.plot(data["year"], data["F_ewma5"], color=s["series.foundation.color"],
              lw=s["series.line_width"])
    ax_eg.plot(data["year"], data["E_ewma5"], color=s["series.extension.color"],
               lw=s["series.line_width"])
    ax_eg.plot(data["year"], data["G_ewma5"], color=s["series.generalization.color"],
               lw=s["series.line_width"])
    ax_f.set(xlabel=s["axes.x_label"], ylabel=s["axes.f_y_label"], xlim=s["axes.x_range"],
             ylim=_padded_limits(data["F_ewma5"], s["axes.relative_padding"], s["axes.minimum_padding"]))
    ax_eg.set_ylim(_padded_limits(pd.concat([data["E_ewma5"], data["G_ewma5"]]),
                                  s["axes.relative_padding"], s["axes.minimum_padding"]))
    ax_f.xaxis.set_major_locator(MultipleLocator(s["axes.x_tick_interval"]))
    labels = s["annotation.labels"]
    annotations = [
        (ax_f, "F", s["annotation.foundation_year"], labels[0], s["series.foundation.color"]),
        (ax_eg, "E", s["annotation.extension_year"], labels[1], s["series.extension.color"]),
        (ax_eg, "G", s["annotation.generalization_year"], labels[2], s["series.generalization.color"]),
    ]
    text_items = []
    for axis, key, year, label, color in annotations:
        row = data.loc[data["year"].eq(year)].iloc[0]
        text_items.append(axis.annotate(
            label, xy=(year, row[f"{key}_ewma5"]), xytext=s["annotation.offset"],
            textcoords="offset points", color=color, fontsize=s["annotation.font_size"],
            bbox={"facecolor": s["annotation.background"], "edgecolor": "none",
                  "alpha": s["annotation.background_alpha"], "pad": s["annotation.background_pad"]}))
    header = ax_f.text(*s["header.position"], s["header.text"], transform=ax_f.transAxes,
                       ha="center", va="bottom", fontsize=s["header.font_size"])
    ax_f.xaxis.label.set_size(s["typography.axis_label_size"])
    ax_f.yaxis.label.set_size(s["typography.axis_label_size"])
    ax_eg.yaxis.label.set_size(s["typography.axis_label_size"])
    for axis in (ax_f, ax_eg):
        axis.tick_params(labelsize=s["typography.tick_label_size"], direction="out",
                         width=s["typography.tick_width"], length=s["typography.tick_length"])
        for spine in axis.spines.values():
            spine.set_linewidth(s["axes.spine_width"])
        axis.grid(s["axes.grid"])
    ax_f.spines["top"].set_visible(False)
    ax_f.spines["right"].set_visible(False)
    ax_eg.spines["top"].set_visible(False)
    ax_eg.spines["left"].set_visible(False)
    ax_eg.spines["bottom"].set_visible(False)
    font_items = [ax_f.xaxis.label, ax_f.yaxis.label, *ax_f.get_xticklabels(),
                  *ax_f.get_yticklabels(), *ax_eg.get_yticklabels(), header, *text_items]
    for item in font_items:
        item.set_fontfamily(s["typography.font_family"])
    fig.tight_layout()
    return fig
