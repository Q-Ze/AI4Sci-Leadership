"""Matplot Studio figure for Figure 3d."""

from __future__ import annotations

from csv import DictReader
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, PercentFormatter
import numpy as np
import pandas as pd


PLOT_META = {
    "id": "fig-3-a-chaperone-routes",
    "name": "Figure 3a — Chaperone paper routes",
    "description": "Paper-level shares of established Domain-led, chaperoned AI-led, and independent AI-led AI4Sci routes.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "Annual counts and shares of classified AI4Sci papers. Chaperoned AI-led papers have an AI Specialist last author previously exposed to a Domain-led AI4Sci paper.",
    "data_export": {"csv": True, "json": True, "note": "Complete embedded annual counts, raw shares, and five-year EWMAs."},
}

PLOT_SCHEMA = [
    {'path': 'layout.mode', 'label': '布局模式', 'group': '坐标轴对齐', 'type': 'select', 'default': 'auto', 'options': [{'value': 'auto', 'label': '自动布局（原外观）'}, {'value': 'fixed', 'label': '固定边距（毫米）'}], 'required': True},
    {'path': 'layout.left_mm', 'label': '左边距 / Y 轴位置（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 15.642167, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.right_mm', 'label': '右边距（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 3.048, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.bottom_mm', 'label': '下边距 / X 轴位置（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 7.989645, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.top_mm', 'label': '上边距（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 4.075327, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'axes.main.x_label_pad', 'label': 'X 轴标题间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 4.0, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.y_label_pad', 'label': 'Y 轴标题间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 4.0, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.x_tick_pad', 'label': 'X 刻度文字间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 3.5, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.y_tick_pad', 'label': 'Y 刻度文字间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 3.5, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},

    {'path': 'figure.size', 'label': 'Figure size', 'group': 'Figure', 'type': 'number_pair', 'default': [3.83, 2.43], 'min': 1.5, 'max': 12, 'step': 0.01, 'required': True},
    {'path': 'figure.facecolor', 'label': 'Background', 'group': 'Figure', 'type': 'color', 'default': '#FFFFFF', 'required': True},
    {'path': 'axes.main.x_label', 'label': 'X-axis label', 'group': 'Axes', 'type': 'string', 'default': 'Year', 'required': True},
    {'path': 'axes.main.y_label', 'label': 'Y-axis label', 'group': 'Axes', 'type': 'string', 'default': 'Share of classified AI4Sci papers', 'required': True},
    {'path': 'axes.main.x_range', 'label': 'X-axis range', 'group': 'Axes', 'type': 'number_pair', 'default': [1995, 2024], 'min': 1995, 'max': 2024, 'step': 1, 'required': True},
    {'path': 'axes.main.y_range', 'label': 'Y-axis range', 'group': 'Axes', 'type': 'number_pair', 'default': [0, 1], 'min': 0, 'max': 1, 'step': 0.05, 'required': True},
    {'path': 'axes.main.x_tick_step', 'label': 'X tick interval', 'group': 'Axes', 'type': 'number', 'default': 10, 'min': 1, 'max': 30, 'step': 1, 'required': True},
    {'path': 'axes.main.y_tick_step', 'label': 'Y tick interval', 'group': 'Axes', 'type': 'number', 'default': 0.2, 'min': 0.05, 'max': 1, 'step': 0.05, 'required': True},
    {'path': 'axes.main.y_percent_decimals', 'label': 'Y tick decimals', 'group': 'Axes', 'type': 'integer', 'default': 0, 'min': 0, 'max': 3, 'step': 1, 'required': True},
    {'path': 'axes.main.spine_width', 'label': 'Spine width', 'group': 'Axes', 'type': 'number', 'default': 0.6, 'min': 0, 'max': 3, 'step': 0.1, 'required': True},
    {'path': 'axes.main.tick_length', 'label': 'Tick length', 'group': 'Axes', 'type': 'number', 'default': 3, 'min': 0, 'max': 10, 'step': 0.5, 'required': True},
    {'path': 'series.established.color', 'label': 'Established color', 'group': 'Series', 'type': 'color', 'default': '#D55E5E', 'required': True},
    {'path': 'series.established.linewidth', 'label': 'Established width', 'group': 'Series', 'type': 'number', 'default': 1.3, 'min': 0.1, 'max': 5, 'step': 0.1, 'required': True},
    {'path': 'series.established.linestyle', 'label': 'Established style', 'group': 'Series', 'type': 'select', 'default': '-', 'options': ['-', '--', ':', '-.'], 'required': True},
    {'path': 'series.chaperoned.color', 'label': 'Chaperoned color', 'group': 'Series', 'type': 'color', 'default': '#7A5195', 'required': True},
    {'path': 'series.chaperoned.linewidth', 'label': 'Chaperoned width', 'group': 'Series', 'type': 'number', 'default': 1.3, 'min': 0.1, 'max': 5, 'step': 0.1, 'required': True},
    {'path': 'series.chaperoned.linestyle', 'label': 'Chaperoned style', 'group': 'Series', 'type': 'select', 'default': '-', 'options': ['-', '--', ':', '-.'], 'required': True},
    {'path': 'series.independent.color', 'label': 'Independent color', 'group': 'Series', 'type': 'color', 'default': '#3B6FB6', 'required': True},
    {'path': 'series.independent.linewidth', 'label': 'Independent width', 'group': 'Series', 'type': 'number', 'default': 1.3, 'min': 0.1, 'max': 5, 'step': 0.1, 'required': True},
    {'path': 'series.independent.linestyle', 'label': 'Independent style', 'group': 'Series', 'type': 'select', 'default': '-', 'options': ['-', '--', ':', '-.'], 'required': True},
    {'path': 'typography.font_family', 'label': 'Font family', 'group': 'Typography', 'type': 'string', 'default': 'Arial', 'required': True},
    {'path': 'typography.label_size', 'label': 'Axis-label size', 'group': 'Typography', 'type': 'number', 'default': 9, 'min': 4, 'max': 20, 'step': 0.5, 'required': True},
    {'path': 'typography.tick_size', 'label': 'Tick-label size', 'group': 'Typography', 'type': 'number', 'default': 8, 'min': 4, 'max': 20, 'step': 0.5, 'required': True},
    {'path': 'annotations.established.visible', 'label': '显示标注', 'group': 'Established 曲线标注', 'type': 'boolean', 'default': True, 'required': True},
    {'path': 'annotations.established.text', 'label': '标注文字', 'group': 'Established 曲线标注', 'type': 'text', 'default': 'Established:\nDomain Specialist-led', 'required': True},
    {'path': 'annotations.established.font_family', 'label': '字体', 'group': 'Established 曲线标注', 'type': 'string', 'default': 'Arial', 'required': True},
    {'path': 'annotations.established.font_size', 'label': '字号 (pt)', 'group': 'Established 曲线标注', 'type': 'number', 'default': 8, 'required': True, 'min': 3, 'max': 24, 'step': 0.5},
    {'path': 'annotations.established.color', 'label': '文字颜色', 'group': 'Established 曲线标注', 'type': 'color', 'default': '#D55E5E', 'required': True},
    {'path': 'annotations.established.year', 'label': '标注对应年份', 'group': 'Established 曲线标注', 'type': 'number', 'default': 2007, 'required': True, 'min': 1995, 'max': 2024, 'step': 0.5},
    {'path': 'annotations.established.offset', 'label': '相对曲线偏移 (pt，右 / 上为正)', 'group': 'Established 曲线标注', 'type': 'number_pair', 'default': [0, 20], 'required': True, 'min': -100, 'max': 100, 'step': 1},
    {'path': 'annotations.independent.visible', 'label': '显示标注', 'group': 'Independent 曲线标注', 'type': 'boolean', 'default': True, 'required': True},
    {'path': 'annotations.independent.text', 'label': '标注文字', 'group': 'Independent 曲线标注', 'type': 'text', 'default': 'Independent:\nAI Specialist-led', 'required': True},
    {'path': 'annotations.independent.font_family', 'label': '字体', 'group': 'Independent 曲线标注', 'type': 'string', 'default': 'Arial', 'required': True},
    {'path': 'annotations.independent.font_size', 'label': '字号 (pt)', 'group': 'Independent 曲线标注', 'type': 'number', 'default': 8, 'required': True, 'min': 3, 'max': 24, 'step': 0.5},
    {'path': 'annotations.independent.color', 'label': '文字颜色', 'group': 'Independent 曲线标注', 'type': 'color', 'default': '#3B6FB6', 'required': True},
    {'path': 'annotations.independent.year', 'label': '标注对应年份', 'group': 'Independent 曲线标注', 'type': 'number', 'default': 2003, 'required': True, 'min': 1995, 'max': 2024, 'step': 0.5},
    {'path': 'annotations.independent.offset', 'label': '相对曲线偏移 (pt，右 / 上为正)', 'group': 'Independent 曲线标注', 'type': 'number_pair', 'default': [0, 20], 'required': True, 'min': -100, 'max': 100, 'step': 1},
    {'path': 'annotations.chaperoned.visible', 'label': '显示标注', 'group': 'Chaperoned 曲线标注', 'type': 'boolean', 'default': True, 'required': True},
    {'path': 'annotations.chaperoned.text', 'label': '标注文字', 'group': 'Chaperoned 曲线标注', 'type': 'text', 'default': 'Chaperoned:\nAI Specialist-led', 'required': True},
    {'path': 'annotations.chaperoned.font_family', 'label': '字体', 'group': 'Chaperoned 曲线标注', 'type': 'string', 'default': 'Arial', 'required': True},
    {'path': 'annotations.chaperoned.font_size', 'label': '字号 (pt)', 'group': 'Chaperoned 曲线标注', 'type': 'number', 'default': 8, 'required': True, 'min': 3, 'max': 24, 'step': 0.5},
    {'path': 'annotations.chaperoned.color', 'label': '文字颜色', 'group': 'Chaperoned 曲线标注', 'type': 'color', 'default': '#7A5195', 'required': True},
    {'path': 'annotations.chaperoned.year', 'label': '标注对应年份', 'group': 'Chaperoned 曲线标注', 'type': 'number', 'default': 2015, 'required': True, 'min': 1995, 'max': 2024, 'step': 0.5},
    {'path': 'annotations.chaperoned.offset', 'label': '相对曲线偏移 (pt，右 / 上为正)', 'group': 'Chaperoned 曲线标注', 'type': 'number_pair', 'default': [0, -20], 'required': True, 'min': -100, 'max': 100, 'step': 1},
]

