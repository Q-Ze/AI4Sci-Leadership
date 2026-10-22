"""Matplot Studio figure for Figure 3a."""

from __future__ import annotations

from csv import DictReader
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, MultipleLocator
import numpy as np
import pandas as pd


PLOT_META = {
    "id": "fig-3-d-citation-entropy",
    "name": "Figure 3d — Global-normalized citation entropy",
    "description": "Five-year EWMAs of globally normalized citation entropy for AI and Domain references, with a Domain-minus-AI inset.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "Annual Shannon entropy for AI4Sci references, normalized by the global cited-work universe for each cited-paper type. The table includes both main curves and the inset gap.",
    "data_export": {"csv": True, "json": True, "note": "Complete embedded annual entropy and gap table."},
}

PLOT_SCHEMA = [
    {'path': 'layout.mode', 'label': '布局模式', 'group': '坐标轴对齐', 'type': 'select', 'default': 'auto', 'options': [{'value': 'auto', 'label': '自动布局（原外观）'}, {'value': 'fixed', 'label': '固定边距（毫米）'}], 'required': True},
    {'path': 'layout.left_mm', 'label': '左边距 / Y 轴位置（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 15.388167, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.right_mm', 'label': '右边距（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 3.048, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.bottom_mm', 'label': '下边距 / X 轴位置（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 7.989645, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.top_mm', 'label': '上边距（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 3.048, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'axes.main.x_label_pad', 'label': 'X 轴标题间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 4.0, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.y_label_pad', 'label': 'Y 轴标题间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 4.0, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.x_tick_pad', 'label': 'X 刻度文字间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 3.5, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.y_tick_pad', 'label': 'Y 刻度文字间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 3.5, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},

    {'path': 'figure.size', 'label': 'Figure size', 'group': 'Figure', 'type': 'number_pair', 'default': [3.83, 2.43], 'min': 1.5, 'max': 12, 'step': 0.01, 'required': True},
    {'path': 'figure.facecolor', 'label': 'Background', 'group': 'Figure', 'type': 'color', 'default': '#FFFFFF', 'required': True},
    {'path': 'axes.main.x_label', 'label': 'X-axis label', 'group': 'Main axes', 'type': 'string', 'default': 'AI4Sci publication year', 'required': True},
    {'path': 'axes.main.y_label', 'label': 'Y-axis label', 'group': 'Main axes', 'type': 'string', 'default': 'Diversity of cited knowledge', 'required': True},
    {'path': 'axes.main.x_range', 'label': 'X-axis range', 'group': 'Main axes', 'type': 'number_pair', 'default': [1995, 2024], 'min': 1995, 'max': 2024, 'step': 1, 'required': True},
    {'path': 'axes.main.y_range', 'label': 'Y-axis range', 'group': 'Main axes', 'type': 'number_pair', 'default': [0.5, 0.9], 'min': 0, 'max': 1, 'step': 0.01, 'required': True},
    {'path': 'axes.main.x_tick_step', 'label': 'X tick interval', 'group': 'Main axes', 'type': 'number', 'default': 10, 'min': 1, 'max': 30, 'step': 1, 'required': True},
    {'path': 'axes.main.y_tick_step', 'label': 'Y tick interval', 'group': 'Main axes', 'type': 'number', 'default': 0.1, 'min': 0.01, 'max': 0.5, 'step': 0.01, 'required': True},
    {'path': 'axes.main.y_decimals', 'label': 'Y tick decimals', 'group': 'Main axes', 'type': 'integer', 'default': 1, 'min': 0, 'max': 4, 'step': 1, 'required': True},
    {'path': 'axes.main.spine_width', 'label': 'Spine width', 'group': 'Main axes', 'type': 'number', 'default': 0.6, 'min': 0, 'max': 3, 'step': 0.1, 'required': True},
    {'path': 'axes.main.tick_length', 'label': 'Tick length', 'group': 'Main axes', 'type': 'number', 'default': 3, 'min': 0, 'max': 10, 'step': 0.5, 'required': True},
    {'path': 'series.ai.color', 'label': 'AI-paper color', 'group': 'Main series', 'type': 'color', 'default': '#3B6FB6', 'required': True},
    {'path': 'series.domain.color', 'label': 'Domain-paper color', 'group': 'Main series', 'type': 'color', 'default': '#D55E5E', 'required': True},
    {'path': 'series.linewidth', 'label': 'Main line width', 'group': 'Main series', 'type': 'number', 'default': 1.3, 'min': 0.1, 'max': 5, 'step': 0.1, 'required': True},
    {'path': 'inset.position', 'label': 'Inset lower-left position', 'group': 'Inset', 'type': 'number_pair', 'default': [0.53, 0.095], 'min': 0, 'max': 1, 'step': 0.005, 'required': True},
    {'path': 'inset.size', 'label': 'Inset size', 'group': 'Inset', 'type': 'number_pair', 'default': [0.42, 0.27], 'min': 0.05, 'max': 1, 'step': 0.005, 'required': True},
    {'path': 'inset.y_label', 'label': 'Inset y-axis label', 'group': 'Inset', 'type': 'string', 'default': 'Domain − AI', 'required': True},
    {'path': 'inset.x_range', 'label': 'Inset x-axis range', 'group': 'Inset', 'type': 'number_pair', 'default': [1995, 2024], 'min': 1995, 'max': 2024, 'step': 1, 'required': True},
    {'path': 'inset.y_range', 'label': 'Inset y-axis range', 'group': 'Inset', 'type': 'number_pair', 'default': [-0.05, 0.05], 'min': -0.5, 'max': 0.5, 'step': 0.01, 'required': True},
    {'path': 'inset.x_tick_step', 'label': 'Inset x tick interval', 'group': 'Inset', 'type': 'number', 'default': 10, 'min': 1, 'max': 30, 'step': 1, 'required': True},
    {'path': 'inset.y_tick_step', 'label': 'Inset y tick interval', 'group': 'Inset', 'type': 'number', 'default': 0.05, 'min': 0.005, 'max': 0.2, 'step': 0.005, 'required': True},
    {'path': 'inset.line_color', 'label': 'Inset curve color', 'group': 'Inset', 'type': 'color', 'default': '#7A5195', 'required': True},
    {'path': 'inset.linewidth', 'label': 'Inset curve width', 'group': 'Inset', 'type': 'number', 'default': 1.15, 'min': 0.1, 'max': 5, 'step': 0.05, 'required': True},
    {'path': 'inset.reference_visible', 'label': 'Show inset zero line', 'group': 'Inset', 'type': 'boolean', 'default': True, 'required': True},
    {'path': 'inset.reference_value', 'label': 'Inset reference value', 'group': 'Inset', 'type': 'number', 'default': 0, 'min': -0.5, 'max': 0.5, 'step': 0.01, 'required': True},
    {'path': 'inset.reference_color', 'label': 'Inset reference color', 'group': 'Inset', 'type': 'color', 'default': '#777777', 'required': True},
    {'path': 'inset.reference_linewidth', 'label': 'Inset reference width', 'group': 'Inset', 'type': 'number', 'default': 0.6, 'min': 0.1, 'max': 3, 'step': 0.1, 'required': True},
    {'path': 'inset.spine_width', 'label': 'Inset spine width', 'group': 'Inset', 'type': 'number', 'default': 0.55, 'min': 0, 'max': 3, 'step': 0.05, 'required': True},
    {'path': 'inset.tick_length', 'label': 'Inset tick length', 'group': 'Inset', 'type': 'number', 'default': 2.2, 'min': 0, 'max': 10, 'step': 0.1, 'required': True},
    {'path': 'inset.tick_size', 'label': 'Inset tick size', 'group': 'Inset', 'type': 'number', 'default': 6, 'min': 4, 'max': 16, 'step': 0.1, 'required': True},
    {'path': 'inset.label_size', 'label': 'Inset label size', 'group': 'Inset', 'type': 'number', 'default': 6.5, 'min': 4, 'max': 16, 'step': 0.1, 'required': True},
    {'path': 'typography.font_family', 'label': 'Font family', 'group': 'Typography', 'type': 'string', 'default': 'Arial', 'required': True},
    {'path': 'typography.label_size', 'label': 'Axis-label size', 'group': 'Typography', 'type': 'number', 'default': 9, 'min': 4, 'max': 20, 'step': 0.5, 'required': True},
    {'path': 'typography.tick_size', 'label': 'Tick-label size', 'group': 'Typography', 'type': 'number', 'default': 8, 'min': 4, 'max': 20, 'step': 0.5, 'required': True},
    {'path': 'annotations.ai.visible', 'label': '显示标注', 'group': 'AI papers 曲线标注', 'type': 'boolean', 'default': True, 'required': True},
    {'path': 'annotations.ai.text', 'label': '标注文字', 'group': 'AI papers 曲线标注', 'type': 'text', 'default': 'AI papers', 'required': True},
    {'path': 'annotations.ai.font_family', 'label': '字体', 'group': 'AI papers 曲线标注', 'type': 'string', 'default': 'Arial', 'required': True},
    {'path': 'annotations.ai.font_size', 'label': '字号 (pt)', 'group': 'AI papers 曲线标注', 'type': 'number', 'default': 8, 'required': True, 'min': 3, 'max': 24, 'step': 0.5},
    {'path': 'annotations.ai.color', 'label': '文字颜色', 'group': 'AI papers 曲线标注', 'type': 'color', 'default': '#3B6FB6', 'required': True},
    {'path': 'annotations.ai.year', 'label': '标注对应年份', 'group': 'AI papers 曲线标注', 'type': 'number', 'default': 2004, 'required': True, 'min': 1995, 'max': 2024, 'step': 0.5},
    {'path': 'annotations.ai.offset', 'label': '相对曲线偏移 (pt，右 / 上为正)', 'group': 'AI papers 曲线标注', 'type': 'number_pair', 'default': [0, 12], 'required': True, 'min': -100, 'max': 100, 'step': 1},
    {'path': 'annotations.domain.visible', 'label': '显示标注', 'group': 'Domain papers 曲线标注', 'type': 'boolean', 'default': True, 'required': True},
    {'path': 'annotations.domain.text', 'label': '标注文字', 'group': 'Domain papers 曲线标注', 'type': 'text', 'default': 'Domain papers', 'required': True},
    {'path': 'annotations.domain.font_family', 'label': '字体', 'group': 'Domain papers 曲线标注', 'type': 'string', 'default': 'Arial', 'required': True},
    {'path': 'annotations.domain.font_size', 'label': '字号 (pt)', 'group': 'Domain papers 曲线标注', 'type': 'number', 'default': 8, 'required': True, 'min': 3, 'max': 24, 'step': 0.5},
    {'path': 'annotations.domain.color', 'label': '文字颜色', 'group': 'Domain papers 曲线标注', 'type': 'color', 'default': '#D55E5E', 'required': True},
    {'path': 'annotations.domain.year', 'label': '标注对应年份', 'group': 'Domain papers 曲线标注', 'type': 'number', 'default': 2005, 'required': True, 'min': 1995, 'max': 2024, 'step': 0.5},
    {'path': 'annotations.domain.offset', 'label': '相对曲线偏移 (pt，右 / 上为正)', 'group': 'Domain papers 曲线标注', 'type': 'number_pair', 'default': [0, -12], 'required': True, 'min': -100, 'max': 100, 'step': 1},
]

