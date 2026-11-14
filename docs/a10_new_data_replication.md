# A10 — new-data replication and external cross-checks (2026-11-14)

- Generated: 2026-11-14 17:29
- Command: `python scripts/a10_new_data_replication.py`
- Sources: `docs/a9_new_data_inventory.md` + externally downloaded `a9_external_ming_city.json` (GitHub `ChenSK23/GIS`, contents API).
- **Descriptive only**: no new causal model, no new control variable, no headline change.

## 1. Late-Ming out-of-sample elite geography (1627–1644)

| Quantity | Value |
|---|---:|
| rows in late table | 1,950 |
| rows 1627–1644 with parsed rank + coordinates | 1,842 |
| late grids | 197 |
| v0.3 panel grids | 291 |
| union grids | 296 |
| Pearson r (grid Jinshi counts) | 0.865 |
| Spearman r | 0.837 |
| top-20 grid overlap | 14/20 |
| top-20 Jaccard | 0.538 |

The famine series ends in 1619, so this is **not** a famine→Jinshi test. It checks whether the *spatial inequality* finding (Jiangnan core, partial overlap with famine belts) persists after the study window. Raw `EntryYear` extends to 1871, so the 1627–1644 filter is applied explicitly.

## 2. External CHGIS Ming city points — cross-check

| Quantity | Value |
|---|---:|
| external points | 27 |
| longitude range | 91.43 – 127.22 |
| latitude range | 19.98 – 50.57 |
| local CHGIS v6 county points | 10,512 |
| median distance to nearest CHGIS point | 0.109° |
| share within 0.25° / 0.5° / 1° | 78% / 85% / 85% |
| median distance to nearest population city | 0.309° |

| External city | lon | lat | nearest CHGIS point | type | dist (°) |
|---|---:|---:|---|---|---:|
| 黑河 | 127.22 | 50.57 | 拜泉县 | 县 | 3.177 |
| 哈尔滨 | 126.62 | 45.93 | 滨江厅 | 厅 | 0.194 |
| 长春 | 125.17 | 44.07 | 农安县 | 县 | 0.355 |
| 沈阳卫 | 123.49 | 41.97 | 兴仁县 | 县 | 0.198 |
| 京师 | 116.35 | 39.94 | 良乡县 | 县 | 0.294 |
| 呼和浩特 | 111.49 | 40.91 | 右玉林卫 | 卫 | 1.141 |
| 太原 | 112.59 | 37.77 | 平晋县 | 县 | 0.046 |
| 郑州 | 113.56 | 34.66 | 须水县 | 县 | 0.110 |
| 应天府 | 118.93 | 31.92 | 上元县 | 县 | 0.018 |
| 天津卫 | 117.24 | 39.13 | 天津县 | 县 | 0.088 |
| 真定府 | 114.65 | 38.19 | 新市县 | 县 | 0.083 |
| 济南府 | 117.03 | 36.54 | 历城县 | 县 | 0.117 |
| 松江府 | 121.26 | 30.89 | 金山县 | 县 | 0.100 |
| 杭州府 | 120.14 | 30.17 | 余衍县 | 县 | 0.050 |
| 福州府 | 119.38 | 26.08 | 长乐县 | 县 | 0.056 |
| 南昌府 | 116.01 | 28.47 | 南昌县 | 县 | 0.233 |
| 广州府 | 113.29 | 23.10 | 番禺县 | 县 | 0.012 |
| 琼州府 | 110.28 | 19.98 | 琼山县 | 县 | 0.088 |
| 南宁府 | 108.37 | 22.75 | 宣化县 | 县 | 0.075 |
| 贵州司 | 106.75 | 26.36 | 茶山百纳等处长官司 | 长官司 | 0.019 |
| 云南府 | 102.82 | 24.83 | 大吴笼（部） | 部 | 0.041 |
| 成都府 | 104.21 | 30.40 | 广都县 | 县 | 0.173 |
| 西安府 | 108.94 | 34.06 | 乾封县 | 县 | 0.109 |
| 临洮府 | 103.99 | 35.13 | 操虏县 | 县 | 0.216 |
| 宁夏卫 | 106.23 | 38.40 | 廉县 | 县 | 0.098 |
| 哈密卫 | 93.39 | 42.95 | 效谷县 | 县 | 3.005 |
| 拉萨 | 91.43 | 29.51 | 杂瑜委员 | 委员 | 5.686 |

Caveat: only 27 points, concentrated in the far north-east; this is a **small external reference set**, not a national city sample. It is used to verify coordinate plausibility, not to estimate coverage.

## 3. Population-file coverage (descriptive only)

| Quantity | Value |
|---|---:|
| rows 1400–1620 | 135 |
| unique cities | 31 |
| 1° grids touched | 29 |
| panel grids | 291 |
| overlap grids | 26 (8.9%) |

The population file is a sparse city time series, not a continuous annual panel. No dose-response or competition model is fitted here (roadmap §4: no new control variable without pre-registration); it is recorded as a candidate exogenous proxy for a future dated Go decision.

## When this would fail

- Late-Ming table re-exported with different year coverage or rank codes.
- External GeoJSON replaced without re-running this script.
- CHGIS point layer swapped to a different CRS; distances are in degrees and assume WGS84.
- Any of these descriptive numbers is quoted as a causal result.

## Outputs

| Output | Path |
|---|---|
| late-Ming grid table | `data/derived/a10_late_ming_geography.csv` |
| external city cross-check | `data/derived/a10_external_city_crosscheck.csv` |

Private inputs; aggregate outputs only.
