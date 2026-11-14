# 明代灾荒与进士科考（1521–1619）

**1° 格网 × 114 年面板：5,736 条灾荒记录与 2,841 位进士。**

[在线图册](https://charles-delapore.github.io/ming-famine-jinshi/) ·
[交互地图](web/interactive_map.html) ·
[English](README.md) ·
[技术说明](docs/project_notes.md) ·
[引用](CITATION.cff)

![概览](figures/fig3_framework.png)

## 概述

灾荒历史能否预测明代科举的成功者？本项目把 5,736 条灾荒记录与 2,841 位一甲/二甲进士放到 1° 格网 × 114 年面板（1521–1619）上，考察灾荒与进士产出的时空关系。

## 主要结果

- 灾荒带与进士核心区只部分重叠。
- 灾荒→进士的 Granger 因果在 **48/135** 个格网通过 FDR；多尺度模型在 1–5 年找到 **8** 个显著格网，6–10 年与 11–20 年均为 **0**。
- GWR 在 **123/159** 个格网局部显著；灾荒强度是最强因子（**q = 0.337**）。

## 方法与技术栈

Python 3.13 · GeoPandas · PySAL · mgwr · statsmodels · scikit-learn · Matplotlib。格网 Granger（FDR）、多尺度 LASSO/BIC、GWR/SDM 与地理探测器。

## 数据与引用

灾荒：胡鹏《明代灾荒数据库》；进士：CBDB；底图：CHGIS v6；气候：Mann et al. 2009、Schneider et al. 2015。原始数据不随仓库分发。

引用本仓库与上述数据来源，详见 [CITATION.cff](CITATION.cff)。

## 许可

代码采用 MIT 许可；历史数据仍受原始条款约束。
