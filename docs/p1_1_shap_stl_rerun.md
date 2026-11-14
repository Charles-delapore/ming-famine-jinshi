# P1-1 — SHAP / STL re-run on the v0.3 panel (2026-11-14)

- Generated: 2026-11-14 15:33
- Command: `python scripts/p1_1_shap_stl_rerun.py`
- Input: real `output/v03/panel_v03.csv.gz` (291 grids × 114 years, 1506–1619); v0.2 reference `<path to the v0.2 STL output>`.
- STL settings are **unchanged from v0.2** (`src/analysis/sensitivity_analysis.py: run_stl_decomposition`): `period=min(7, n//2)`, `robust=True`, variance shares, Pearson r of trend/residual vs `jinshi_count`.

## 1. STL v0.2 vs v0.3

| Metric | v0.2 | v0.3 |
|---|---:|---:|
| grids | 160.0000 | 160.0000 |
| mean_var_trend | 0.1849 | 0.1849 |
| mean_var_seasonal | 0.3089 | 0.3089 |
| mean_var_resid | 0.9771 | 0.9771 |
| sig_trend | 26.0000 | 18.0000 |
| sig_resid | 14.0000 | 14.0000 |
| sig_trend_pct | 0.1625 | 0.1125 |
| sig_resid_pct | 0.0875 | 0.0875 |
| common_grids |  | 160.0000 |
| var_trend_pearson_common |  | 1.0000 |
| sig_resid_agreement_common |  | 1.0000 |

v0.3 decomposes **160 grids** — exactly the same 160 as v0.2 (shared grids: **160**). The **famine series is identical** between v0.2 and v0.3 (only the Jinshi layer was corrected), so every STL variance share is bit-for-bit identical: trend variance share correlates at r = 1.000 on shared grids. What changes is only the Jinshi-dependent correlation: `sig_trend` drops from 26 to 18, while `sig_resid` stays at 14 and its flag agrees on 100.0% of grids. The qualitative STL conclusion (residual / short-term shock dominates over trend) is **unchanged** by the sample fix.

## 2. Factor importance — SUBSTITUTE, not SHAP

> ⚠️ **`shap` is not installed in this environment and this session does not install packages over the network.** The table below is **permutation importance** from a RandomForest surrogate (hold-out R² = 0.056), produced only so the v0.3 panel has a reproducible importance ranking. It is **not SHAP / GeoShapley**, and no SHAP-based conclusion is claimed. P1-1's SHAP acceptance item remains **open**.

> ⚠️ Hold-out R² = **0.056**: the surrogate has almost no predictive power on this zero-inflated panel, so the ranking below has **no interpretive value**. It is recorded only to demonstrate a reproducible pipeline and must not be quoted as evidence about factor importance.

| Feature | permutation importance (mean) | std |
|---|---:|---:|
| zaihuang_count | 0.1264 | 0.0071 |
| sev_lag3 | 0.0146 | 0.0024 |
| sev_lag1 | 0.0115 | 0.0053 |
| zaihuang_severity | 0.0062 | 0.0015 |
| sev_lag5 | 0.0057 | 0.0032 |
| zaihuang_level | 0.0043 | 0.0008 |

To close the SHAP item: install `shap` (offline wheel or a networked environment), then re-run the same feature matrix with `shap.TreeExplainer` on the v0.3 panel and compare with the v0.2 importance ranking. No threshold or feature set should be changed after seeing the result.

## 3. When this result would fail

- The STL agreement fails if `period` or `robust` is changed; both are held fixed here on purpose.
- The importance ranking is model-dependent (RandomForest surrogate); it is not a causal or SHAP attribution and would change with a different model or feature set.
- `train_test_split` is random (fixed seed); a different split changes the hold-out R² slightly.

## 4. Outputs

| Output | Path |
|---|---|
| v0.3 STL grid summary | `data/derived/p1_1_stl_v03_summary.csv` |
| v0.2/v0.3 comparison | `data/derived/p1_1_stl_comparison.csv` |
| permutation importance | `data/derived/p1_1_feature_importance.csv` |
| figure | `figures/p1_1_stl_comparison.{png,pdf}` |

Private inputs; aggregate outputs only.
