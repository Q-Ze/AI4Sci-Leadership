"""Matplot Studio figure for Figure 1e."""

from __future__ import annotations

from csv import DictReader
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "fig-1-e-line-historical-jcr-last-author-composition",
    "name": "Figure 1e — Historical JCR last-author composition",
    "description": "AI- and Domain-origin last-author shares by lagged historical JCR quartile.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "AI4Sci journals are assigned the JCR quartile available one year before publication. Shares use AI- plus Domain-origin classified last-author positions as the denominator. Lines show 5-year EWMAs for 1998–2024; journals without a valid historical JCR match are excluded.",
    "data_export": {
        "csv": True,
        "json": True,
        "note": "Exports the complete embedded calculation table used by the figure.",
    },
}

PLOT_SCHEMA = [
    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.45, 2.15], "min": 1.5, "max": 12, "step": 0.05, "required": True},
    {"path": "figure.facecolor", "label": "Background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.main.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Publication year", "required": True},
    {"path": "axes.main.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "Last-author share", "required": True},
    {"path": "axes.main.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1998, 2024], "min": 1998, "max": 2024, "step": 1, "required": True},
    {"path": "axes.main.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0.20, 0.80], "min": 0, "max": 1, "step": 0.05, "required": True},
    {"path": "axes.main.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 3, "step": 0.1, "required": True},
    {"path": "axes.main.tick_length", "label": "Tick length", "group": "Axes", "type": "number", "default": 3.0, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "series.q1.color", "label": "Q1 color", "group": "Series", "type": "color", "default": "#440154", "required": True},
    {"path": "series.q2.color", "label": "Q2 color", "group": "Series", "type": "color", "default": "#31688E", "required": True},
    {"path": "series.q3.color", "label": "Q3 color", "group": "Series", "type": "color", "default": "#35B779", "required": True},
    {"path": "series.q4.color", "label": "Q4 color", "group": "Series", "type": "color", "default": "#FDE725", "required": True},
    {"path": "series.ai.linestyle", "label": "AI-origin line style", "group": "Series", "type": "select", "default": "-", "options": ["-", "--", ":", "-."], "required": True},
    {"path": "series.domain.linestyle", "label": "Domain-origin line style", "group": "Series", "type": "select", "default": "--", "options": ["-", "--", ":", "-."], "required": True},
    {"path": "series.linewidth", "label": "Line width", "group": "Series", "type": "number", "default": 1.25, "min": 0.2, "max": 5, "step": 0.05, "required": True},
    {"path": "legend.q1_label", "label": "Q1 legend label", "group": "Legend", "type": "string", "default": "Q1", "required": True},
    {"path": "legend.q2_label", "label": "Q2 legend label", "group": "Legend", "type": "string", "default": "Q2", "required": True},
    {"path": "legend.q3_label", "label": "Q3 legend label", "group": "Legend", "type": "string", "default": "Q3", "required": True},
    {"path": "legend.q4_label", "label": "Q4 legend label", "group": "Legend", "type": "string", "default": "Q4", "required": True},
    {"path": "legend.ai_label", "label": "AI legend label", "group": "Legend", "type": "string", "default": "AI-origin", "required": True},
    {"path": "legend.domain_label", "label": "Domain legend label", "group": "Legend", "type": "string", "default": "Domain-origin", "required": True},
    {"path": "legend.location", "label": "Legend location", "group": "Legend", "type": "select", "default": "best", "options": ["best", "upper left", "upper right", "lower left", "lower right"], "required": True},
    {"path": "legend.columns", "label": "Legend columns", "group": "Legend", "type": "integer", "default": 3, "min": 1, "max": 6, "step": 1, "required": True},
    {"path": "legend.font_size", "label": "Legend font size", "group": "Legend", "type": "number", "default": 7.5, "min": 4, "max": 16, "step": 0.5, "required": True},
    {"path": "legend.frame", "label": "Legend frame", "group": "Legend", "type": "boolean", "default": False, "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.label_size", "label": "Axis-label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "typography.tick_size", "label": "Tick-label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 20, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    "figure.size": [2.45, 2.15],
    "figure.facecolor": "#FFFFFF",
    "axes.main.x_label": "Publication year",
    "axes.main.y_label": "Last-author share",
    "axes.main.x_range": [1998, 2024],
    "axes.main.y_range": [0.20, 0.80],
    "axes.main.spine_width": 0.6,
    "axes.main.tick_length": 3.0,
    "series.q1.color": "#440154",
    "series.q2.color": "#31688E",
    "series.q3.color": "#35B779",
    "series.q4.color": "#FDE725",
    "series.ai.linestyle": "-",
    "series.domain.linestyle": "--",
    "series.linewidth": 1.25,
    "legend.q1_label": "Q1",
    "legend.q2_label": "Q2",
    "legend.q3_label": "Q3",
    "legend.q4_label": "Q4",
    "legend.ai_label": "AI-origin",
    "legend.domain_label": "Domain-origin",
    "legend.location": "best",
    "legend.columns": 3,
    "legend.font_size": 7.5,
    "legend.frame": False,
    "typography.font_family": "Arial",
    "typography.label_size": 9,
    "typography.tick_size": 8,
}


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


_CSV_DATA = """year,specification,jcr,n_ai,n_domain,n_classified,ai_specialist_share,domain_specialist_share,ai_specialist_share_ewma5,domain_specialist_share_ewma5
1998,Historical lagged,Q1,189,369,558,0.3387096774193548,0.6612903225806451,0.3387096774193548,0.6612903225806451
1998,Historical lagged,Q2,133,178,311,0.42765273311897106,0.572347266881029,0.42765273311897106,0.572347266881029
1998,Historical lagged,Q3,35,94,129,0.2713178294573643,0.7286821705426356,0.2713178294573643,0.7286821705426356
1998,Historical lagged,Q4,70,77,147,0.47619047619047616,0.5238095238095238,0.47619047619047616,0.5238095238095238
1999,Historical lagged,Q1,230,459,689,0.33381712626995647,0.6661828737300436,0.33707882703622205,0.6629211729637781
1999,Historical lagged,Q2,63,160,223,0.2825112107623318,0.7174887892376681,0.379272225666758,0.620727774333242
1999,Historical lagged,Q3,91,126,217,0.41935483870967744,0.5806451612903226,0.32066349920813536,0.6793365007918646
1999,Historical lagged,Q4,61,86,147,0.41496598639455784,0.5850340136054422,0.45578231292517013,0.54421768707483
2000,Historical lagged,Q1,195,469,664,0.2936746987951807,0.7063253012048193,0.3226107842892083,0.6773892157107919
2000,Historical lagged,Q2,105,202,307,0.34201954397394135,0.6579804560260586,0.3668546651024858,0.6331453348975142
2000,Historical lagged,Q3,84,150,234,0.358974358974359,0.6410256410256411,0.33343378579687655,0.6665662142031235
2000,Historical lagged,Q4,41,50,91,0.45054945054945056,0.5494505494505495,0.454038025466597,0.5459619745334032
2001,Historical lagged,Q1,211,489,700,0.30142857142857143,0.6985714285714286,0.315550046668996,0.6844499533310042
2001,Historical lagged,Q2,87,189,276,0.31521739130434784,0.6847826086956522,0.34964224050310655,0.6503577594968937
2001,Historical lagged,Q3,61,108,169,0.3609467455621302,0.6390532544378699,0.34260477238529446,0.6573952276147056
2001,Historical lagged,Q4,66,106,172,0.38372093023255816,0.6162790697674418,0.4305989937219174,0.5694010062780828
2002,Historical lagged,Q1,248,529,777,0.31917631917631917,0.6808236808236808,0.3167588041714371,0.6832411958285631
2002,Historical lagged,Q2,122,211,333,0.3663663663663664,0.6336336336336337,0.3552169491241932,0.644783050875807
2002,Historical lagged,Q3,69,129,198,0.3484848484848485,0.6515151515151515,0.3445647977518125,0.6554352022481876
2002,Historical lagged,Q4,62,98,160,0.3875,0.6125,0.41623266248127827,0.5837673375187219
2003,Historical lagged,Q1,252,487,739,0.34100135317997293,0.6589986468200271,0.32483965384094904,0.6751603461590512
2003,Historical lagged,Q2,148,222,370,0.4,0.6,0.3701446327494622,0.629855367250538
2003,Historical lagged,Q3,77,160,237,0.32489451476793246,0.6751054852320675,0.3380080367571858,0.6619919632428143
2003,Historical lagged,Q4,77,141,218,0.3532110091743119,0.6467889908256881,0.39522544471228954,0.6047745552877106
2004,Historical lagged,Q1,340,673,1013,0.33563672260612043,0.6643632773938796,0.32843867676267285,0.6715613232373273
2004,Historical lagged,Q2,184,239,423,0.43498817966903075,0.5650118203309693,0.39175914838931836,0.6082408516106819
2004,Historical lagged,Q3,77,161,238,0.3235294117647059,0.6764705882352942,0.33318182842635924,0.666818171573641
2004,Historical lagged,Q4,80,112,192,0.4166666666666667,0.5833333333333334,0.40237251869708196,0.5976274813029182
2005,Historical lagged,Q1,429,680,1109,0.38683498647430115,0.6131650135256989,0.34790411333321564,0.6520958866667845
2005,Historical lagged,Q2,120,190,310,0.3870967741935484,0.6129032258064516,0.39020502365739507,0.6097949763426052
2005,Historical lagged,Q3,136,189,325,0.41846153846153844,0.5815384615384616,0.3616083984380857,0.6383916015619145
2005,Historical lagged,Q4,80,138,218,0.3669724770642202,0.6330275229357798,0.3905725048194614,0.6094274951805387
2006,Historical lagged,Q1,503,911,1414,0.35572842998585574,0.6442715700141443,0.35051221888409567,0.6494877811159044
2006,Historical lagged,Q2,151,287,438,0.3447488584474886,0.6552511415525114,0.3750529685874263,0.6249470314125739
2006,Historical lagged,Q3,130,221,351,0.37037037037037035,0.6296296296296297,0.36452905574884725,0.635470944251153
2006,Historical lagged,Q4,100,154,254,0.3937007874015748,0.6062992125984252,0.3916152656801659,0.6083847343198343
2007,Historical lagged,Q1,544,950,1494,0.36412315930388217,0.6358768406961178,0.35504919902402454,0.6449508009759757
2007,Historical lagged,Q2,143,302,445,0.32134831460674157,0.6786516853932584,0.35715141726053146,0.6428485827394688
2007,Historical lagged,Q3,139,179,318,0.4371069182389937,0.5628930817610063,0.3887216765788961,0.6112783234211041
2007,Historical lagged,Q4,166,232,398,0.41708542713567837,0.5829145728643216,0.4001053194986701,0.5998946805013301
2008,Historical lagged,Q1,631,1149,1780,0.3544943820224719,0.645505617977528,0.354864260023507,0.6451357399764932
2008,Historical lagged,Q2,247,382,629,0.39268680445151033,0.6073131955484896,0.3689965463241911,0.6310034536758091
2008,Historical lagged,Q3,136,240,376,0.3617021276595745,0.6382978723404256,0.3797151602724556,0.6202848397275447
2008,Historical lagged,Q4,176,261,437,0.40274599542334094,0.597254004576659,0.40098554480689375,0.5990144551931065
2009,Historical lagged,Q1,671,1241,1912,0.35094142259414224,0.6490585774058577,0.3535566475470521,0.646443352452948
2009,Historical lagged,Q2,199,338,537,0.37057728119180633,0.6294227188081937,0.3695234579467295,0.6304765420532707
2009,Historical lagged,Q3,170,286,456,0.37280701754385964,0.6271929824561403,0.3774124460295903,0.6225875539704099
2009,Historical lagged,Q4,227,281,508,0.4468503937007874,0.5531496062992126,0.416273827771525,0.5837261722284752
2010,Historical lagged,Q1,775,1475,2250,0.34444444444444444,0.6555555555555556,0.3505192465128496,0.6494807534871505
2010,Historical lagged,Q2,210,465,675,0.3111111111111111,0.6888888888888889,0.3500526756681901,0.6499473243318101
2010,Historical lagged,Q3,212,380,592,0.3581081081081081,0.6418918918918919,0.3709776667224296,0.6290223332775706
2010,Historical lagged,Q4,220,325,545,0.4036697247706422,0.5963302752293578,0.4120724601045641,0.5879275398954361
2011,Historical lagged,Q1,754,1641,2395,0.3148225469728601,0.6851774530271398,0.33862034666618646,0.6613796533338137
2011,Historical lagged,Q2,281,628,909,0.30913091309130913,0.6908690869086909,0.3364120881425631,0.663587911857437
2011,Historical lagged,Q3,218,360,578,0.3771626297577855,0.6228373702422145,0.3730393210675482,0.626960678932452
2011,Historical lagged,Q4,286,390,676,0.4230769230769231,0.5769230769230769,0.4157406144286838,0.5842593855713164
2012,Historical lagged,Q1,808,1669,2477,0.32620104965684293,0.6737989503431571,0.3344805809964053,0.6655194190035948
2012,Historical lagged,Q2,290,693,983,0.2950152594099695,0.7049847405900305,0.3226131452316986,0.6773868547683015
2012,Historical lagged,Q3,265,401,666,0.3978978978978979,0.6021021021021021,0.3813255133443315,0.6186744866556687
2012,Historical lagged,Q4,286,467,753,0.3798140770252324,0.6201859229747676,0.4037651019608667,0.5962348980391335
2013,Historical lagged,Q1,819,1870,2689,0.3045741911491261,0.6954258088508739,0.3245117843806456,0.6754882156193546
2013,Historical lagged,Q2,301,819,1120,0.26875,0.73125,0.3046587634877991,0.695341236512201
2013,Historical lagged,Q3,359,569,928,0.38685344827586204,0.6131465517241379,0.3831681583215084,0.6168318416784918
2013,Historical lagged,Q4,359,486,845,0.42485207100591715,0.5751479289940828,0.4107940916425502,0.58920590835745
2014,Historical lagged,Q1,1069,2108,3177,0.33648095687755747,0.6635190431224426,0.3285015085462829,0.6714984914537173
2014,Historical lagged,Q2,420,1015,1435,0.2926829268292683,0.7073170731707317,0.3006668179349555,0.6993331820650446
2014,Historical lagged,Q3,330,540,870,0.3793103448275862,0.6206896551724138,0.38188222049020104,0.6181177795097992
2014,Historical lagged,Q4,411,526,937,0.4386339381003202,0.5613660618996799,0.4200740404618069,0.5799259595381934
2015,Historical lagged,Q1,1108,2513,3621,0.3059928196630765,0.6940071803369235,0.32099861225188075,0.6790013877481195
2015,Historical lagged,Q2,393,1002,1395,0.2817204301075269,0.7182795698924731,0.29435135532581264,0.7056486446741874
2015,Historical lagged,Q3,419,690,1109,0.37781785392245265,0.6221821460775473,0.38052743163428493,0.6194725683657152
2015,Historical lagged,Q4,402,612,1014,0.39644970414201186,0.6035502958579881,0.41219926168854193,0.5878007383114583
2016,Historical lagged,Q1,1270,2691,3961,0.3206261045190608,0.6793738954809392,0.3208744430076075,0.6791255569923927
2016,Historical lagged,Q2,573,1277,1850,0.30972972972972973,0.6902702702702703,0.2994774801271184,0.7005225198728817
2016,Historical lagged,Q3,312,689,1001,0.3116883116883117,0.6883116883116883,0.35758105831896053,0.6424189416810395
2016,Historical lagged,Q4,406,600,1006,0.40357852882703776,0.5964214711729622,0.4093256840680406,0.5906743159319596
2017,Historical lagged,Q1,1546,3592,5138,0.30089528999610743,0.6991047100038925,0.3142147253371075,0.6857852746628927
2017,Historical lagged,Q2,494,1202,1696,0.29127358490566035,0.7087264150943396,0.2967428483866324,0.7032571516133677
2017,Historical lagged,Q3,372,868,1240,0.3,0.7,0.33838737221264037,0.6616126277873597
2017,Historical lagged,Q4,356,618,974,0.3655030800821355,0.6344969199178645,0.3947181494060723,0.6052818505939279
2018,Historical lagged,Q1,1913,4734,6647,0.28779900707085904,0.712200992929141,0.3054094859150247,0.6945905140849755
2018,Historical lagged,Q2,679,1973,2652,0.2560331825037707,0.7439668174962293,0.28317295975901186,0.7168270402409882
2018,Historical lagged,Q3,618,1202,1820,0.3395604395604396,0.6604395604395604,0.3387783946619068,0.6612216053380934
2018,Historical lagged,Q4,360,765,1125,0.32,0.68,0.36981209960404826,0.6301879003959521
2019,Historical lagged,Q1,2923,7290,10213,0.2862038578282581,0.7137961421717419,0.29900760988610253,0.7009923901138977
2019,Historical lagged,Q2,908,2685,3593,0.25271360979682717,0.7472863902031729,0.2730198431049503,0.7269801568950498
2019,Historical lagged,Q3,590,1505,2095,0.28162291169451076,0.7183770883054893,0.31972656700610813,0.6802734329938921
2019,Historical lagged,Q4,497,953,1450,0.3427586206896552,0.6572413793103449,0.3607942732992506,0.6392057267007497
2020,Historical lagged,Q1,3881,9910,13791,0.2814154158509173,0.7185845841490828,0.29314354520770747,0.7068564547922928
2020,Historical lagged,Q2,1551,4570,6121,0.25338996895932037,0.7466100310406796,0.26647655172307366,0.7335234482769264
2020,Historical lagged,Q3,712,2046,2758,0.25815808556925307,0.7418419144307469,0.2992037398604898,0.7007962601395104
2020,Historical lagged,Q4,561,1034,1595,0.35172413793103446,0.6482758620689655,0.3577708948431786,0.6422291051568216
2021,Historical lagged,Q1,3789,10911,14700,0.2577551020408163,0.7422448979591837,0.28134739748541043,0.7186526025145898
2021,Historical lagged,Q2,2910,7875,10785,0.2698191933240612,0.7301808066759388,0.26759076559006956,0.7324092344099306
2021,Historical lagged,Q3,1070,2951,4021,0.2661029594628202,0.7338970405371799,0.2881701463946,0.7118298536054002
2021,Historical lagged,Q4,781,1574,2355,0.3316348195329087,0.6683651804670913,0.3490588697397553,0.6509411302602448
2022,Historical lagged,Q1,4275,12377,16652,0.2567259188085515,0.7432740811914484,0.2731402379264575,0.7268597620735427
2022,Historical lagged,Q2,4219,11422,15641,0.2697397864586663,0.7302602135413336,0.2683071058796018,0.7316928941203983
2022,Historical lagged,Q3,1548,3903,5451,0.28398458998348924,0.7160154100165107,0.28677496092422977,0.7132250390757704
2022,Historical lagged,Q4,973,1720,2693,0.3613070924619384,0.6386929075380616,0.35314161064714966,0.6468583893528504
2023,Historical lagged,Q1,4598,14324,18922,0.2429975689673396,0.7570024310326604,0.26309268160675153,0.7369073183932486
2023,Historical lagged,Q2,4396,13295,17691,0.2484879317166921,0.7515120682833079,0.2617007144919653,0.7382992855080348
2023,Historical lagged,Q3,996,3170,4166,0.23907825252040327,0.7609217474795967,0.2708760581229543,0.7291239418770459
2023,Historical lagged,Q4,837,1834,2671,0.31336578060651443,0.6866342193934856,0.3398830006336046,0.6601169993663956
2024,Historical lagged,Q1,5452,20950,26402,0.20649950761305963,0.7935004923869404,0.2442282902755209,0.7557717097244793
2024,Historical lagged,Q2,3518,11528,15046,0.2338162966901502,0.7661837033098498,0.2524059085580269,0.7475940914419732
2024,Historical lagged,Q3,1528,4555,6083,0.251191846128555,0.7488081538714451,0.2643146541248212,0.735685345875179
2024,Historical lagged,Q4,812,1885,2697,0.3010752688172043,0.6989247311827957,0.3269470900281379,0.6730529099718623
"""


def prepare_data():
    """Parse and return the complete CSV embedded in this module."""
    integer_columns = {"year", "n_ai", "n_domain", "n_classified"}
    rows = []
    for row in DictReader(StringIO(_CSV_DATA)):
        rows.append(
            {
                key: int(value) if key in integer_columns else value if key in {"specification", "jcr"} else float(value)
                for key, value in row.items()
            }
        )
    return pd.DataFrame(rows)


def render(data, settings):
    """Render and return one Matplotlib Figure without external I/O."""
    config = _resolved(settings)
    colors = {q: config[f"series.{q.lower()}.color"] for q in ["Q1", "Q2", "Q3", "Q4"]}
    fig, ax = plt.subplots(figsize=tuple(config["figure.size"]), facecolor=config["figure.facecolor"])
    ax.set_facecolor(config["figure.facecolor"])
    for quartile in ["Q1", "Q2", "Q3", "Q4"]:
        subset = data[data["jcr"] == quartile]
        ax.plot(subset["year"], subset["ai_specialist_share_ewma5"], color=colors[quartile], linewidth=config["series.linewidth"], linestyle=config["series.ai.linestyle"])
        ax.plot(subset["year"], subset["domain_specialist_share_ewma5"], color=colors[quartile], linewidth=config["series.linewidth"], linestyle=config["series.domain.linestyle"])
    handles = [Line2D([], [], color=colors[q], linewidth=config["series.linewidth"], label=config[f"legend.{q.lower()}_label"]) for q in ["Q1", "Q2", "Q3", "Q4"]]
    handles.extend([
        Line2D([], [], color="#333333", linewidth=config["series.linewidth"], linestyle=config["series.ai.linestyle"], label=config["legend.ai_label"]),
        Line2D([], [], color="#333333", linewidth=config["series.linewidth"], linestyle=config["series.domain.linestyle"], label=config["legend.domain_label"]),
    ])
    ax.set_xlabel(config["axes.main.x_label"], family=config["typography.font_family"], fontsize=config["typography.label_size"])
    ax.set_ylabel(config["axes.main.y_label"], family=config["typography.font_family"], fontsize=config["typography.label_size"])
    ax.set_xlim(*config["axes.main.x_range"])
    ax.set_ylim(*config["axes.main.y_range"])
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.tick_params(axis="both", direction="out", labelsize=config["typography.tick_size"], width=config["axes.main.spine_width"], length=config["axes.main.tick_length"])
    for label in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        label.set_fontfamily(config["typography.font_family"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(config["axes.main.spine_width"])
    ax.spines["bottom"].set_linewidth(config["axes.main.spine_width"])
    ax.grid(False)
    legend = ax.legend(
        handles=handles,
        loc=config["legend.location"],
        frameon=config["legend.frame"],
        ncols=config["legend.columns"],
        fontsize=config["legend.font_size"],
        columnspacing=0.8,
        handlelength=1.5,
        labelspacing=0.3,
        borderaxespad=0.2,
    )
    for text in legend.get_texts():
        text.set_fontfamily(config["typography.font_family"])
    fig.tight_layout()
    return fig