PLOT_SETTINGS = {
    'layout.mode': 'auto',
    'layout.left_mm': 15.642167,
    'layout.right_mm': 3.048,
    'layout.bottom_mm': 7.989645,
    'layout.top_mm': 4.075327,
    'axes.main.x_label_pad': 4.0,
    'axes.main.y_label_pad': 4.0,
    'axes.main.x_tick_pad': 3.5,
    'axes.main.y_tick_pad': 3.5,
'figure.size': [3.83, 3.2],
 'figure.facecolor': '#FFFFFF',
 'axes.main.x_label': '',
 'axes.main.y_label': 'Percent of AI4Sci papers',
 'axes.main.x_range': [1995, 2024],
 'axes.main.y_range': [0, 0.8],
 'axes.main.x_tick_step': 10,
 'axes.main.y_tick_step': 0.2,
 'axes.main.y_percent_decimals': 0,
 'axes.main.spine_width': 0.6,
 'axes.main.tick_length': 3,
 'series.established.color': '#D55E5E',
 'series.established.linewidth': 1.3,
 'series.established.linestyle': '-',
 'series.chaperoned.color': '#7A5195',
 'series.chaperoned.linewidth': 1.3,
 'series.chaperoned.linestyle': '-',
 'series.independent.color': '#3B6FB6',
 'series.independent.linewidth': 1.3,
 'series.independent.linestyle': '-',
 'typography.font_family': 'Arial',
 'typography.label_size': 9,
 'typography.tick_size': 8,
 'annotations.established.visible': True,
 'annotations.established.text': 'Domain-led',
 'annotations.established.font_family': 'Arial',
 'annotations.established.font_size': 8,
 'annotations.established.color': '#D55E5E',
 'annotations.established.year': 2007,
 'annotations.established.offset': [0, 10],
 'annotations.independent.visible': True,
 'annotations.independent.text': 'Independent AI-led',
 'annotations.independent.font_family': 'Arial',
 'annotations.independent.font_size': 8,
 'annotations.independent.color': '#3B6FB6',
 'annotations.independent.year': 2003,
 'annotations.independent.offset': [5, 15],
 'annotations.chaperoned.visible': True,
 'annotations.chaperoned.text': 'Chaperoned AI-led',
 'annotations.chaperoned.font_family': 'Arial',
 'annotations.chaperoned.font_size': 8,
 'annotations.chaperoned.color': '#7A5195',
 'annotations.chaperoned.year': 2015,
 'annotations.chaperoned.offset': [-10, -15]}


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


