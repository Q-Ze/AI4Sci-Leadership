"""Manuscript Figure 3B: career age at first AI4Sci publication."""

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd

PLOT_META = {
    "id": "fig-3-b-ecdf-career-age-common-window",
    "name": "Figure 3B — Career-age ECDF",
    "description": "Career-age distributions at first AI4Sci publication in a common observation window.",
    "version": 1, "data_mode": "inline",
    "data_note": "Final grouped ECDF values from the common-window analysis are embedded.",
    "data_export": {"csv": True, "json": True, "note": "Grouped career-age counts and cumulative shares."},
}
PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [3.8, 2.4], "min": 1, "max": 16, "step": 0.1, "required": True},
    {"path": "axes.main.xlabel", "label": "X label", "group": "Axes", "type": "string", "default": "Career age at first AI4Sci paper (years)"},
    {"path": "axes.main.ylabel", "label": "Y label", "group": "Axes", "type": "string", "default": "Cumulative share"},
    {"path": "axes.main.x_range", "label": "X range", "group": "Axes", "type": "number_pair", "default": [0, 29]},
    {"path": "series.ai.color", "label": "AI Specialist color", "group": "Series", "type": "color", "default": "#3B6FB6"},
    {"path": "series.domain.color", "label": "Domain Specialist color", "group": "Series", "type": "color", "default": "#D55E5E"},
    {"path": "series.lines.linewidth", "label": "Step width", "group": "Series", "type": "number", "default": 1.3, "min": 0.1, "max": 8, "step": 0.1},
    {"path": "reference.median.color", "label": "Median guide color", "group": "Reference", "type": "color", "default": "#B8B8B8"},
    {"path": "legend.visible", "label": "Show legend", "group": "Legend", "type": "boolean", "default": True},
    {"path": "typography.label_size", "label": "Label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 30, "step": 0.5},
    {"path": "typography.tick_size", "label": "Tick size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 30, "step": 0.5},
]
PLOT_SETTINGS = {
    "figure.size": [3.8, 2.4], "axes.main.xlabel": "Career age at first AI4Sci paper (years)",
    "axes.main.ylabel": "Cumulative share", "axes.main.x_range": [0, 29],
    "series.ai.color": "#3B6FB6", "series.domain.color": "#D55E5E", "series.lines.linewidth": 1.3,
    "reference.median.color": "#B8B8B8", "legend.visible": True,
    "typography.label_size": 9, "typography.tick_size": 8,
}
_DATA = [{'leader_class': 'AI', 'career_age': 0, 'n': 158028, 'total': 336289, 'cdf': 0.4699172437992322},
 {'leader_class': 'AI', 'career_age': 1, 'n': 35786, 'total': 336289, 'cdf': 0.5763316671077555},
 {'leader_class': 'AI', 'career_age': 2, 'n': 26336, 'total': 336289, 'cdf': 0.654645260475365},
 {'leader_class': 'AI', 'career_age': 3, 'n': 15666, 'total': 336289, 'cdf': 0.7012301918885244},
 {'leader_class': 'AI', 'career_age': 4, 'n': 12938, 'total': 336289, 'cdf': 0.7397030530287937},
 {'leader_class': 'AI', 'career_age': 5, 'n': 10856, 'total': 336289, 'cdf': 0.7719848106836679},
 {'leader_class': 'AI', 'career_age': 6, 'n': 9236, 'total': 336289, 'cdf': 0.7994492832058141},
 {'leader_class': 'AI', 'career_age': 7, 'n': 8115, 'total': 336289, 'cdf': 0.8235803133614242},
 {'leader_class': 'AI', 'career_age': 8, 'n': 7206, 'total': 336289, 'cdf': 0.8450083113036704},
 {'leader_class': 'AI', 'career_age': 9, 'n': 6618, 'total': 336289, 'cdf': 0.8646878131607041},
 {'leader_class': 'AI', 'career_age': 10, 'n': 6060, 'total': 336289, 'cdf': 0.8827080279164647},
 {'leader_class': 'AI', 'career_age': 11, 'n': 5628, 'total': 336289, 'cdf': 0.8994436333034979},
 {'leader_class': 'AI', 'career_age': 12, 'n': 5048, 'total': 336289, 'cdf': 0.9144545316677024},
 {'leader_class': 'AI', 'career_age': 13, 'n': 4380, 'total': 336289, 'cdf': 0.9274790433228562},
 {'leader_class': 'AI', 'career_age': 14, 'n': 3811, 'total': 336289, 'cdf': 0.9388115579159592},
 {'leader_class': 'AI', 'career_age': 15, 'n': 3505, 'total': 336289, 'cdf': 0.9492341408728802},
 {'leader_class': 'AI', 'career_age': 16, 'n': 3123, 'total': 336289, 'cdf': 0.9585207961009726},
 {'leader_class': 'AI', 'career_age': 17, 'n': 2760, 'total': 336289, 'cdf': 0.9667280226233984},
 {'leader_class': 'AI', 'career_age': 18, 'n': 2365, 'total': 336289, 'cdf': 0.9737606641906218},
 {'leader_class': 'AI', 'career_age': 19, 'n': 1912, 'total': 336289, 'cdf': 0.97944625010036},
 {'leader_class': 'AI', 'career_age': 20, 'n': 1659, 'total': 336289, 'cdf': 0.9843795069122094},
 {'leader_class': 'AI', 'career_age': 21, 'n': 1299, 'total': 336289, 'cdf': 0.9882422559167858},
 {'leader_class': 'AI', 'career_age': 22, 'n': 1111, 'total': 336289, 'cdf': 0.991545961955342},
 {'leader_class': 'AI', 'career_age': 23, 'n': 830, 'total': 336289, 'cdf': 0.9940140771776655},
 {'leader_class': 'AI', 'career_age': 24, 'n': 665, 'total': 336289, 'cdf': 0.9959915429883226},
 {'leader_class': 'AI', 'career_age': 25, 'n': 510, 'total': 336289, 'cdf': 0.9975080957152924},
 {'leader_class': 'AI', 'career_age': 26, 'n': 390, 'total': 336289, 'cdf': 0.9986678125065048},
 {'leader_class': 'AI', 'career_age': 27, 'n': 234, 'total': 336289, 'cdf': 0.9993636425812322},
 {'leader_class': 'AI', 'career_age': 28, 'n': 150, 'total': 336289, 'cdf': 0.9998096875009292},
 {'leader_class': 'AI', 'career_age': 29, 'n': 64, 'total': 336289, 'cdf': 1.0},
 {'leader_class': 'Domain', 'career_age': 0, 'n': 200754, 'total': 759877, 'cdf': 0.264192757512071},
 {'leader_class': 'Domain', 'career_age': 1, 'n': 55523, 'total': 759877, 'cdf': 0.3372611620038506},
 {'leader_class': 'Domain', 'career_age': 2, 'n': 43683, 'total': 759877, 'cdf': 0.3947480973894459},
 {'leader_class': 'Domain', 'career_age': 3, 'n': 36192, 'total': 759877, 'cdf': 0.4423768583599714},
 {'leader_class': 'Domain', 'career_age': 4, 'n': 31290, 'total': 759877, 'cdf': 0.4835545752799466},
 {'leader_class': 'Domain', 'career_age': 5, 'n': 28260, 'total': 759877, 'cdf': 0.5207448047512953},
 {'leader_class': 'Domain', 'career_age': 6, 'n': 26568, 'total': 759877, 'cdf': 0.5557083580632128},
 {'leader_class': 'Domain', 'career_age': 7, 'n': 24913, 'total': 759877, 'cdf': 0.5884939273066562},
 {'leader_class': 'Domain', 'career_age': 8, 'n': 23951, 'total': 759877, 'cdf': 0.6200135021852221},
 {'leader_class': 'Domain', 'career_age': 9, 'n': 22989, 'total': 759877, 'cdf': 0.6502670826989105},
 {'leader_class': 'Domain', 'career_age': 10, 'n': 22380, 'total': 759877, 'cdf': 0.6797192177154987},
 {'leader_class': 'Domain', 'career_age': 11, 'n': 21647, 'total': 759877, 'cdf': 0.7082067229301584},
 {'leader_class': 'Domain', 'career_age': 12, 'n': 20840, 'total': 759877, 'cdf': 0.735632214160976},
 {'leader_class': 'Domain', 'career_age': 13, 'n': 19990, 'total': 759877, 'cdf': 0.761939103302245},
 {'leader_class': 'Domain', 'career_age': 14, 'n': 18719, 'total': 759877, 'cdf': 0.786573353319024},
 {'leader_class': 'Domain', 'career_age': 15, 'n': 18338, 'total': 759877, 'cdf': 0.8107062063991936},
 {'leader_class': 'Domain', 'career_age': 16, 'n': 17543, 'total': 759877, 'cdf': 0.8337928375250205},
 {'leader_class': 'Domain', 'career_age': 17, 'n': 17013, 'total': 759877, 'cdf': 0.8561819873479524},
 {'leader_class': 'Domain', 'career_age': 18, 'n': 16078, 'total': 759877, 'cdf': 0.8773406748723807},
 {'leader_class': 'Domain', 'career_age': 19, 'n': 14742, 'total': 759877, 'cdf': 0.89674118311253},
 {'leader_class': 'Domain', 'career_age': 20, 'n': 13988, 'total': 759877, 'cdf': 0.9151494254991268},
 {'leader_class': 'Domain', 'career_age': 21, 'n': 12623, 'total': 759877, 'cdf': 0.9317613245301544},
 {'leader_class': 'Domain', 'career_age': 22, 'n': 11452, 'total': 759877, 'cdf': 0.946832184682521},
 {'leader_class': 'Domain', 'career_age': 23, 'n': 10027, 'total': 759877, 'cdf': 0.9600277413318208},
 {'leader_class': 'Domain', 'career_age': 24, 'n': 8673, 'total': 759877, 'cdf': 0.9714414306525924},
 {'leader_class': 'Domain', 'career_age': 25, 'n': 7084, 'total': 759877, 'cdf': 0.9807639920671372},
 {'leader_class': 'Domain', 'career_age': 26, 'n': 5839, 'total': 759877, 'cdf': 0.9884481304211076},
 {'leader_class': 'Domain', 'career_age': 27, 'n': 4403, 'total': 759877, 'cdf': 0.99424248924497},
 {'leader_class': 'Domain', 'career_age': 28, 'n': 2937, 'total': 759877, 'cdf': 0.9981075884649752},
 {'leader_class': 'Domain', 'career_age': 29, 'n': 1438, 'total': 759877, 'cdf': 1.0}]


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


def prepare_data():
    return pd.DataFrame(_DATA)


def render(data, settings):
    cfg = _resolved(settings)
    fig, ax = plt.subplots(figsize=cfg["figure.size"])
    ax.axhline(0.5, color=cfg["reference.median.color"], lw=0.7, ls="--", zorder=0)
    for leader, label, color_path in [
        ("AI", "AI Specialist", "series.ai.color"),
        ("Domain", "Domain Specialist", "series.domain.color"),
    ]:
        subset = data.loc[data["leader_class"].eq(leader)].sort_values("career_age")
        median = float(subset.loc[subset["cdf"].ge(0.5), "career_age"].iloc[0])
        ax.step(subset["career_age"], subset["cdf"], where="post", color=cfg[color_path],
                lw=cfg["series.lines.linewidth"], label=label)
        ax.vlines(median, 0, 0.5, color=cfg[color_path], lw=0.7, ls=":")
        ax.scatter([median], [0.5], s=15, color=cfg[color_path], zorder=3)
        ax.text(median + 0.25, 0.525 if leader == "AI" else 0.475, f"{median:g} y",
                color=cfg[color_path], fontsize=6.5, va="bottom" if leader == "AI" else "top")
    ax.set(xlim=cfg["axes.main.x_range"], ylim=(0, 1),
           xlabel=cfg["axes.main.xlabel"], ylabel=cfg["axes.main.ylabel"])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    if cfg["legend.visible"]:
        ax.legend(frameon=False, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=cfg["typography.tick_size"], direction="out")
    ax.xaxis.label.set_size(cfg["typography.label_size"])
    ax.yaxis.label.set_size(cfg["typography.label_size"])
    ax.grid(False)
    fig.tight_layout()
    return fig