PLOT_SETTINGS = {
    'layout.mode': 'auto',
    'layout.left_mm': 15.388167,
    'layout.right_mm': 3.048,
    'layout.bottom_mm': 7.989645,
    'layout.top_mm': 3.048,
    'axes.main.x_label_pad': 4.0,
    'axes.main.y_label_pad': 4.0,
    'axes.main.x_tick_pad': 3.5,
    'axes.main.y_tick_pad': 3.5,
'figure.size': [3.83, 1.6],
 'figure.facecolor': '#FFFFFF',
 'axes.main.x_label': '',
 'axes.main.y_label': 'Entropy of cited paper',
 'axes.main.x_range': [1995, 2024],
 'axes.main.y_range': [0.4, 0.89],
 'axes.main.x_tick_step': 10,
 'axes.main.y_tick_step': 0.2,
 'axes.main.y_decimals': 2,
 'axes.main.spine_width': 0.6,
 'axes.main.tick_length': 3,
 'series.ai.color': '#3B6FB6',
 'series.domain.color': '#D55E5E',
 'series.linewidth': 1.3,
 'inset.position': [0.66, 0.185],
 'inset.size': [0.3, 0.25],
 'inset.y_label': 'Domain − AI',
 'inset.x_range': [1995, 2024],
 'inset.y_range': [-0.05, 0.05],
 'inset.x_tick_step': 10,
 'inset.y_tick_step': 0.05,
 'inset.line_color': '#7A5195',
 'inset.linewidth': 1.15,
 'inset.reference_visible': True,
 'inset.reference_value': 0,
 'inset.reference_color': '#777777',
 'inset.reference_linewidth': 0.6,
 'inset.spine_width': 0.55,
 'inset.tick_length': 2.2,
 'inset.tick_size': 6,
 'inset.label_size': 6.5,
 'typography.font_family': 'Arial',
 'typography.label_size': 9,
 'typography.tick_size': 8,
 'annotations.ai.visible': True,
 'annotations.ai.text': 'Cited AI',
 'annotations.ai.font_family': 'Arial',
 'annotations.ai.font_size': 8,
 'annotations.ai.color': '#3B6FB6',
 'annotations.ai.year': 2004,
 'annotations.ai.offset': [10, 12],
 'annotations.domain.visible': True,
 'annotations.domain.text': 'Cited Domain',
 'annotations.domain.font_family': 'Arial',
 'annotations.domain.font_size': 8,
 'annotations.domain.color': '#D55E5E',
 'annotations.domain.year': 2005,
 'annotations.domain.offset': [-20, -14]}


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