_CSV_DATA = """year,category,n,share,share_ewma5
1995,Established: Domain Specialist-led,1311,0.60778859527121,0.60778859527121
1995,Independent: AI Specialist-led,846,0.39221140472878996,0.39221140472878996
1996,Chaperoned: AI Specialist-led,49,0.01912568306010929,0.01912568306010929
1996,Established: Domain Specialist-led,1571,0.6131928181108509,0.6095900028844237
1996,Independent: AI Specialist-led,942,0.36768149882903983,0.38403476942887327
1997,Chaperoned: AI Specialist-led,98,0.039805036555645816,0.026018800891954796
1997,Established: Domain Specialist-led,1514,0.6149471974004874,0.6113757343897783
1997,Independent: AI Specialist-led,850,0.34524776604386676,0.37110576830053776
1998,Chaperoned: AI Specialist-led,139,0.04896090172595984,0.03366616783662314
1998,Established: Domain Specialist-led,1676,0.5903487143360339,0.6043667277051968
1998,Independent: AI Specialist-led,1024,0.36069038393800634,0.3676339735130273
1999,Chaperoned: AI Specialist-led,197,0.06608520630660852,0.04447251399328493
1999,Established: Domain Specialist-led,1791,0.6008050989600805,0.6031795181234914
1999,Independent: AI Specialist-led,993,0.333109694733311,0.3561258805864552
2000,Chaperoned: AI Specialist-led,259,0.07742899850523169,0.05545800883060052
2000,Established: Domain Specialist-led,2086,0.6236173393124066,0.6099921251864632
2000,Independent: AI Specialist-led,1000,0.29895366218236175,0.3370684744517574
2001,Chaperoned: AI Specialist-led,296,0.08305274971941638,0.06465625579353915
2001,Established: Domain Specialist-led,2167,0.6080246913580247,0.6093363139103171
2001,Independent: AI Specialist-led,1101,0.30892255892255893,0.32768650260869125
2002,Chaperoned: AI Specialist-led,513,0.0954951600893522,0.07493589055881017
2002,Established: Domain Specialist-led,3115,0.5798585256887565,0.5995103845031302
2002,Independent: AI Specialist-led,1744,0.3246463142218913,0.32667310647975795
2003,Chaperoned: AI Specialist-led,547,0.10791083053856776,0.08592753721872937
2003,Established: Domain Specialist-led,2978,0.5874926020911423,0.5955044570324676
2003,Independent: AI Specialist-led,1544,0.30459656737029,0.3193142601099353
2004,Chaperoned: AI Specialist-led,826,0.11494572780406345,0.09560026741384073
2004,Established: Domain Specialist-led,4114,0.5725020873921514,0.5878370004856955
2004,Independent: AI Specialist-led,2246,0.31255218480378516,0.31706023500788527
2005,Chaperoned: AI Specialist-led,891,0.11694448090300565,0.10271500524356238
2005,Established: Domain Specialist-led,4452,0.5843286520540754,0.5866675510084889
2005,Independent: AI Specialist-led,2276,0.298726867042919,0.3109491123528966
2006,Chaperoned: AI Specialist-led,1264,0.12222007348675304,0.10921669465795927
2006,Established: Domain Specialist-led,5851,0.5657513053567975,0.5796954691245918
2006,Independent: AI Specialist-led,3227,0.3120286211564494,0.31130894862074754
2007,Chaperoned: AI Specialist-led,1715,0.14631857350055455,0.12158398760549105
2007,Established: Domain Specialist-led,6640,0.5665045644569576,0.575298500902047
2007,Independent: AI Specialist-led,3366,0.2871768620424878,0.30326491976132763
2008,Chaperoned: AI Specialist-led,1779,0.15504619138922782,0.13273805553340332
2008,Established: Domain Specialist-led,6514,0.5677183196792749,0.5727717738277897
2008,Independent: AI Specialist-led,3181,0.2772354889314973,0.29458844281805086
2009,Chaperoned: AI Specialist-led,1990,0.16311475409836065,0.14286362172172246
2009,Established: Domain Specialist-led,7041,0.5771311475409836,0.5742248983988544
2009,Independent: AI Specialist-led,3169,0.2597540983606557,0.2829769946655858
2010,Chaperoned: AI Specialist-led,2608,0.17848343826991514,0.15473689390445336
2010,Established: Domain Specialist-led,8391,0.5742540377771694,0.5742346115249595
2010,Independent: AI Specialist-led,3613,0.24726252395291543,0.27107217109469567
2011,Chaperoned: AI Specialist-led,2727,0.1835127860026918,0.16432885793719954
2011,Established: Domain Specialist-led,8632,0.5808882907133244,0.5764525045877478
2011,Independent: AI Specialist-led,3501,0.23559892328398385,0.25924775515779175
2012,Chaperoned: AI Specialist-led,3027,0.1826024009169331,0.17042003893044405
2012,Established: Domain Specialist-led,9870,0.5954032695903964,0.5827694262552974
2012,Independent: AI Specialist-led,3680,0.22199432949267056,0.24682994660275137
2013,Chaperoned: AI Specialist-led,3565,0.19109133790737565,0.1773104719227546
2013,Established: Domain Specialist-led,11161,0.5982525728987993,0.5879304751364647
2013,Independent: AI Specialist-led,3930,0.21065608919382503,0.23477199413310929
2014,Chaperoned: AI Specialist-led,3857,0.19079891169923324,0.18180661851491414
2014,Established: Domain Specialist-led,12099,0.5985159534998763,0.5914589679242686
2014,Independent: AI Specialist-led,4259,0.21068513480089043,0.2267430410223697
2015,Chaperoned: AI Specialist-led,4048,0.19828557433259858,0.18729960378747562
2015,Established: Domain Specialist-led,12355,0.6051922605927015,0.5960367321470795
2015,Independent: AI Specialist-led,4012,0.19652216507469997,0.2166694157064798
2016,Chaperoned: AI Specialist-led,4770,0.20449284060704792,0.19303068272733306
2016,Established: Domain Specialist-led,14191,0.6083769184600875,0.6001501275847488
2016,Independent: AI Specialist-led,4365,0.18713024093286462,0.20682302411527476
2017,Chaperoned: AI Specialist-led,5011,0.19196291756052714,0.19267476100506442
2017,Established: Domain Specialist-led,16362,0.626800490346307,0.6090335818386016
2017,Independent: AI Specialist-led,4731,0.1812365920931658,0.19829421344123846
2018,Chaperoned: AI Specialist-led,6605,0.19201697773126344,0.19245549991379746
2018,Established: Domain Specialist-led,21689,0.6305308448165591,0.6161993361645874
2018,Independent: AI Specialist-led,6104,0.17745217745217745,0.19134686811155147
2019,Chaperoned: AI Specialist-led,8557,0.18329227803362966,0.1894010926204082
2019,Established: Domain Specialist-led,30629,0.6560779693691764,0.6294922138994505
2019,Independent: AI Specialist-led,7499,0.16062975259719395,0.18110782960676564
2020,Chaperoned: AI Specialist-led,10629,0.1815867700823453,0.18679631844105393
2020,Established: Domain Specialist-led,38907,0.6646906071684833,0.6412250116557948
2020,Independent: AI Specialist-led,8998,0.15372262274917142,0.1719794273209009
2021,Chaperoned: AI Specialist-led,14963,0.1886100361766226,0.18740089101957683
2021,Established: Domain Specialist-led,52897,0.6667717091248283,0.6497405774788061
2021,Independent: AI Specialist-led,11473,0.14461825469854916,0.16285903644678368
2022,Chaperoned: AI Specialist-led,16348,0.17854373491475814,0.18444850565130394
2022,Established: Domain Specialist-led,61465,0.6712864366610968,0.6569225305395697
2022,Independent: AI Specialist-led,13750,0.1501698284241451,0.1586293004392375
2023,Chaperoned: AI Specialist-led,16966,0.1731648566995999,0.18068728933406927
2023,Established: Domain Specialist-led,68699,0.7011819221033723,0.6716756610608372
2023,Independent: AI Specialist-led,12311,0.12565322119702785,0.14763727402516763
2024,Chaperoned: AI Specialist-led,12388,0.13959882803696191,0.16699113556836684
2024,Established: Domain Specialist-led,66383,0.748061753437007,0.6971376918528939
2024,Independent: AI Specialist-led,9969,0.1123394185260311,0.13587132219212214
"""


