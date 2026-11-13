import numpy as np
import pandas as pd
from scipy import stats
import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config import OUTPUT_DIR


def _build_spatial_weights(coords, k=8):
    from libpysal.weights import KNN
    w = KNN(coords, k=min(k, len(coords) - 1))
    w.transform = 'r'
    return w


def run_spatial_durbin_model(grid_data):
    import libpysal
    import spreg

    print("\n--- 空间杜宾模型 (SDM) ---")

    cell_avg = grid_data.groupby(['grid_x', 'grid_y']).agg(
        zaihuang_severity=('zaihuang_severity', 'mean'),
        jinshi_count=('jinshi_count', 'mean'),
        zaihuang_count=('zaihuang_count', 'mean'),
    ).reset_index()

    cell_avg = cell_avg[(cell_avg['zaihuang_severity'] > 0) & (cell_avg['jinshi_count'] > 0)]
    if len(cell_avg) < 10:
        print("  有效格网不足10个, 跳过SDM")
        return None

    coords = cell_avg[['grid_x', 'grid_y']].values
    y = cell_avg['jinshi_count'].values.reshape(-1, 1)
    X = cell_avg[['zaihuang_severity']].values

    try:
        w = _build_spatial_weights(coords, k=8)
        w_name = "knn8"

        sdm = spreg.GM_Lag(y, X, w=w, w_lags=2, name_y='jinshi', name_x=['zaihuang'], name_w=w_name)

        results = {
            'model': 'Spatial_Durbin_GM_Lag',
            'n_obs': sdm.n,
            'r_squared': round(sdm.pr2, 4) if hasattr(sdm, 'pr2') else None,
            'coef_zaihuang': round(float(sdm.betas[1]), 4),
            'coef_W_zaihuang': round(float(sdm.betas[2]), 4) if len(sdm.betas) > 2 else None,
            'coef_rho': round(float(sdm.betas[-1]), 4),
        }

        print(f"  SDM拟合成功: n={results['n_obs']}")
        print(f"  R²={results['r_squared']}")
        print(f"  灾荒系数={results['coef_zaihuang']}")
        print(f"  空间滞后(W*灾荒)系数={results['coef_W_zaihuang']}")
        print(f"  空间自相关(ρ)={results['coef_rho']}")

        if results['coef_rho'] > 0.1:
            print("  → 空间自相关显著, OLS独立假设被违反, 空间回归更可靠")
        else:
            print("  → 空间自相关较弱, OLS结果基本可靠")

        return results
    except Exception as e:
        print(f"  SDM拟合失败: {e}")
        return None


def run_gwr_analysis(grid_data):
    from mgwr.gwr import GWR
    from mgwr.sel_bw import Sel_BW

    print("\n--- 地理加权回归 (GWR) ---")

    cell_avg = grid_data.groupby(['grid_x', 'grid_y']).agg(
        zaihuang_severity=('zaihuang_severity', 'mean'),
        jinshi_count=('jinshi_count', 'mean'),
    ).reset_index()

    cell_avg = cell_avg[(cell_avg['zaihuang_severity'] > 0) & (cell_avg['jinshi_count'] > 0)]
    if len(cell_avg) < 20:
        print("  有效格网不足20个, 跳过GWR")
        return None

    coords = cell_avg[['grid_x', 'grid_y']].values
    y = cell_avg['jinshi_count'].values.reshape(-1, 1)
    X = cell_avg[['zaihuang_severity']].values

    X = (X - X.mean()) / (X.std() + 1e-10)
    y = (y - y.mean()) / (y.std() + 1e-10)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            bw = Sel_BW(coords, y, X, kernel='gaussian', fixed=False)
            bw_value = bw.search(bw_min=2, bw_max=max(50, len(coords) // 2))

        gwr_model = GWR(coords, y, X, bw_value, kernel='gaussian', fixed=False)
        gwr_results = gwr_model.fit()

        cell_avg['gwr_coef'] = gwr_results.params[:, 1]
        cell_avg['gwr_tval'] = gwr_results.tvalues[:, 1]
        cell_avg['gwr_local_r2'] = gwr_results.localR2
        cell_avg['gwr_sig'] = np.abs(cell_avg['gwr_tval']) > 1.96

        n_sig = cell_avg['gwr_sig'].sum()
        n_positive = (cell_avg['gwr_coef'] > 0).sum()
        n_negative = (cell_avg['gwr_coef'] < 0).sum()

        print(f"  GWR拟合成功: n={len(cell_avg)}, bw={bw_value:.2f}")
        print(f"  全局R²={gwr_results.R2:.4f}")
        print(f"  显著格网: {n_sig}/{len(cell_avg)}")
        print(f"  正系格网: {n_positive}, 负系格网: {n_negative}")

        sig_cells = cell_avg[cell_avg['gwr_sig']]
        if len(sig_cells) > 0:
            print(f"  显著格网系数范围: [{sig_cells['gwr_coef'].min():.4f}, {sig_cells['gwr_coef'].max():.4f}]")
            for _, row in sig_cells.head(5).iterrows():
                print(f"    ({row['grid_x']:.1f}, {row['grid_y']:.1f}): "
                      f"coef={row['gwr_coef']:.4f}, t={row['gwr_tval']:.2f}, "
                      f"local_R²={row['gwr_local_r2']:.4f}")

        cell_avg.to_excel(
            os.path.join(OUTPUT_DIR, "gwr_coefficients.xlsx"),
            index=False, engine='openpyxl'
        )
        print(f"  GWR系数已保存至 {OUTPUT_DIR}/gwr_coefficients.xlsx")

        return cell_avg
    except Exception as e:
        print(f"  GWR拟合失败: {e}")
        return None


def run_spatial_analysis(grid_data):
    print("=" * 60)
    print("空间异质性因果模型分析")
    print("=" * 60)

    sdm_results = run_spatial_durbin_model(grid_data)
    gwr_results = run_gwr_analysis(grid_data)

    return sdm_results, gwr_results
