# 图件索引

## 当前主图（14 个模块）

来源：2026-10-22 整理时用户指定的 `figrues-new/` 导出项目。
以原目录和显示名称为准确定图号，统一目录、项目清单与 `PLOT_META.id`。
图形设置、内嵌数据和绘图逻辑保持不变；下表保留原始 ID 供追溯。

| 图件 | 当前模块 | 导出项目原始 ID |
| --- | --- | --- |
| Figure 1b — Merged author composition · Original ratio | [`fig-1-b-author-composition`](../figures/plots/fig-1-b-author-composition/plot.py) | `figure1b` |
| Figure 1c — Annual active-role shares · Direct labels | [`fig-1-c-active-role-shares`](../figures/plots/fig-1-c-active-role-shares/plot.py) | `figure1c` |
| Figure 1d — Common-window career-age density | [`fig-1-d-career-age-density`](../figures/plots/fig-1-d-career-age-density/plot.py) | `figure1e` |
| Figure 1e — Historical JCR last-author composition | [`fig-1-e-historical-jcr-last-author`](../figures/plots/fig-1-e-historical-jcr-last-author/plot.py) | `figure1d` |
| Figure 2b — Extension · 独立子图 | [`fig-2-b-extension`](../figures/plots/fig-2-b-extension/plot.py) | `figure-2b-extension-standalone` |
| Figure 2b — Foundation · 独立子图 | [`fig-2-b-foundation`](../figures/plots/fig-2-b-foundation/plot.py) | `figure-2b-foundation-standalone` |
| Figure 2b — Generalization · 独立子图 | [`fig-2-b-generalization`](../figures/plots/fig-2-b-generalization/plot.py) | `figure-2b-generalization-standalone` |
| Figure 3a — Chaperone paper routes | [`fig-3-a-chaperone-routes`](../figures/plots/fig-3-a-chaperone-routes/plot.py) | `figure3a` |
| Figure 3b — Top 10% Foundation share by route | [`fig-3-b-top10-foundation-by-route`](../figures/plots/fig-3-b-top10-foundation-by-route/plot.py) | `fig-3-e-point-top10-foundation-by-route` |
| Figure 3c — Outsider-author share | [`fig-3-c-outsider-author-share`](../figures/plots/fig-3-c-outsider-author-share/plot.py) | `figure3c` |
| Figure 3d — Global-normalized citation entropy | [`fig-3-d-citation-entropy`](../figures/plots/fig-3-d-citation-entropy/plot.py) | `figure3d` |
| Figure 4a — Citation audience amount | [`fig-4-a-citation-audience-amount`](../figures/plots/fig-4-a-citation-audience-amount/plot.py) | `fig-4-a-point-citation-audience-amount` |
| Figure 4b — Raw and adjusted reward probabilities | [`fig-4-b-reward-probabilities`](../figures/plots/fig-4-b-reward-probabilities/plot.py) | `4b` |
| Figure 4c — Origin-normalized · Leadership routes | [`fig-4-c-leadership-route-impact`](../figures/plots/fig-4-c-leadership-route-impact/plot.py) | `fig-4-c-point-pivot-impact-leadership-routes` |

新版提供 Figure 1b–1e、Figure 2b 的三个独立子图、Figure 3a–3d、Figure 4a–4c。
Figure 1a 为此前 README 说明的概念分类图；新版导出中未提供 Figure 2a、2c 等其他模块，不以旧图补齐。
原 Figure 1d/1e 的内部 ID 对调，原 Figure 3b 的 ID 仍含 `3-e`，现均已与显示图号统一。

## 补充图（9 个模块，沿用原版）

新版导出未包含补充图更新，以下模块保留原有内容和编号。

| 图件 | 模块 |
| --- | --- |
| Figure S1a — Annual author counts | [`fig-s1-a-line-author-absolute-counts`](../supplementary/fig-s1-a-line-author-absolute-counts/plot.py) |
| Figure S1b — Annual active-role counts | [`fig-s1-b-line-annual-active-role-counts`](../supplementary/fig-s1-b-line-annual-active-role-counts/plot.py) |
| Figure S1c — AI4Sci-active inflow composition | [`fig-s1-c-line-role-transition-inflow-composition`](../supplementary/fig-s1-c-line-role-transition-inflow-composition/plot.py) |
| Supplementary — Home-subfield reception | [`fig-s2-scatter-home-subfield-reception`](../supplementary/fig-s2-scatter-home-subfield-reception/plot.py) |
| Supplementary — F/E/G window sensitivity | [`fig-s3-line-feg-window-sensitivity`](../supplementary/fig-s3-line-feg-window-sensitivity/plot.py) |
| Supplementary — Origin tie sensitivity | [`fig-s4-line-origin-tie-sensitivity`](../supplementary/fig-s4-line-origin-tie-sensitivity/plot.py) |
| Supplementary — AI Specialist entry routes | [`fig-s5-area-ai-specialist-entry-routes`](../supplementary/fig-s5-area-ai-specialist-entry-routes/plot.py) |
| Supplementary — Abundance-normalized collaboration | [`fig-s6-line-abundance-normalized-collaboration`](../supplementary/fig-s6-line-abundance-normalized-collaboration/plot.py) |
| Supplementary — Citation-audience composition | [`fig-s7-bar-citation-audience-composition`](../supplementary/fig-s7-bar-citation-audience-composition/plot.py) |

## 旧版追溯

旧主图的 24 个模块及整理前的 README 均已核对，与 Git 提交
`b426f365dc813de9f77fa5a6aa92e0bca3adc0f6` 中的内容完全一致。
本地归档副本已删除；可在该提交的 `figure1/`–`figure4/` 中查看或恢复旧版。
旧图号不代表当前稿件图号。

例如，查看该版本的仓库说明：

```bash
git show b426f365dc813de9f77fa5a6aa92e0bca3adc0f6:README.md
```