def prepare_data():
    rows = []
    for row in DictReader(StringIO(_CSV_DATA)):
        if not row or "year" not in row:
            continue
        rows.append({
            "year": int(row["year"]), "category": row["category"],
            "n": int(row["n"]), "share": float(row["share"]),
            "share_ewma5": float(row["share_ewma5"]),
        })
    return pd.DataFrame(rows)


def _apply_axis_alignment(fig, axes, c):
    """Apply main-axis text spacing and optional physical margins; leave insets attached."""
    for axis in axes:
        axis.xaxis.labelpad = c["axes.main.x_label_pad"]
        axis.yaxis.labelpad = c["axes.main.y_label_pad"]
        axis.tick_params(axis="x", which="major", pad=c["axes.main.x_tick_pad"])
        axis.tick_params(axis="y", which="major", pad=c["axes.main.y_tick_pad"])
    if c["layout.mode"] != "fixed":
        fig.tight_layout()
        return
    width_mm, height_mm = fig.get_size_inches() * 25.4
    left, right = c["layout.left_mm"], c["layout.right_mm"]
    bottom, top = c["layout.bottom_mm"], c["layout.top_mm"]
    if min(left, right, bottom, top) < 0 or left + right >= width_mm or bottom + top >= height_mm:
        raise ValueError("固定边距无效：左右边距之和须小于画布宽度，上下边距之和须小于画布高度。")
    fig.set_layout_engine(None)
    fig.subplots_adjust(left=left / width_mm, right=1 - right / width_mm,
                        bottom=bottom / height_mm, top=1 - top / height_mm,
                        wspace=c.get("layout.wspace", 0.2))