_CSV_DATA = """year,cited_type,n_citations,n_unique_cited,entropy_raw,n_global,entropy_global,entropy_year_max,effective_number,entropy_global_ewma5,gap_global,gap_global_ewma5
1995,AI,10819.0,6944,8.54911605412328,597572,0.6427602314392173,0.9664786913922332,5162.18931385786,0.6427602314392173,-0.037986260578244835,-0.037986260578244835
1995,Domain,10182.0,8011,8.8528245388457,2276698,0.6047739708609725,0.9848978954231068,6994.116249795426,0.6047739708609725,-0.037986260578244835,-0.037986260578244835
1996,AI,11471.0,7317,8.600169424201926,597572,0.6465986488568491,0.9665331820969784,5432.579923915485,0.6440397039117614,-0.03800328807614484,-0.03799193641087817
1996,Domain,11077.0,8733,8.908762949035111,2276698,0.6085953607807043,0.9816965544470254,7396.50558216152,0.6060477675008832,-0.03800328807614484,-0.03799193641087817
1997,AI,11478.0,7562,8.655832262329163,597572,0.6507836264019803,0.9692014242923124,5743.547112651691,0.6462876780751677,-0.042049530034757865,-0.03934446761883807
1997,Domain,10947.0,8667,8.910793793390052,2276698,0.6087340963672224,0.9827418773382912,7411.541996910422,0.6069432104563296,-0.042049530034757865,-0.03934446761883807
1998,AI,13382.0,8877,8.828849681889642,597572,0.6637918387055287,0.971140365128216,6828.427432353479,0.6521223982852881,-0.042693557048909536,-0.04046083076219523
1998,Domain,13536.0,10541,9.091783664328082,2276698,0.6210982816566192,0.9815131687414352,8882.014464135913,0.6116615675230928,-0.042693557048909536,-0.04046083076219523
1999,AI,14389.0,9423,8.875094921648166,597572,0.667268759690338,0.969859401624236,7151.625279309396,0.6571711854203047,-0.039432513451514994,-0.04011805832530182
1999,Domain,15244.0,11765,9.190415584796298,2276698,0.6278362462388231,0.9805322768848695,9802.72399585794,0.6170531270950028,-0.039432513451514994,-0.04011805832530182
2000,AI,15518.0,10422,8.984436688343312,597572,0.6754895557143957,0.9711146825618536,7977.949386754912,0.6632773088516684,-0.04258225188662834,-0.04093945617907733
2000,Domain,15770.0,12427,9.264646926130972,2276698,0.6329073038277674,0.9827125234094728,10558.082149450747,0.622337852672591,-0.04258225188662834,-0.04093945617907733
2001,AI,17509.0,11703,9.109664455558285,597572,0.684904731286716,0.9724650893612788,9042.2603021639,0.6704864496633509,-0.04621594584456712,-0.04269828606757393
2001,Domain,17554.0,13649,9.349277622511336,2276698,0.6386887854421489,0.9819203556254248,11490.51995343575,0.6277881635957769,-0.04621594584456712,-0.04269828606757393
2002,AI,23681.0,14872,9.269190143646473,597572,0.69689857574349,0.964813459114198,10606.158942170254,0.679290491690064,-0.04250965102032711,-0.042635407718491655
2002,Domain,24053.0,17951,9.579099977617632,2276698,0.6543889247231629,0.977918094135578,14459.399660807074,0.6366550839715723,-0.04250965102032711,-0.042635407718491655
2003,AI,22739.0,14867,9.302755624420827,597572,0.6994221765525452,0.9683411226010382,10968.201847921046,0.6860010533108911,-0.04330977873577646,-0.04286019805758659
2003,Domain,23857.0,18061,9.60432858471756,2276698,0.6561123978167688,0.9798825275131532,14828.83069445491,0.6431408552533044,-0.04330977873577646,-0.04286019805758659
2004,AI,32416.0,19005,9.487116515518526,597572,0.7132832410509203,0.9629188077896518,13188.711001744565,0.6950951158909009,-0.04721778097425566,-0.044312725696476284
2004,Domain,31248.0,22192,9.750023866023444,2276698,0.6660654600766647,0.9742729345675236,17154.63821740336,0.6507823901944245,-0.04721778097425566,-0.044312725696476284
2005,AI,36453.0,22379,9.664414078585946,597572,0.7266132534111878,0.9649092961128182,15747.140600323884,0.7056011617309965,-0.04404824624257209,-0.04422456587850822
2005,Domain,37093.0,27392,9.991548141890538,2276698,0.6825650071686157,0.9778373460664588,21841.08573775916,0.6613765958524883,-0.04404824624257209,-0.04422456587850822
2006,AI,48022.0,27391,9.79330326464875,597572,0.7363037105928731,0.9584392480968976,17913.38118255061,0.7158353446849555,-0.04385317621847595,-0.04410076932516413
2006,Domain,47541.0,33366,10.13625482908837,2276698,0.6924505343743972,0.9732088309507348,25241.75455479548,0.6717345753597913,-0.04385317621847595,-0.04410076932516413
2007,AI,58861.0,32759,9.967122110903732,597572,0.7493721776881894,0.9586598373721064,21314.0575078676,0.7270142890193668,-0.04643994658550221,-0.04488049507861016
2007,Domain,57433.0,39546,10.289688386873344,2276698,0.7029322311026872,0.972080745780828,29427.60289598525,0.6821337939407566,-0.04643994658550221,-0.04488049507861016
2008,AI,58594.0,33585,9.996814571909308,597572,0.7516045877978567,0.9592182899435536,21956.413704108625,0.7352110552788635,-0.03949464519723711,-0.043085211784819145
2008,Domain,63211.0,44615,10.42403390019574,2276698,0.7121099426006195,0.9736786755344964,33658.937453069826,0.6921258434940443,-0.03949464519723711,-0.043085211784819145
2009,AI,59536.0,34535,10.026155919100546,597572,0.7538105996231708,0.9594656780682824,22610.188880852013,0.7414109033936327,-0.034482685924003165,-0.040217703164547154
2009,Domain,72083.0,50310,10.529692269670432,2276698,0.7193279136991676,0.9726336604555528,37409.960432520405,0.7011932002290854,-0.034482685924003165,-0.040217703164547154
2010,AI,73696.0,40339,10.125580859611023,597572,0.7612858049389909,0.9547864388962992,24973.757676853635,0.7480358705754188,-0.035535544754006,-0.03865698369436677
2010,Domain,83938.0,56984,10.623704097735176,2276698,0.7257502601849849,0.970154701817684,41097.56272927902,0.709378886881052,-0.035535544754006,-0.03865698369436677
2011,AI,79234.0,43957,10.226983966966928,597572,0.7689097375584693,0.956600447057897,27639.02402354972,0.7549938262364356,-0.03505071726656239,-0.03745489488509865
2011,Domain,93447.0,64289,10.742402047569186,2276698,0.7338590202919069,0.9703064308261452,46277.07826281668,0.717538931351337,-0.03505071726656239,-0.03745489488509865
2012,AI,88352.0,48010,10.268035274533776,597572,0.7719961558250482,0.952581730970237,28797.25285322992,0.7606612694326399,-0.030020385047096587,-0.03497672493909797
2012,Domain,107132.0,73080,10.861216962464164,2276698,0.7419757707779516,0.9698112608981232,52115.46217302133,0.7256845444935419,-0.030020385047096587,-0.03497672493909797
2013,AI,102424.0,54657,10.376929870731754,597572,0.7801833315998974,0.9512410976214696,32110.22745674913,0.7671686234883925,-0.029083871346826218,-0.03301244040834072
2013,Domain,129373.0,86059,10.994771688629314,2276698,0.7510994602530712,0.967612113736796,59561.91797195724,0.7341561830800517,-0.029083871346826218,-0.03301244040834072
2014,AI,112016.0,59004,10.428483687130235,597572,0.7840593747779383,0.9493073687297024,33809.046281642586,0.7727988739182412,-0.023991417855427688,-0.030005432890703045
2014,Domain,147303.0,98347,11.12605466576991,2276698,0.7600679569225106,0.9677979846856796,67917.8839707384,0.7427934410275381,-0.023991417855427688,-0.030005432890703045
2015,AI,118973.0,62587,10.492082875986828,597572,0.7888410421561806,0.9499987008323248,36029.123481638046,0.7781462633308878,-0.020937336932060346,-0.026982734237822145
2015,Domain,162931.0,109016,11.240756204174335,2276698,0.7679037052241202,0.96909336921548,76172.53199439007,0.7511635290930655,-0.020937336932060346,-0.026982734237822145
2016,AI,125026.0,64524,10.47585424017257,597572,0.7876209017760667,0.9459187804207914,35449.13886658518,0.7813044761459476,-0.01281589486333623,-0.022260454446326843
2016,Domain,182865.0,121503,11.34177909186894,2276698,0.7748050069127305,0.9687457552554318,84269.82160923994,0.7590440216996205,-0.01281589486333623,-0.022260454446326843
2017,AI,135367.0,69031,10.494972389669108,597572,0.7890582885324621,0.9419026653612552,36133.380680660826,0.7838890802747858,-0.0034452593211297122,-0.0159887227379278
2017,Domain,211766.0,142117,11.499989480595223,2276698,0.7856130292113324,0.9692848961669552,98714.7325850694,0.7679003575368578,-0.0034452593211297122,-0.0159887227379278
2018,AI,172419.0,82386,10.581540624339368,597572,0.7955668700278676,0.9348335503246454,39400.76945221503,0.7877816768591465,0.0051413311033827735,-0.008945371457490942
2018,Domain,281156.0,183416,11.720956180270642,2276698,0.8007082011312504,0.9671145262917782,123125.09872120312,0.7788363054016554,0.0051413311033827735,-0.008945371457490942
2019,AI,233789.0,98719,10.5918641341439,597572,0.7963430370034026,0.9210290441574304,39809.63049124796,0.7906354635738986,0.02061658723839488,0.000908614774470998
2019,Domain,396986.0,246744,11.95884835856561,2276698,0.8169596242417975,0.9631721685750396,156193.10270047208,0.7915440783483695,0.02061658723839488,0.000908614774470998
2020,AI,288047.0,117523,10.742005597836464,597572,0.8076313341022718,0.9201342602809192,46258.73536376725,0.7963007537500231,0.029505906178954877,0.01044104524263229
2020,Domain,551921.0,334946,12.254213078305392,2276698,0.8371372402812267,0.9632509317691296,209863.60072345968,0.8067417989926553,0.029505906178954877,0.01044104524263229
2021,AI,396857.0,147624,10.89302257975862,597572,0.8189854565211294,0.9151936430350054,53799.66824917329,0.8038623213403919,0.03767430356048029,0.019518798015248293
2021,Domain,795288.0,461325,12.53998834423307,2276698,0.8566597600816097,0.9615185415991264,279285.0836276627,0.8233811193556402,0.03767430356048029,0.019518798015248293
2022,AI,439870.0,161310,11.003901849521071,597572,0.8273218488034579,0.9176737090660004,60108.217974571024,0.8116821638280807,0.04365005942630873,0.027562551818935105
2022,Domain,960587.0,558623,12.749492956591338,2276698,0.8709719082297667,0.963445270312422,344377.23765340354,0.8392447156470157,0.04365005942630873,0.027562551818935105
2023,AI,449701.0,165447,11.044796812016578,597572,0.8303965123583681,0.91914309867842,62617.29594745248,0.8179202800048432,0.04984044411230204,0.03498851591672408
2023,Domain,1098597.0,639493,12.885116925830442,2276698,0.8802369564706701,0.9638466152291072,394398.43191597593,0.8529087959215672,0.04984044411230204,0.03498851591672408
2024,AI,349190.0,149745,11.10421708279132,597572,0.8348639902535749,0.9318206563058904,66450.79864408699,0.8235681834210872,0.05361149708217838,0.04119617630520885
2024,Domain,1066504.0,669991,13.005714490739882,2276698,0.8884754873357533,0.9694890442821846,444948.7966142733,0.864764359726296,0.05361149708217838,0.04119617630520885
"""


