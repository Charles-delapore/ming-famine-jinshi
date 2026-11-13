import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression, Ridge
import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config import OUTPUT_DIR, DATA_PATHS
from src.analysis.grid_analysis import (
    build_full_grid_data, compute_grid_derived_features,
    fdr_correction, MultiScaleCausalModel,
)


def sensitivity_grid_resolution(grid_sizes=None):
    print("\n--- 敏感性分析: 不同格网分辨率 ---")
    if grid_sizes is None:
        grid_sizes = [0.5, 1.0, 2.0]

    results = []
    for gs in grid_sizes:
        print(f"\n  格网分辨率: {gs}°×{gs}°")
        try:
            grid_data = build_full_grid_data(grid_size=gs, use_extended=True)
            grid_enriched = compute_grid_derived_features(grid_data)

            n_grids = grid_enriched[['grid_x', 'grid_y']].drop_duplicates().shape[0]
            n_years = grid_enriched['year'].nunique()

            ms_model = MultiScaleCausalModel(significance=0.05, use_ridge_when_collinear=True)
            stratified = ms_model.fit_stratified_model(grid_enriched)

            for scale_name, scale_df in stratified.items():
                if len(scale_df) > 0:
                    n_fdr = scale_df['fdr_significant'].sum() if 'fdr_significant' in scale_df.columns else 0
                    n_sig = scale_df['significant'].sum()
                    avg_r2 = scale_df['r_squared'].mean()
                else:
                    n_fdr = 0
                    n_sig = 0
                    avg_r2 = 0

                results.append({
                    'grid_size': gs,
                    'scale': scale_name,
                    'n_grids': n_grids,
                    'n_years': n_years,
                    'n_sig': n_sig,
                    'n_fdr_sig': n_fdr,
                    'avg_r2': round(avg_r2, 4),
                })
                print(f"    {scale_name}: {n_grids}格网, {n_sig}显著, {n_fdr}FDR显著, R²={avg_r2:.4f}")
        except Exception as e:
            print(f"    失败: {e}")
            results.append({
                'grid_size': gs, 'scale': 'error', 'n_grids': 0,
                'n_years': 0, 'n_sig': 0, 'n_fdr_sig': 0, 'avg_r2': 0,
            })

    df = pd.DataFrame(results)
    df.to_excel(os.path.join(OUTPUT_DIR, "sensitivity_grid_resolution.xlsx"),
                index=False, engine='openpyxl')
    print(f"\n  结果已保存至 {OUTPUT_DIR}/sensitivity_grid_resolution.xlsx")
    return df


def sensitivity_lag_groups(grid_data):
    print("\n--- 敏感性分析: 不同滞后分组 ---")

    lag_configs = {
        'original_1-5_6-10_11-20': {'short': [1, 3, 5], 'medium': [5, 10], 'long': [10, 15, 20]},
        'narrow_1-3_4-7_8-15': {'short': [1, 2, 3], 'medium': [4, 7], 'long': [8, 12, 15]},
        'wide_1-5_6-15_16-25': {'short': [1, 3, 5], 'medium': [6, 10, 15], 'long': [16, 20, 25]},
    }

    results = []
    for config_name, lags in lag_configs.items():
        print(f"\n  滞后配置: {config_name}")

        for (gx, gy), cell in grid_data.groupby(['grid_x', 'grid_y']):
            cell = cell.sort_values('year')
            if len(cell) < 30:
                continue

            j_series = cell['jinshi_count'].values
            if np.sum(j_series > 0) < 3:
                continue

            for scale_name, lag_list in lags.items():
                lag_cols = [f'zaihuang_lag{l}' for l in lag_list if f'zaihuang_lag{l}' in cell.columns]
                if len(lag_cols) < 2:
                    continue

                X = cell[lag_cols].values
                y = j_series

                valid = np.isfinite(X).all(axis=1) & np.isfinite(y)
                if valid.sum() < 20:
                    continue

                X_v, y_v = X[valid], y[valid]

                try:
                    from src.analysis.grid_analysis import MultiScaleCausalModel
                    vif = MultiScaleCausalModel._compute_vif(X_v)
                    has_collin = np.any(vif > 10)

                    if has_collin:
                        reg = Ridge(alpha=1.0).fit(X_v, y_v)
                        model_type = 'ridge'
                    else:
                        reg = LinearRegression().fit(X_v, y_v)
                        model_type = 'ols'

                    y_pred = reg.predict(X_v)
                    ss_res = np.sum((y_v - y_pred) ** 2)
                    ss_tot = np.sum((y_v - np.mean(y_v)) ** 2)
                    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

                    n = len(y_v)
                    k = X_v.shape[1]
                    if n > k + 1 and r2 < 1:
                        f_stat = (r2 / k) / ((1 - r2) / (n - k - 1))
                        p_val = 1 - stats.f.cdf(f_stat, k, n - k - 1)
                    else:
                        f_stat = 0
                        p_val = 1.0

                    results.append({
                        'config': config_name,
                        'scale': scale_name,
                        'grid_x': gx,
                        'grid_y': gy,
                        'r_squared': r2,
                        'p_value': p_val,
                        'significant': p_val < 0.05,
                        'model_type': model_type,
                        'max_vif': np.max(vif),
                    })
                except Exception:
                    continue

    if not results:
        print("  无有效结果")
        return pd.DataFrame()

    df = pd.DataFrame(results)

    for config_name in lag_configs:
        sub = df[df['config'] == config_name]
        for scale in ['short', 'medium', 'long']:
            scale_sub = sub[(sub['scale'] == scale) & (sub['significant'])]
            print(f"    {config_name} {scale}: {len(scale_sub)}显著")

    if len(df) > 0:
        p_vals = df['p_value'].values
        sig, q_vals = fdr_correction(p_vals, alpha=0.05)
        df['q_value'] = q_vals
        df['fdr_significant'] = sig

    df.to_excel(os.path.join(OUTPUT_DIR, "sensitivity_lag_groups.xlsx"),
                index=False, engine='openpyxl')
    print(f"\n  结果已保存至 {OUTPUT_DIR}/sensitivity_lag_groups.xlsx")
    return df


