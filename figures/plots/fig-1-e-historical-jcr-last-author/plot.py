"""Matplot Studio figure for Figure 1e."""

from __future__ import annotations

import base64
import zlib
from csv import DictReader
from io import StringIO

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd


PLOT_META = {
    "id": "fig-1-e-historical-jcr-last-author",
    "name": "Figure 1e — Historical JCR last-author composition",
    "description": "AI-origin last-author shares by lagged historical JCR quartile.",
    "version": 1,
    "data_mode": "inline",
    "data_note": "The exact 108-row by 10-column plotting table is embedded as zlib-level-9 compressed, base64-encoded CSV. AI4Sci journals are assigned the JCR quartile available one year before publication. AI-origin shares use AI- plus Domain-origin classified last-author positions as the denominator. Lines show 5-year EWMAs for 1998–2024; journals without a valid historical JCR match are excluded.",
    "data_export": {
        "csv": True,
        "json": True,
        "note": "Exports the complete embedded calculation table used by the figure.",
    },
}

PLOT_SCHEMA = [
    {'path': 'layout.mode', 'label': '布局模式', 'group': '坐标轴对齐', 'type': 'select', 'default': 'auto', 'options': [{'value': 'auto', 'label': '自动布局（原外观）'}, {'value': 'fixed', 'label': '固定边距（用于对齐）'}], 'required': True},
    {'path': 'layout.left_mm', 'label': '左边距 / Y 轴位置（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 16.404167, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.right_mm', 'label': '右边距（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 3.81, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.bottom_mm', 'label': '下边距 / X 轴位置（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 13.370932, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'layout.top_mm', 'label': '上边距（mm）', 'group': '坐标轴对齐', 'type': 'number', 'default': 4.837327, 'min': 0, 'max': 100, 'step': 0.1, 'required': True},
    {'path': 'axes.main.x_label_pad', 'label': 'X 轴标题间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 4, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.x_tick_pad', 'label': 'X 刻度文字间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 3.5, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.y_label_pad', 'label': 'Y 轴标题间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 4, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},
    {'path': 'axes.main.y_tick_pad', 'label': 'Y 刻度文字间距（pt）', 'group': '坐标轴文字间距', 'type': 'number', 'default': 3.5, 'min': 0, 'max': 40, 'step': 0.5, 'required': True},

    {"path": "figure.size", "label": "Figure size", "group": "Figure", "type": "number_pair", "default": [2.45, 2.15], "min": 1.5, "max": 12, "step": 0.01, "required": True},
    {"path": "figure.facecolor", "label": "Background", "group": "Figure", "type": "color", "default": "#FFFFFF", "required": True},
    {"path": "axes.main.x_label", "label": "X-axis label", "group": "Axes", "type": "string", "default": "Publication year", "required": True},
    {"path": "axes.main.y_label", "label": "Y-axis label", "group": "Axes", "type": "string", "default": "AI-origin last-author share", "required": True},
    {"path": "axes.main.x_range", "label": "X-axis range", "group": "Axes", "type": "number_pair", "default": [1998, 2024], "min": 1998, "max": 2024, "step": 1, "required": True},
    {"path": "axes.main.y_range", "label": "Y-axis range", "group": "Axes", "type": "number_pair", "default": [0.20, 0.50], "min": 0, "max": 1, "step": 0.05, "required": True},
    {"path": "axes.main.spine_width", "label": "Spine width", "group": "Axes", "type": "number", "default": 0.6, "min": 0, "max": 3, "step": 0.1, "required": True},
    {"path": "axes.main.tick_length", "label": "Tick length", "group": "Axes", "type": "number", "default": 3.0, "min": 0, "max": 10, "step": 0.5, "required": True},
    {"path": "series.q1.color", "label": "Q1 color", "group": "Series", "type": "color", "default": "#440154", "required": True},
    {"path": "series.q2.color", "label": "Q2 color", "group": "Series", "type": "color", "default": "#31688E", "required": True},
    {"path": "series.q3.color", "label": "Q3 color", "group": "Series", "type": "color", "default": "#35B779", "required": True},
    {"path": "series.q4.color", "label": "Q4 color", "group": "Series", "type": "color", "default": "#FDE725", "required": True},
    {"path": "series.ai.linestyle", "label": "AI-origin line style", "group": "Series", "type": "select", "default": "-", "options": ["-", "--", ":", "-."], "required": True},
    {"path": "series.linewidth", "label": "Line width", "group": "Series", "type": "number", "default": 1.25, "min": 0.2, "max": 5, "step": 0.05, "required": True},
    {"path": "annotation.q1.text", "label": "Q1 label", "group": "Curve labels", "type": "string", "default": "Q1", "required": True},
    {"path": "annotation.q1.year", "label": "Q1 label year", "group": "Curve labels", "type": "integer", "default": 2012, "min": 1998, "max": 2024, "step": 1, "required": True},
    {"path": "annotation.q1.offset", "label": "Q1 label offset", "group": "Curve labels", "type": "number_pair", "default": [4, 6], "min": -50, "max": 50, "step": 1, "required": True},
    {"path": "annotation.q2.text", "label": "Q2 label", "group": "Curve labels", "type": "string", "default": "Q2", "required": True},
    {"path": "annotation.q2.year", "label": "Q2 label year", "group": "Curve labels", "type": "integer", "default": 2015, "min": 1998, "max": 2024, "step": 1, "required": True},
    {"path": "annotation.q2.offset", "label": "Q2 label offset", "group": "Curve labels", "type": "number_pair", "default": [4, -6], "min": -50, "max": 50, "step": 1, "required": True},
    {"path": "annotation.q3.text", "label": "Q3 label", "group": "Curve labels", "type": "string", "default": "Q3", "required": True},
    {"path": "annotation.q3.year", "label": "Q3 label year", "group": "Curve labels", "type": "integer", "default": 2014, "min": 1998, "max": 2024, "step": 1, "required": True},
    {"path": "annotation.q3.offset", "label": "Q3 label offset", "group": "Curve labels", "type": "number_pair", "default": [4, 4], "min": -50, "max": 50, "step": 1, "required": True},
    {"path": "annotation.q4.text", "label": "Q4 label", "group": "Curve labels", "type": "string", "default": "Q4", "required": True},
    {"path": "annotation.q4.year", "label": "Q4 label year", "group": "Curve labels", "type": "integer", "default": 2019, "min": 1998, "max": 2024, "step": 1, "required": True},
    {"path": "annotation.q4.offset", "label": "Q4 label offset", "group": "Curve labels", "type": "number_pair", "default": [4, 4], "min": -50, "max": 50, "step": 1, "required": True},
    {"path": "annotation.font_size", "label": "Curve-label size", "group": "Curve labels", "type": "number", "default": 7.5, "min": 4, "max": 16, "step": 0.5, "required": True},
    {"path": "annotation.font_weight", "label": "Curve-label weight", "group": "Curve labels", "type": "select", "default": "bold", "options": ["normal", "bold"], "required": True},
    {"path": "typography.font_family", "label": "Font family", "group": "Typography", "type": "string", "default": "Arial", "required": True},
    {"path": "typography.label_size", "label": "Axis-label size", "group": "Typography", "type": "number", "default": 9, "min": 4, "max": 20, "step": 0.5, "required": True},
    {"path": "typography.tick_size", "label": "Tick-label size", "group": "Typography", "type": "number", "default": 8, "min": 4, "max": 20, "step": 0.5, "required": True},
]

PLOT_SETTINGS = {
    'layout.mode': 'auto',
    'layout.left_mm': 16.404167,
    'layout.right_mm': 3.81,
    'layout.bottom_mm': 13.370932,
    'layout.top_mm': 4.837327,
    'axes.main.x_label_pad': 4,
    'axes.main.x_tick_pad': 3.5,
    'axes.main.y_label_pad': 4,
    'axes.main.y_tick_pad': 3.5,
'figure.size': [2.67, 2.4],
 'figure.facecolor': '#FFFFFF',
 'axes.main.x_label': 'Year',
 'axes.main.y_label': 'Percent of AI-origin last authors',
 'axes.main.x_range': [1998, 2024],
 'axes.main.y_range': [0.2, 0.5],
 'axes.main.spine_width': 0.6,
 'axes.main.tick_length': 3,
 'series.q1.color': '#440154',
 'series.q2.color': '#31688E',
 'series.q3.color': '#35B779',
 'series.q4.color': '#FDE725',
 'series.ai.linestyle': '-',
 'series.linewidth': 1.25,
 'annotation.q1.text': 'Q1',
 'annotation.q1.year': 2003,
 'annotation.q1.offset': [4, -6],
 'annotation.q2.text': 'Q2',
 'annotation.q2.year': 2015,
 'annotation.q2.offset': [4, -6],
 'annotation.q3.text': 'Q3',
 'annotation.q3.year': 2020,
 'annotation.q3.offset': [4, 4],
 'annotation.q4.text': 'Q4',
 'annotation.q4.year': 2019,
 'annotation.q4.offset': [4, 4],
 'annotation.font_size': 7.5,
 'annotation.font_weight': 'bold',
 'typography.font_family': 'Arial',
 'typography.label_size': 9,
 'typography.tick_size': 8}


def _resolved(settings):
    values = {field["path"]: field["default"] for field in PLOT_SCHEMA}
    values.update(settings or {})
    return values


_DATA_ZLIB_BASE64 = (
    "eNqNmm9uZTluxb/3KrIAYSBRfyjtIF9nBQ2jpzKpoKc76BogyO7nd8hr+xVSCtp+dV1+vu9SEsnDwyP975e3P8q3//7yy9f/+PrL2z+//v5b+a9f"
    "/ii//fz2lcvffv/H29ff+M8vv759+8YtX/5W3r7+HPe//fr12z9//vafb398KXnf/33/B/f+/OV//vE2b5/Iv/7Uztnl33n39z8Y1a//9uvb3/+O"
    "6b+20vYpfZ0y5y71L71vr2e5j3b6HHprrWandrO56xqz/bm7rhattN5L811607OG+Zrmnd/28VYX7023PtzW2rtVO3/urqvFXvosZ5QWTzJvHet2"
    "xvS+Ructt722Na9z2Opz/bm7rvZG8VrcSxuukftqp35eY+TWdz2f1z95myyeH3vRei1jnrL2Cf/03bzZsnXOXDGOhYe2be/eax19xW1efW/z2peZ"
    "1Rm32bHW3M7q7rtdbVpZuHHVYqbVsW2zNWvVl+ElTcmbj719H+uOkyJw/JhjajIaj4BbVt2cSGLMNuxqrpdDrNoqeEDLlYH3EYdDy5WR9x6IMUOr"
    "a/VxjtXd+oxZLz+9r1mrn7bXWFeTo6xW9nr3YxtnzbNXJyam77Q4ax+19UVQDDPdpr9ZZwysh/Mn3cbfmi/GyoL0n6zWesnFM8sgF9fS0+305fy6"
    "/cy2qwbhdXWbvTarY7MEMUVbrPoetjXLHjP0zi9tkihM8lwtkos43aqVHo/vwypjGP04s2TB9LDpZ9cxVzVmuWNV8eYca03Sbux0Iz4fs/dBds6G"
    "H28me2Hl2iRsuubYJx8Y71fF7ho8dX5cE2464eGbkbCIa2acLoLIMFVZ7D6vBkcZrWDvBNhMHHU+r5Flr2+MM+O2UUk6i0kej5vmITU95kh0yVy7"
    "pCJjZhkAgaqxV4bIyN+v4Z/z8oblkrY5CUnskcEnwnSPQeBirzf+cLdoZXugOBCZTyLY+mmdLB8ZpzyLoFx1L9BgRpySFIuIHZUIBk5zTfn/dJ+H"
    "v+3T/WqyKzNa3eR/wM2qZxCqc+KQXi3i4dRJqI6B3wChDK4FtAHae4KrY2VwdaCNkZNkuONqkVwkEYF9kEnP2t2tHmxhY+5ASzDT/NR1nKGMQKDR"
    "Kxl7mIq1AxrJkeuQsLVy767goSzaxZEUNkYKlEdu6Anr5RrryiP65zVuE7CRME3O9hZ3gWyNvMLc5LNXk6QjvlH84PTMs9fXyDx7fcXAJg5nVqeZ"
    "UDFWf+Bv5l43Y6l+NYgfT5TFdmLsY79+Z0i0777jrqGScgiUtpvlXWDGBEdYskaGXg3iRitnR92QFz0+nQ8Z+K9TzfUMnGORdvh5UfVlSj7Ug/vF"
    "W9NIOy8EVAwSHwvxm59DMYu0A2WOEH9reOEaHLM7sN73IISpvIGe1BBgfbVJDDe72sRdRAjVrFBHNQF9OIocOT8AagdTVmQbRXVPyo8bGNP39ZE9"
    "eIOKarqW4QFL5IaKlmXKMDxwihxScYsFpNrXuiniDqA8eAxYgfxLNXUTiFeLI5mKYCtCgKRtLJ2yBa6VgLwgCecQ5FNUS3cpZ8ntAceg7MyYuXIb"
    "CJhwDBE0WRw/dhUIWvAq+RzlsUOmtDTAw1JhC1/BubSCeJMoOVnL9+h7sRTQGshYhI63uVpnKaA10MOrUXwFEhqxMYKuAI2HufDkBVmosYxAY4Ve"
    "UlA6pCKLK+swTxPROJCa5A8sxKhbRKPCas7V5uNMkbNYWqoUuAe3WsK6WNr8LxQs/mRZ68gqkCJI5rGRtY63AJTgou1qcJRdCySMdLZMqNevJ59e"
    "v/TwAYYSllCh45CkWGpqHvhIHgKwkKRIgfljXw4T6ZTZGnkHR9bSMi/At7XMb0BxKhsJoJMEFfwAIpsGAU9JaANAwMgdY91jXo0KJjF4Kh3EAyOv"
    "zchISHltRiJ8ToXhMtmsOcF3qFtO2gPoqk3zPk9iFd9Hq/Rg1RY+9PdrksGXN5LAd35AyY4Cl4gJk5Suw7uKWwLrPst0JpHzJCaB6kaKVZXtp8bi"
    "HicTj6p2IjiIJYwROWQMmZcEFkgkCsnIohisH/uS8g9NaoKD5GY8izgENCG6M8onlcUUh4ArN0Wq9imUZJRbIDojzhbIt9U+NIHoGFej+JKOEsgo"
    "I5METKFpmDt/JkeYai1Ge34GwmKTDoX7XHkSCItJGhnuMzn4alGuVNMCDGUvy4deXzPh+vUVUEwcEVNaBubpWfYIN0KPJWFcs19NQnjhgg2YtIBK"
    "MI0FdMZOGHi2zxASuhTGTrColAX2EEsGzd2V/DkJPcSWw4Yp2D1R3S++JCaJcnx5Rg4flowzOsR2Zw/F8KnVOG1BbdWQh8srRAKwB+JszMflPIgK"
    "A7Pn5Vejqof02sQmDCEAr8Eo8AiTIzkz/GGD5OOerAHZmWFGQOE2Vwrq7rBpIiCQAPoQis7VprwJfXES82F8qj3CrB68L2CdEtWBNkgmDoqQ3WIT"
    "oO9UZVtB0ppIBxg9VP8SZP3iTKgoFaf0SDkGTmorKyhjPCFh1pTbUgwGq7ACZmGdTO8IHCEIgbKAIbOrwkbAUiYvIg2sEYQdmukOyMO9h4wJyuVP"
    "mZ5qaFoQM0tnDuyzqoDeg3dgYVd2AHnjZBdzEWl4bOH58LXA62MLZCeTxQJrsNNVvYPsZwpzd5boaF6muA9gHL3bUvfSh7gPYHzuk0yIJexgUw92"
    "eiUhcNIhSTLfWFfSBifREM3kWkfRQ3MKOM54a7EoW7TOAUdg5GoRT2KJ7hns8ayE2KHlgiJ08cGshOQs9Xb6yhzkF3G5MSgtapJmelKUb04qkJop"
    "mbwINTCWIqJO/WqW6AknANJn/siMA2goF+BD/EhexuyoqkIc+H7yMgCYoipgGvtqU3SA9ABeZ5JKHkAXBjaTJuRDoidFghCmcZGskIAnzYl5q7Wz"
    "k+svaYrlUWvn2VdcxBp8V9TZjsdLRhtS4VLELI10TBJzB1rM8ClUNdJSNdygzrAOykYODJRwqDPkBJecq0mwlY6BWVHFIi1JLOrZB9LKS0KX84G0"
    "6+k5nKiixQNq59NxEBISqUDaoATtotaQZ9KGJpZnzdr1/VcWr9ev9V4vIXbgICay11e5hIQCl4yjzqtRdYe18NHyMP/2/Vd0m999nbRIzPAJ8chT"
    "M3gO5ZI0DboZ2NMueg1LBRLUMk/GK7e/vFKx2efzdTLGgCEROSLaco5UTzPxPdbNoz9o9ebJGjxrRtYTG99xn8i377hPwrCEREKnSasaga9baiOh"
    "ow4FOJHFi2ZDYALr6oL6yXUdWx2O7O6VKwbjV4Mjuy2hn5wCbLpEmxVSYjZeYNKSbNPhz341ahGs1KZykjlXSTYv/0IokmTz8S+lXVXySu8iBOwx"
    "sijkwC1YMf4fiz2oZKe7zCUj3Qh/8RvwYKcCRNTTSQG8LHTLKu5daUTcEUCsSty1lEa+1ZNmilxEG0EAnJRojWwzOq113q/ho5ffdQ1PMg06wSFp"
    "bAcrnOJENIKwL/USopPtItrsUKV4kOIlSMhSoEm7XeKyqY/iIoKiikjNFAK6AF0VCnQC3mJZhefUMerXTIBtF9nGNEUefUJ+Bbyq0OQIsFbEE+AF"
    "rxOe62l1vuu2Ek1ZCLqi9a7bSlqFlcEH5tUingQCYI+FyIvyjC8+X0kV8djLK1hPk1rWNFfSPluzLbFsa66Ag18tpiupBKRKQvUhAispaRIiEtAr"
    "EXhISZdekaSHWg5foKskgLMDhVBLJd5VEmXotu2i6IBVtFwqJM+uhqpw8AppXcnaVKzxGh1D3Y/yQ0iKzarlWll+InC3RcsFKVpXm9LBH7tqMXHl"
    "SokKphPVgSEskWYBtZ/zDKGLWwvOLYG033ahTqEBLifZmTytqAOiBCPj6ZSHwg4kE4yk0gldbpQlxl+f5pbwoAFtapOB3KvJESbxbtmJpFLrgUkY"
    "2TySEyIBJS8xJOqB9NBIwOqKXRKNcIlWc2pvgdjdXVRMBi/Sjsi3apR29zL/wCttX7GQrubJH8DSNheLSrV/Nmq2kkZMGki0FEeakkZEGlIf2k67"
    "aDtDegAfVwMyIwNx3Ocldu/EVl8u4cwayoqfToeT+EfPoIpokDjI7rraxJt0kTDDskP7w1kwv093Zj4Qtx/eTJ/DsLTTNiRGtMfnMDH4B6BB5h67"
    "mtRGBuyG5UqCJjGsSx4TwU5FQFrYkoomGu4nN07hP9BlAlds74TLMQOpJnBF9gJNL+pOkyfpbpnuSgwhCggWEnoJr3PNoMRQR7oCoXhiW5XSinun"
    "KGWqvH6kyBIGQ9RzXq2qsZI2WLVTHOiJPZcuyIpR8mMO2DOWTHISQB+lBArb1d5o22GDDyO8DhegMmt3Aii5T7WzuAcM/xSypF64+lRTjVtPdcSs"
    "+lkXD89OEmYlqVQSEsEahYOq4dJKJTW1rI8XiYeWoywJdjV1jaNmm2KhbS3qecqNasqpKdr+SvkVuIHSm3CAfMltQFCJFt0FFyRM7DK2i8xDTyVM"
    "Bb169r4SkrWJOJSVK+iz9GZtIk4lb0/mB+ugVuAGHP/hU3CR0sFouMmvRg3K0WVYO1VJlqtk+c/XQ3cY2scra+mRrLwpS97aTp9Wqc/t0AhKwr0a"
    "JWhZWtUO7QUkW2bFPq65g7O/ezf1CHHcKYw96+ECQCe/DUExhWtebcqlqyzJPbU+JRC2RUMe2+zuKa/yPFA3t9lz27hKDwkxhi47jzccySah2ZAu"
    "J7DoIvY0UFNYzzI/QEPLS/sGDBxtDj+7jgcXC/yrdocfmqtxGGxVW8Uzaa6G65BabSj71SqoG2cqlKYrGL4RDA4VVfe6VippTsyQik1dLmCVtzGt"
    "6NChBEkdWBkLFQj86rCgq1Fc6laonOqhI4z06aTiXWcbTI2daEdS8aUzEGQywzr3p6pO4jTI8fEUy8i4LsmLbO9ZGIB2uJw2VRw8icUjMsFuVoGc"
    "cUtJhDVXgE/ljKtbbbdjN2L4kvK02e8BcmIU5FaVnpRbUdpeod+lTZae9OCvlAluYEktq+kZsVFF+QY75rwaJRdcW30e9FFRR8TVKHdToZknDAZe"
    "UlEcisyTRzu6AlXi33lHJToHBbREwgoq2dVoj3XNMNnBqQgDzI73azZNn7/r+hwx8i31Tydi1vsRI2vKSB2Iybp1EXbU5Kg6tYe2RT1OGR3equq0"
    "VBJ3cA8qGbVBxFw10YLC3Y7ZgHPFRffFqXNx1AIqaXQCJuDZowNUaukETPTDFp5dWqqlgw3JSGrAJktKPmbQXwScoypMZirHw+hUDxq7F3JDS8ep"
    "VY1djnBXHGJiZtp8UP8zax5iYgG0+aD2B3p1Ndrp96VZx/mQ9yqsiGjaa54655NlWIGztdkMqe+5T+4SrZnekkDQc5/cpFqzDHEw5WoV+DxeICYw"
    "uUdTeehxUinLMwPJjpNwPQcQXLscMkAsp1PFWBmJ9J8RyW8XHaerqgoci57acqpAFi9SmYTvOVOQjRcJ//BkskN8c4hS62jPc0BnQzmmKDXBsq9m"
    "tfExW6GjqWIAYVWBfXT0Ai9bYphwWPyuqSjkPqgJMJJWQsF6NIAuHTDZJxwsGmS7yDlgCh6lXlgewFLQqoNSFdfRorSq9uJog6fqBFJGsIbUoXVV"
    "7VsGMCOyVUXTGODV6KDtUWvQdfIn9ZWPFiedmCLY/s7XWYoVXeDd0Gm8Z2dAQQjeTZ3GU1W0i6jTPUp/7mjlaRzT8RYdW2I5CedwrERXHVti1VvK"
    "97i/A80UA9Gr3JDG/2AmXfUUvYrEsZuuo1ByNY46lxWpI9SheOiIm/a4w2OADiVG5+BIivCE/itSLZFAJ3XiNgGsXAtY9HqfrhizaN1RUGW/bwod"
    "4Xa0VDWtCmqqFA5v2SAEh4J+6lxbpjQ4fSC+OtMGCb9aHMxR1MO1r57uChrMTKHgJEnWYLFgZgoDf0StHuq2tpu7ylWezJAIrt1mFniE1GJ222/W"
    "ulqPrfWPKgaFOSFezzyjQhWDwtTQuEduCYMOLfa6lR8zu3phqra6SSPt4FzNqsMMUUDyY3vkRcsZiA1oz7qnUzUDOMPQ1nZmK9joopPkSs1zkRJ8"
    "TGySjDpB1e0i8zQdru2SwmeevLXYTY6DLFJRkj3FdnIceJHYkhGs/XAMHgl5JzpxKoaEap4mvS/T9aL1iCKo5VKXkAeR8I3rYVJQUoSAvcFKJFoT"
    "xLnbLX09TkUMte4r01WbtDo9MdXhh9GL3AOL2WrgmRNUO1ixtGNiRHjgD3uUdkyMCDZsJVUwCrja/CZNEv+nJ2gmXEc2pFHudbWLa/Vg1gZgar4S"
    "/7WjJWxySYmRTHpwEzThAdYiMkc7VPh2aMd0PWa3gJIw1HmcDOSLGqRTfhIjio5p6GlyDBSC76oThuEyORAOwbc6gPCsGLUOYsKFJGtHGEO8dV5z"
    "y63zXI2OInxjTcjYlbKn+DbcBQZL6OR+/hItV7yzdABgHhQ+KvHaPQUWHp27igkAStx94uSejdtW9LQgEYqnETjEQupsI2DXpChk8hztUwzAbktS"
    "CM/qUO3WxgFAYdGXS0QCutQ9DlalX+2a9vcJqKbNUHjMyEXuYjFx6qeltOXS7rXxTxBBoLMkWii1uBHiknrD8NBzWSMRaLuaVc5iUAehysrjuDod"
    "cOLAiAIj4Sk22nQcQ9uGiSYjtD9tgG17SsQMiVAbYC2aCbsd+5GEsCk1wqQ8dBpKyX6EkzxzmkpJCiePNK4jExQbFbxUjUEwHXMg66h31n/6F9sI"
    "Ln8="
)


def prepare_data():
    """Parse and return the complete CSV embedded in this module."""
    csv_text = zlib.decompress(base64.b64decode(_DATA_ZLIB_BASE64)).decode("utf-8")
    integer_columns = {"year", "n_ai", "n_domain", "n_classified"}
    rows = []
    for row in DictReader(StringIO(csv_text)):
        rows.append(
            {
                key: int(value) if key in integer_columns else value if key in {"specification", "jcr"} else float(value)
                for key, value in row.items()
            }
        )
    return pd.DataFrame(rows)


def _apply_axis_alignment(fig, ax, config):
    """Keep the original auto layout, or place axes at physical canvas margins."""
    ax.xaxis.labelpad = config["axes.main.x_label_pad"]
    ax.yaxis.labelpad = config["axes.main.y_label_pad"]
    ax.tick_params(axis="x", which="major", pad=config["axes.main.x_tick_pad"])
    ax.tick_params(axis="y", which="major", pad=config["axes.main.y_tick_pad"])
    if config["layout.mode"] == "auto":
        fig.tight_layout()
        return
    width_mm, height_mm = fig.get_size_inches() * 25.4
    left = config["layout.left_mm"]
    right = config["layout.right_mm"]
    bottom = config["layout.bottom_mm"]
    top = config["layout.top_mm"]
    if min(left, right, bottom, top) < 0 or left + right >= width_mm or bottom + top >= height_mm:
        raise ValueError("固定边距无效：左右边距之和须小于画布宽度，上下边距之和须小于画布高度。请减小边距或增大画布。")
    fig.set_layout_engine(None)
    fig.subplots_adjust(left=left / width_mm, right=1 - right / width_mm,
                        bottom=bottom / height_mm, top=1 - top / height_mm)


def render(data, settings):
    """Render and return one Matplotlib Figure without external I/O."""
    config = _resolved(settings)
    colors = {q: config[f"series.{q.lower()}.color"] for q in ["Q1", "Q2", "Q3", "Q4"]}
    fig, ax = plt.subplots(figsize=tuple(config["figure.size"]), facecolor=config["figure.facecolor"])
    ax.set_facecolor(config["figure.facecolor"])
    for quartile in ["Q1", "Q2", "Q3", "Q4"]:
        subset = data[data["jcr"] == quartile]
        ax.plot(subset["year"], subset["ai_specialist_share_ewma5"], color=colors[quartile], linewidth=config["series.linewidth"], linestyle=config["series.ai.linestyle"])
        key = quartile.lower()
        label_year = config[f"annotation.{key}.year"]
        label_values = subset.loc[subset["year"].eq(label_year), "ai_specialist_share_ewma5"]
        if not label_values.empty:
            ax.annotate(
                config[f"annotation.{key}.text"],
                xy=(label_year, float(label_values.iloc[0])),
                xytext=tuple(config[f"annotation.{key}.offset"]),
                textcoords="offset points", ha="left", va="center",
                color=colors[quartile], family=config["typography.font_family"],
                fontsize=config["annotation.font_size"],
                fontweight=config["annotation.font_weight"],
            )
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
    _apply_axis_alignment(fig, ax, config)
    return fig