def render(data, settings):
    c = _resolved(settings)
    style = {
        "font.family": c["typography.font_family"], "font.size": 8,
        "axes.labelsize": c["typography.label_size"],
        "xtick.labelsize": c["typography.tick_size"],
        "ytick.labelsize": c["typography.tick_size"],
        "axes.linewidth": c["axes.main.spine_width"],
        "xtick.major.width": c["axes.main.spine_width"],
        "ytick.major.width": c["axes.main.spine_width"],
        "xtick.major.size": c["axes.main.tick_length"],
        "ytick.major.size": c["axes.main.tick_length"],
    }
    with plt.rc_context(style):
        return _draw(data, c)


def _draw(data, c):
    fig, ax = plt.subplots(figsize=tuple(c["figure.size"]), facecolor=c["figure.facecolor"])
    ax.set_facecolor(c["figure.facecolor"])
    specs = [
        ("Established: Domain Specialist-led", "established"),
        ("Chaperoned: AI Specialist-led", "chaperoned"),
        ("Independent: AI Specialist-led", "independent"),
    ]
    for category, key in specs:
        subset = data.loc[data.category.eq(category)]
        ax.plot(subset.year, subset.share_ewma5, color=c[f"series.{key}.color"],
                lw=c[f"series.{key}.linewidth"], ls=c[f"series.{key}.linestyle"],
                label=c[f"annotations.{key}.text"])
        prefix = f"annotations.{key}"
        if c[f"{prefix}.visible"]:
            # Anchor to the actual smoothed curve; offsets are display points.
            ordered = subset.sort_values("year")
            year = float(np.clip(c[f"{prefix}.year"], ordered.year.min(), ordered.year.max()))
            share = float(np.interp(year, ordered.year, ordered.share_ewma5))
            ax.annotate(
                c[f"{prefix}.text"], xy=(year, share), xycoords="data",
                xytext=c[f"{prefix}.offset"], textcoords="offset points",
                fontfamily=c[f"{prefix}.font_family"], fontsize=c[f"{prefix}.font_size"],
                color=c[f"{prefix}.color"], ha="center", va="center", zorder=4,
            )
    ax.set_xlabel(c["axes.main.x_label"], family=c["typography.font_family"], fontsize=c["typography.label_size"])
    ax.set_ylabel(c["axes.main.y_label"], family=c["typography.font_family"], fontsize=c["typography.label_size"])
    ax.set_xlim(*c["axes.main.x_range"]); ax.set_ylim(*c["axes.main.y_range"])
    ax.xaxis.set_major_locator(MultipleLocator(c["axes.main.x_tick_step"]))
    ax.yaxis.set_major_locator(MultipleLocator(c["axes.main.y_tick_step"]))
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=c["axes.main.y_percent_decimals"]))
    ax.tick_params(labelsize=c["typography.tick_size"], direction="out",
                   width=c["axes.main.spine_width"], length=c["axes.main.tick_length"])
    for tick in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        tick.set_fontfamily(c["typography.font_family"])
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(c["axes.main.spine_width"])
    ax.spines["bottom"].set_linewidth(c["axes.main.spine_width"])
    ax.grid(False); _apply_axis_alignment(fig, [ax], c)
    return fig
