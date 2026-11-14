# Derived tables

这些文件只含**聚合计数、系数或网格级汇总**；不含 CBDB 个人记录、姓名、地址或坐标。

## 公开（随仓库发布）

| 文件 | 内容 |
|---|---|
| `a1_rank_coefficients.csv`, `a1_rank_units.csv` | A1 秩次份额模型系数与格网×科年单元 |
| `a2_spillover_coefficients.csv`, `a2_spillover_units.csv` | A2 空间溢出系数与单元 |
| `a3_main_results.csv` | A3 主结果表（脚本 → 表 → 文档） |
| `a10_*.csv` | 坐标置信度敏感性、层级、晚明地理、外部城市对照 |
| `a12_full_ming_cities.csv`, `a12_full_ming_fixed_lag.csv`, `a12_full_ming_lag_window.csv` | 全明复制的城市汇总、固定窗与滞后窗结果 |
| `a13_admin_density_dose.csv` | 行政密度剂量反应 |
| `a14_network_coverage.csv` | 网络覆盖审计汇总 |
| `a15_external_famine_summary.csv`, `a15_external_famine_crosscheck.csv` | 外部灾荒对照的汇总（不含逐条年表） |
| `a17_cbdb_network_coverage.csv` | CBDB 全图覆盖审计 |
| `a18_ego_network_summary.csv`, `a18_grid_correlations.csv` | ego-network 汇总与网格相关 |
| `a19_early_ming_decomposition.csv` | 早明分解 |
| `jinshi_by_year_1521_1619.csv`, `jinshi_rank_summary.csv`, `jinshi_unparsed_summary.csv` | 进士年度/秩次/未解析汇总 |
| `long_tail_*.csv` | 长尾诊断：滞后窗、固定窗、置换零分布、队列探针 |
| `p0_3_*.csv`, `p0_3b_*.csv` | P0-3 敏感性、双代理、时间扰动、记录偏差 |
| `p1_1_*.csv` | STL 对照与特征重要性 |
| `v03_model_summary.csv` | v0.2/v0.3 Granger、GWR、多尺度、GeoDetector 汇总 |

## 不发布（本地私有）

| 文件 | 原因 |
|---|---|
| CBDB 个人-地址链接 | 个人级标识 |
| 晚明进士 1627–1644 明细 | 个人级记录（姓名、坐标） |
| CBDB 地址字典、CHGIS 县点 | 第三方数据库批量内容，再分发许可不明 |
| 外部明城/明面 GeoJSON | 第三方集合，来源许可未确认 |
| 全明灾荒事件表与面板 | 外部灾荒数据，许可未确认 |
| 网络边表（PersonID + 关系） | 个人级关系数据 |
| ego 度表（personid + 度） | 个人级标识 |
| 外部灾荒逐条年表 | 大段原文与来源，许可未确认 |

## 重建

```bash
set MING_JINSHI_RAW=<path to the private CBDB export>
python scripts/make_jinshi_aggregates.py
```

进士数据来源：China Biographical Database (CBDB)，`入仕查询结果` 导出。
其他来源与许可见 `docs/data_provenance.md` 与各 A 系列文档。
