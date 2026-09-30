"""Matplot Studio conversion of a career-age ECDF."""

from base64 import b64decode
import csv
from gzip import decompress
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "ecdf-career-age-first-ai4sci",
    "name": "Career age at first AI4Sci paper",
    "description": "ECDF of career age when authors first appear on an AI4Sci paper, by Specialist class.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The original aggregated ECDF table is embedded; the upstream database query is not rerun.",
    "data_export": {"csv": True, "json": True, "note": "Embedded tabular research result."},
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Figure background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Career age at first AI4Sci paper (years)", "required": True},
    {"path": "axes.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Cumulative share", "required": True},
    {"path": "axes.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [0, 50], "required": True},
    {"path": "axes.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0, 1], "required": True},
    {"path": "axes.grid", "label": "Show grid", "group": "Axes", "type": "boolean", "default": False, "required": True},
    {"path": "axes.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "format.percent_decimals", "label": "Percent decimals", "group": "Axes", "type": "integer", "default": 0, "min": 0, "max": 3, "required": True},
    {"path": "series.ai.color", "label": "AI Specialist color", "group": "Series", "type": "color", "default": "#3B6FB6", "required": True},
    {"path": "series.domain.color", "label": "Domain Specialist color", "group": "Series", "type": "color", "default": "#D55E5E", "required": True},
    {"path": "series.line_width", "label": "Line width", "group": "Series", "type": "number", "default": 1.3, "min": 0.1, "max": 8, "step": 0.05, "required": True},
    {"path": "series.step_where", "label": "Step alignment", "group": "Series", "type": "select", "options": ["pre", "post", "mid"], "default": "post", "required": True},
    {"path": "legend.labels", "label": "Legend labels", "group": "Legend", "type": "string_list", "default": ["AI Specialist", "Domain Specialist"], "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "options": ["lower right", "lower left", "upper right", "upper left", "best"], "default": "lower right", "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.2, "min": 4, "max": 24, "step": 0.1, "required": True},
    {"path": "legend.handle_length", "label": "Legend handle length", "group": "Legend", "type": "number", "default": 1.8, "min": 0, "max": 8, "step": 0.1, "required": True},
    {"path": "legend.label_spacing", "label": "Legend label spacing", "group": "Legend", "type": "number", "default": 0.3, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "legend.border_axes_pad", "label": "Legend axes padding", "group": "Legend", "type": "number", "default": 0.2, "min": 0, "max": 3, "step": 0.05, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.axis_label_size", "label": "Axis label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_label_size", "label": "Tick label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5, "required": True},
    {"path": "typography.tick_width", "label": "Tick width", "group": "Typography", "type": "number", "default": 0.6, "min": 0, "max": 5, "step": 0.1, "required": True},
    {"path": "typography.tick_length", "label": "Tick length", "group": "Typography", "type": "number", "default": 3, "min": 0, "max": 12, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [3.8, 2.4], "figure.facecolor": "#FFFFFF",
    "axes.x_label": "Career age at first AI4Sci paper (years)", "axes.y_label": "Cumulative share",
    "axes.x_range": [0, 50], "axes.y_range": [0, 1], "axes.grid": False,
    "axes.spine_width": 0.6, "format.percent_decimals": 0,
    "series.ai.color": "#3B6FB6", "series.domain.color": "#D55E5E",
    "series.line_width": 1.3, "series.step_where": "post",
    "legend.labels": ["AI Specialist", "Domain Specialist"], "legend.location": "lower right",
    "legend.font_size": 7.2, "legend.handle_length": 1.8,
    "legend.label_spacing": 0.3, "legend.border_axes_pad": 0.2,
    "typography.font_family": "Arial", "typography.axis_label_size": 9,
    "typography.tick_label_size": 8, "typography.tick_width": 0.6,
    "typography.tick_length": 3,
}

_CSV_GZIP_B64 = "H4sIAAAAAAAAA2WY3c4mNQ6Ez7mWFortJHYOV9qTvQo0YtkfiQUJhvvfx93fl3ZmhARo3poktsvlcn/56+t/fv/jp59//fLnn9fPX/745Zc/fvry71+u366vv3/98uv18z//9cPf/nG1S0Y0jcvGDImr/di7Roj27vz5UEmU8POa9oJGtzmXqUzpq98YvXTO6C9mSvSho/duvYvPBNkls00voGk9RJp2aT50JahfYr2tF+RN2mw9+pQZwBI0LhEABWS8e6qZiYeO+6R5LfdRMJNQRYY4fyThifErZmjB5DUcZeGLV9+XxcWRJUfR5hiitlrz1lokZl0uq2J0OghyaWuK3BhpFwGXPJIhE9M1l/el0W+QXFNnK6CpMZxMrrFI1XOSXmPW8MPDW3SyoK79yZHY1deqJy2larLMdTV5ciT9okQlSasNGW1oJ/z+xC/j6s1LkpZwuSZqdPf1PInX+ChlW+ptuYZPQovxnETtrWZg2ezG/8IQNf65QXHxvnoSD1zN16IkfTW7QeviiSUDi2cHNKX2Mvw5SdulElFB7uKrN7XokOwGCTeOkibOWE3vCKdYu5mrSoDiFeQQ2zxMSJjcb1L4bVZz6SI+PPLV3HdjoPf5JO+ZyLaWxZrtTpNC7xb1SfCYwk1rbp9s0qR3vYyGndQyRod4H10JvbWeQ2sQlgUFMW9PkpLetSTQaMCTfqdcn8jWNV0qBiI7ZenabDyRWbvIbsVwWR/Co6OZ3d1mcg2tRYtkyBwu+a9518P0ogULZqEPbcIOOqrJ/eak0Kp3LSXzqJYlejzvSTGqcUF9TUFCqEjUI0jkrx3n0LJKm9BNSMVz1yTVNc+r041ICT2xxsNG8yRaxQwzRCLyVX6XywIGHccMz/DDB9onT+iLzj4wKbAKRVqD1fc5Hc2eR1gTTRXh1Y0A7+d0Sf4cGAjoFIQ6+KMOXa8zg9SALI+B1o75HAOf21EJFMFmPmjQGHd2er8Ooi4ndxA5pcqe5KAuB+FpY2M0MGSS93et+rzieEyg4rQXhY8Puvek8gHp/MYBSHFbzylxzeMi9CBSOVub+pC0Q+TzFEcvuWpwxsM/pMCP/FIkb3PB9T6eGgw0uuoTpPOW3WAuc93MGnrNI6JlIxiYVKDHg0h5PhAo/OgiMJQn3ZB+jYMOa6J5kGog3/PucH7X47XUsTNzMoPqd8zMCdETgmp7Y6hAmwfiOZwOCLqFHE1Ecj1piZwDFVJrdHMB9Z8nwvrMscVL7I6ZuRYnYmRqmVIxH4Wg88+0MT+SUcasuXlL+c6sMcroecev9I8j7FuEOn2IeIQ94U6G3omwjCQHvj7dQaeeoVAaJiakjTvUiSicv8/mjDISKh8n+HeI7B3yOeUBxLeP2Dm/KwvD5PwdGYVCA+358C7tO4QxSqHip01Cs795RGR3cpA+k4ap/s0RK8Mk253LboR9hyBTDAesnD5n+HcI9CzHWrRnMHoJRX5sP/z99/99+e9vuE/FQUFyBpu1xl+mRDmbqfjEXTHyPqHMDURJC3KSRkuz9vzbPpFMD0OhXqTlDEbv060SdvdPJG2TEl2QfXlLbWfo9z7nJ5AyYRkrEHc30tXCuxj4tg8gvYjGlrs7ck6bDGKybLdPIOyBjiVwzEgo1El5JvR9IiRiFlcgvoOpg55zoiF+n0hME2Wvd2PQGR54QoS/Zb0/kDgnbpgvckik/Ub/nB8o+2fSKZAdGUIDP7MzoNE+EtOqIEp9xgSUOkTZzZduJIsCHtUKMhaeJHkPsf293K6s2HiB+PLWBMtML+Nydh2xsDkFSuj8N72Z0I/YnL65wWlknZH2IkdOIpo7BVHekuNmofAqSZpUkQr23C5osjcg2L/SILxI6oPxS/M705RtJOQPZs2L5IXwA4MQubb4ezv94mAK0nImMO2gXBtvOjXdwNJyO/SgzbAduE4t70ybO3L7eJEYB2qu+AZY29dGogk5ywqSIUxXcRo+FQu6kWl4u9XbiR0xh5srt5b3zJ7ORko+A3UILB0R5bKxq6n3alczH4IoIdCsZivNyUbOdDmj3I78CR4HNac7R+x8ao43qY3JwgHb8fmkhPGy+w0zzB+XxAfbIiOopUnDXu4OzsPaqndDT2UQRc66rq/KMPLwtgWItUyNTSOaGrmBchFpr0DMi/JwuMQmuq9GBv1oDBZf5hYGNE27vFJIsdl2SlPGyj2OZQpPxN07k1hlvHVJOeqOi6Y2uXegvBvIWESyK/BNohUOYZrpqZJwKkhq7qWd/cveEx03JVKBuXtH2qTFIHujZlx6K6RkSmmu3wR97+sbuHCco56o/sws2pGi7zfipPmbNep7g5iwiCTpezV22g6e5dbKHVCDfK83j3hqGF2BTLO001SaPisTJS3b0ArkfegAzgxr984o7LXprAlHzyH4SN+FX9m4XGSiHshSaWluWVS5emcH3SfmqECjL5EA1ls2w60X+G09ZvNKIcd+5rZChnbL4Lo1v/wU4EK4Ee+Zzny8JzJ4RpTe4qww9nZUHe/kOxgcOFmrQUNW+tly2UQAd76pMqJSr2ZLha5ci1Ku3Qhk+hSf5AGDFAFs5OblDp4cClTuOHNN2HrYjhi9L5CZ06tO4Hfw5ZgSfCa24gUiZxC5AidNNScviPSCG4iacUIFpm4wkXkiHfIGjZiRrQLEzhFMTJLIuN/8vh370dXoC2lQvBAsX++JjJtDxdO4Y11yHUmHtAuDfZdjLDESaOqVXoweewUXFy80ZwWyyVI9nCvecBcGMy+yjiditPDzeL38IPbenKvoOILmV7SChEt7RRRnL20eoSwMGgJOAenajQMSFZaTJT9WdWzTetUbnx+r8gF7zCjmdTS0vTBe1g4YSXY8yb0R6G4BGi9WVUXEi9djFWSO9Y51vL/XUYB+aX5vyz0eK7vDJcUsPhU3WlXFjWOrshPn+W0Sy8Xa9Pay59Zay5YLZ+coUsc02vHi39jqKg7Dg4VllVO83GaWs8Ce98J+RCAN9GvLUMxxKHsSlVcx/RC11244K9nSAzcxbRhsYRa3zb78CuVH9vCqpJoV3fOD1cZFfo2suGX5ZRhbhoXQF8c6eajHs8vlN2SBMTvL+SFE97256PwfySbzQ4cXAAA="


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


def render(data, settings):
    s = _resolved(settings)
    fig, ax = plt.subplots(figsize=s["figure.size"], facecolor=s["figure.facecolor"])
    labels = s["legend.labels"]
    for author_class, color, label in [("AI", s["series.ai.color"], labels[0]),
                                        ("Domain", s["series.domain.color"], labels[1])]:
        subset = data[data["author_class"] == author_class]
        ax.step(subset["career_age"], subset["cdf"], where=s["series.step_where"],
                color=color, lw=s["series.line_width"], label=label)
    ax.set(xlabel=s["axes.x_label"], ylabel=s["axes.y_label"],
           xlim=s["axes.x_range"], ylim=s["axes.y_range"])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=s["format.percent_decimals"]))
    legend = ax.legend(frameon=False, loc=s["legend.location"], fontsize=s["legend.font_size"],
                       handlelength=s["legend.handle_length"], labelspacing=s["legend.label_spacing"],
                       borderaxespad=s["legend.border_axes_pad"])
    ax.xaxis.label.set_size(s["typography.axis_label_size"])
    ax.yaxis.label.set_size(s["typography.axis_label_size"])
    ax.tick_params(labelsize=s["typography.tick_label_size"], direction="out",
                   width=s["typography.tick_width"], length=s["typography.tick_length"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for spine in ax.spines.values():
        spine.set_linewidth(s["axes.spine_width"])
    ax.grid(s["axes.grid"])
    for item in [ax.xaxis.label, ax.yaxis.label, *ax.get_xticklabels(), *ax.get_yticklabels(), *legend.get_texts()]:
        item.set_fontfamily(s["typography.font_family"])
    fig.tight_layout()
    return fig