def run_stl_decomposition(grid_data):
    from statsmodels.tsa.seasonal import STL

    print("\n--- 时间序列分解 (STL) ---")

    results = []
    decomposed_data = []

    for (gx, gy), cell in grid_data.groupby(['grid_x', 'grid_y']):
        cell = cell.sort_values('year')
        if len(cell) < 20:
            continue

        z_series = cell['zaihuang_severity'].values.astype(float)
        j_series = cell['jinshi_count'].values.astype(float)

        if np.sum(z_series > 0) < 5 or np.std(z_series) < 1e-10:
            continue

        try:
            z_df = pd.Series(z_series, index=pd.period_range(
                start=str(int(cell['year'].iloc[0])),
                periods=len(z_series), freq='Y'
            ))

            stl = STL(z_df, period=min(7, len(z_series) // 2), robust=True)
            res = stl.fit()

            trend = res.trend.values
            seasonal = res.seasonal.values
            residual = res.resid.values

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                r_trend_j, p_trend_j = stats.pearsonr(trend, j_series) if np.std(trend) > 1e-10 else (0, 1)
                r_resid_j, p_resid_j = stats.pearsonr(residual, j_series) if np.std(residual) > 1e-10 else (0, 1)

            results.append({
                'grid_x': gx, 'grid_y': gy,
                'n_obs': len(cell),
                'var_trend': np.var(trend) / (np.var(z_series) + 1e-10),
                'var_seasonal': np.var(seasonal) / (np.var(z_series) + 1e-10),
                'var_resid': np.var(residual) / (np.var(z_series) + 1e-10),
                'corr_trend_jinshi': r_trend_j,
                'pval_trend_jinshi': p_trend_j,
                'corr_resid_jinshi': r_resid_j,
                'pval_resid_jinshi': p_resid_j,
                'sig_trend': p_trend_j < 0.05,
                'sig_resid': p_resid_j < 0.05,
            })

            decomposed_data.append({
                'grid_x': gx, 'grid_y': gy,
                'year': cell['year'].values,
                'zaihuang_original': z_series,
                'zaihuang_trend': trend,
                'zaihuang_seasonal': seasonal,
                'zaihuang_residual': residual,
                'jinshi_count': j_series,
            })
        except Exception:
            continue

    if not results:
        print("  无有效STL分解结果")
        return pd.DataFrame(), pd.DataFrame()

    df = pd.DataFrame(results)

    n_sig_trend = df['sig_trend'].sum()
    n_sig_resid = df['sig_resid'].sum()
    avg_var_trend = df['var_trend'].mean()
    avg_var_resid = df['var_resid'].mean()

    print(f"  STL分解完成: {len(df)} 个格网")
    print(f"  方差分解: 趋势={avg_var_trend:.2%}, 残差={avg_var_resid:.2%}")
    print(f"  趋势-进士显著: {n_sig_trend}, 残差-进士显著: {n_sig_resid}")

    if n_sig_resid > n_sig_trend:
        print("  → 残差(随机冲击)与进士关联更强, 支持短期冲击假说")
    else:
        print("  → 趋势(长期气候)与进士关联更强, 支持长期结构性影响假说")

    df.to_excel(os.path.join(OUTPUT_DIR, "stl_decomposition_results.xlsx"),
                index=False, engine='openpyxl')

    all_decomp_rows = []
    for item in decomposed_data:
        for i in range(len(item['year'])):
            all_decomp_rows.append({
                'grid_x': item['grid_x'],
                'grid_y': item['grid_y'],
                'year': item['year'][i],
                'zaihuang_original': item['zaihuang_original'][i],
                'zaihuang_trend': item['zaihuang_trend'][i],
                'zaihuang_seasonal': item['zaihuang_seasonal'][i],
                'zaihuang_residual': item['zaihuang_residual'][i],
                'jinshi_count': item['jinshi_count'][i],
            })

    decomp_df = pd.DataFrame(all_decomp_rows)
    decomp_df.to_csv(os.path.join(OUTPUT_DIR, "stl_decomposed_data.csv"), index=False)

    print(f"  结果已保存至 {OUTPUT_DIR}/stl_decomposition_results.xlsx")
    return df, decomp_df


def run_geodetector(grid_data):
    print("\n--- 地理探测器 ---")

    cell_avg = grid_data.groupby(['grid_x', 'grid_y']).agg(
        zaihuang_severity=('zaihuang_severity', 'mean'),
        jinshi_count=('jinshi_count', 'mean'),
        zaihuang_freq=('zaihuang_count', 'sum'),
    ).reset_index()

    cell_avg = cell_avg[(cell_avg['zaihuang_severity'] > 0) & (cell_avg['jinshi_count'] > 0)]
    if len(cell_avg) < 10:
        print("  有效格网不足, 跳过")
        return None

    y = cell_avg['jinshi_count'].values
    N = len(y)
    sigma_total = np.var(y) * N

    if sigma_total < 1e-10:
        print("  进士方差为零, 跳过")
        return None

    def _q_statistic(x_discrete, y_continuous, N, sigma_total):
        x_arr = np.array(x_discrete)
        unique_groups = np.unique(x_arr[~np.isnan(x_arr)])
        q_num = 0
        for g in unique_groups:
            mask = x_arr == g
            Nh = mask.sum()
            if Nh < 2:
                continue
            sigma_h = np.var(y_continuous[mask]) * Nh
            q_num += sigma_h
        q = 1 - q_num / sigma_total if sigma_total > 0 else 0
        return max(0, q)

    n_bins = min(5, len(cell_avg) // 3)
    if n_bins < 2:
        n_bins = 2

    try:
        x_bins_z = pd.qcut(cell_avg['zaihuang_severity'], q=n_bins,
                            labels=False, duplicates='drop')
    except ValueError:
        x_bins_z = pd.cut(cell_avg['zaihuang_severity'], bins=n_bins, labels=False)

    try:
        x_bins_x = pd.cut(cell_avg['grid_x'], bins=n_bins, labels=False)
    except ValueError:
        x_bins_x = np.zeros(N)

    try:
        x_bins_y = pd.cut(cell_avg['grid_y'], bins=n_bins, labels=False)
    except ValueError:
        x_bins_y = np.zeros(N)

    q_zaihuang = _q_statistic(x_bins_z, y, N, sigma_total)
    q_longitude = _q_statistic(x_bins_x, y, N, sigma_total)
    q_latitude = _q_statistic(x_bins_y, y, N, sigma_total)

    results = {
        'q_zaihuang_severity': round(q_zaihuang, 4),
        'q_longitude': round(q_longitude, 4),
        'q_latitude': round(q_latitude, 4),
        'n_cells': N,
    }

    print(f"  地理探测器完成: {N} 个格网")
    print(f"  q(灾荒严重度)={results['q_zaihuang_severity']}")
    print(f"  q(经度)={results['q_longitude']}")
    print(f"  q(纬度)={results['q_latitude']}")

    if q_zaihuang > max(q_longitude, q_latitude):
        print("  → 灾荒对进士空间分异的解释力 > 纯地理因素, 支持灾荒影响假说")
    else:
        print("  → 地理因素解释力更强, 灾荒影响需控制地理效应")

    pd.DataFrame([results]).to_excel(
        os.path.join(OUTPUT_DIR, "geodetector_results.xlsx"),
        index=False, engine='openpyxl'
    )
    return results


def run_sensitivity_and_decomposition(grid_data):
    print("=" * 60)
    print("敏感性分析 + 时间序列分解 + 地理探测器")
    print("=" * 60)

    sens_grid = sensitivity_grid_resolution()
    sens_lag = sensitivity_lag_groups(grid_data)
    stl_results, stl_decomp = run_stl_decomposition(grid_data)
    geodet = run_geodetector(grid_data)

    return sens_grid, sens_lag, stl_results, geodet