def prepare_data():
    integer_columns = {"year", "n_unique_cited", "n_global"}
    rows = []
    for row in DictReader(StringIO(_CSV_DATA)):
        if not row or "year" not in row:
            continue
        rows.append({key: (value if key == "cited_type" else int(float(value)) if key in integer_columns else float(value)) for key, value in row.items()})
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
    for cited_type, key in (("AI", "ai"), ("Domain", "domain")):
        subset = data.loc[data.cited_type.eq(cited_type)]
        prefix = f"annotations.{key}"
        ax.plot(subset.year, subset.entropy_global_ewma5,
                color=c[f"series.{key}.color"], lw=c["series.linewidth"],
                label=c[f"{prefix}.text"])
        if c[f"{prefix}.visible"]:
            # Keep the anchor on the actual smoothed curve as its year changes.
            ordered = subset.sort_values("year")
            year = float(np.clip(c[f"{prefix}.year"], ordered.year.min(), ordered.year.max()))
            entropy = float(np.interp(year, ordered.year, ordered.entropy_global_ewma5))
            ax.annotate(
                c[f"{prefix}.text"], xy=(year, entropy), xycoords="data",
                xytext=c[f"{prefix}.offset"], textcoords="offset points",
                fontfamily=c[f"{prefix}.font_family"], fontsize=c[f"{prefix}.font_size"],
                color=c[f"{prefix}.color"], ha="center", va="center", zorder=4,
            )
    ax.set_xlabel(c["axes.main.x_label"], family=c["typography.font_family"], fontsize=c["typography.label_size"])
    ax.set_ylabel(c["axes.main.y_label"], family=c["typography.font_family"], fontsize=c["typography.label_size"])
    ax.set_xlim(*c["axes.main.x_range"]); ax.set_ylim(*c["axes.main.y_range"])
    ax.xaxis.set_major_locator(MultipleLocator(c["axes.main.x_tick_step"]))
    ax.yaxis.set_major_locator(MultipleLocator(c["axes.main.y_tick_step"]))
    ax.yaxis.set_major_formatter(FormatStrFormatter(f"%.{c['axes.main.y_decimals']}f"))
    gap = data.drop_duplicates("year").sort_values("year")
    bounds = [*c["inset.position"], *c["inset.size"]]
    inset = ax.inset_axes(bounds)
    inset.set_facecolor(c["figure.facecolor"])
    if c["inset.reference_visible"]:
        inset.axhline(c["inset.reference_value"], color=c["inset.reference_color"], lw=c["inset.reference_linewidth"])
    inset.plot(gap.year, gap.gap_global_ewma5, color=c["inset.line_color"], lw=c["inset.linewidth"])
    inset.set_xlim(*c["inset.x_range"]); inset.set_ylim(*c["inset.y_range"])
    inset.set_ylabel(c["inset.y_label"], family=c["typography.font_family"], fontsize=c["inset.label_size"])
    inset.xaxis.set_major_locator(MultipleLocator(c["inset.x_tick_step"]))
    inset.yaxis.set_major_locator(MultipleLocator(c["inset.y_tick_step"]))
    inset.xaxis.label.set_visible(False)
    inset.tick_params(labelsize=c["inset.tick_size"], width=c["inset.spine_width"], length=c["inset.tick_length"])
    for tick in [*inset.get_xticklabels(), *inset.get_yticklabels()]:
        tick.set_fontfamily(c["typography.font_family"])
    inset.spines["top"].set_visible(False); inset.spines["right"].set_visible(False)
    inset.spines["left"].set_linewidth(c["inset.spine_width"])
    inset.spines["bottom"].set_linewidth(c["inset.spine_width"])
    inset.grid(False)
    ax.tick_params(labelsize=c["typography.tick_size"], direction="out",
                   width=c["axes.main.spine_width"], length=c["axes.main.tick_length"])
    for tick in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        tick.set_fontfamily(c["typography.font_family"])
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(c["axes.main.spine_width"])
    ax.spines["bottom"].set_linewidth(c["axes.main.spine_width"])
    ax.grid(False); _apply_axis_alignment(fig, [ax], c)
    return fig
