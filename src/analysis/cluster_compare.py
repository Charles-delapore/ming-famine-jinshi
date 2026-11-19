import os
import sys

import numpy as np
import pandas as pd
from tqdm import tqdm

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config import COMPARE_PARAMS, OUTPUT_PATHS


def calculate_lagged_similarity(z_params, j_params, max_lag=20, time_weight=0.7, space_weight=0.3):
    (z_min_year, z_max_year, z_x_min, z_x_max, z_y_min, z_y_max) = z_params
    (j_min_year, j_max_year, j_x_min, j_x_max, j_y_min, j_y_max) = j_params

    lags = np.arange(-max_lag, max_lag + 1)
    adj_z_mins = z_min_year + lags
    adj_z_maxs = z_max_year + lags

    overlap_starts = np.maximum(adj_z_mins, j_min_year)
    overlap_ends = np.minimum(adj_z_maxs, j_max_year)
    overlap_durations = np.maximum(overlap_ends - overlap_starts + 1, 0)
    total_durations = np.minimum(j_max_year - j_min_year + 1, adj_z_maxs - adj_z_mins + 1)
    time_sims = np.divide(overlap_durations, total_durations, where=total_durations > 0,
                          out=np.zeros_like(overlap_durations))

    def _range_overlap(a_min, a_max, b_min, b_max):
        overlap = max(0, min(a_max, b_max) - max(a_min, b_min))
        union = max(a_max, b_max) - min(a_min, b_min)
        return overlap / union if union != 0 else 0

    x_sim = _range_overlap(z_x_min, z_x_max, j_x_min, j_x_max)
    y_sim = _range_overlap(z_y_min, z_y_max, j_y_min, j_y_max)
    space_sim = (x_sim + y_sim) / 2

    total_sims = time_weight * time_sims + space_weight * space_sim
    best_idx = np.argmax(total_sims)
    return total_sims[best_idx], lags[best_idx]


def _build_cluster_time_series(cluster, time_col, value_col, year_range):
    years = np.arange(year_range[0], year_range[1] + 1)
    values = np.zeros(len(years))
    cluster_years = cluster[time_col].values
    for i, year in enumerate(years):
        mask = cluster_years == year
        if mask.any():
            if value_col in cluster.columns:
                values[i] = cluster.loc[mask, value_col].sum()
            else:
                values[i] = mask.sum()
    return years, values


def _cross_correlation(x, y, max_lag=20):
    n = len(x)
    if n < 5:
        return 0.0, 0

    x_mean = np.mean(x)
    y_mean = np.mean(y)
    x_centered = x - x_mean
    y_centered = y - y_mean
    x_std = np.std(x)
    y_std = np.std(y)

    if x_std < 1e-10 or y_std < 1e-10:
        return 0.0, 0

    best_corr = -2.0
    best_lag = 0

    for lag in range(-max_lag, max_lag + 1):
        if lag >= 0:
            x_seg = x_centered[lag:]
            y_seg = y_centered[:n - lag] if lag > 0 else y_centered
        else:
            x_seg = x_centered[:n + lag]
            y_seg = y_centered[-lag:]

        m = len(x_seg)
        if m < 3:
            continue

        corr = np.sum(x_seg * y_seg) / (m * x_std * y_std)
        if corr > best_corr:
            best_corr = corr
            best_lag = lag

    return best_corr, best_lag


def _toroidal_shift(values, shift, value_min, value_max):
    shifted = values + shift
    span = value_max - value_min
    if span <= 0:
        return shifted
    shifted = value_min + (shifted - value_min) % span
    return shifted


def causal_relationship_test(j_group, z_group, n_permutations=1000, max_lag=20,
                             time_weight=0.7, space_weight=0.3,
                             study_year_range=None, study_spatial_range=None):
    z_years = z_group['year'].values
    z_xs = z_group['x'].values
    z_ys = z_group['y'].values
    j_years = j_group['EntryYear'].values
    j_xs = j_group['X'].values
    j_ys = j_group['Y'].values

    if len(z_years) < 10 or len(j_years) < 10:
        return 0.0, 0, 1.0, 0.0, 1.0

    if study_year_range is None:
        study_year_range = (min(z_years.min(), j_years.min()),
                            max(z_years.max(), j_years.max()))
    if study_spatial_range is None:
        study_spatial_range = (
            min(z_xs.min(), j_xs.min()),
            max(z_xs.max(), j_xs.max()),
            min(z_ys.min(), j_ys.min()),
            max(z_ys.max(), j_ys.max()),
        )

    all_years = study_year_range
    _, j_series = _build_cluster_time_series(j_group, 'EntryYear', 'level', all_years)
    _, z_series = _build_cluster_time_series(z_group, 'year', 'level', all_years)

    if len(j_series) < 10 or len(z_series) < 10:
        return 0.0, 0, 1.0, 0.0, 1.0

    if np.std(j_series) < 1e-10 or np.std(z_series) < 1e-10:
        return 0.0, 0, 1.0, 0.0, 1.0

    observed_corr, observed_lag = _cross_correlation(z_series, j_series, max_lag)

    z_params = (
        z_years.min(), z_years.max(),
        z_xs.min(), z_xs.max(),
        z_ys.min(), z_ys.max()
    )
    j_params = (
        j_years.min(), j_years.max(),
        j_xs.min(), j_xs.max(),
        j_ys.min(), j_ys.max()
    )
    observed_sim, _ = calculate_lagged_similarity(
        z_params, j_params, max_lag=max_lag,
        time_weight=time_weight, space_weight=space_weight
    )

    null_corrs = np.empty(n_permutations)
    null_sims = np.empty(n_permutations)
    null_lags = np.empty(n_permutations)

    year_span = study_year_range[1] - study_year_range[0]
    x_span = study_spatial_range[1] - study_spatial_range[0]
    y_span = study_spatial_range[3] - study_spatial_range[2]

    for i in range(n_permutations):
        time_shift = np.random.randint(1, max(year_span, 2))
        perm_z_series = np.roll(z_series, time_shift)

        corr, lag = _cross_correlation(perm_z_series, j_series, max_lag)
        null_corrs[i] = corr
        null_lags[i] = lag

        perm_z_years = _toroidal_shift(z_years, time_shift,
                                        study_year_range[0], study_year_range[1])
        spatial_shift_x = np.random.uniform(-x_span * 0.5, x_span * 0.5)
        spatial_shift_y = np.random.uniform(-y_span * 0.5, y_span * 0.5)
        perm_z_xs = _toroidal_shift(z_xs, spatial_shift_x,
                                     study_spatial_range[0], study_spatial_range[1])
        perm_z_ys = _toroidal_shift(z_ys, spatial_shift_y,
                                     study_spatial_range[2], study_spatial_range[3])

        perm_params = (
            perm_z_years.min(), perm_z_years.max(),
            perm_z_xs.min(), perm_z_xs.max(),
            perm_z_ys.min(), perm_z_ys.max()
        )
        sim, _ = calculate_lagged_similarity(
            perm_params, j_params, max_lag=max_lag,
            time_weight=time_weight, space_weight=space_weight
        )
        null_sims[i] = sim

    p_corr = (np.sum(null_corrs >= observed_corr) + 1) / (n_permutations + 1)
    p_sim = (np.sum(null_sims >= observed_sim) + 1) / (n_permutations + 1)

    return observed_corr, observed_lag, p_corr, observed_sim, p_sim


def _process_cluster_pair(args):
    j_cluster_id, j_group, z_cluster_id, z_group, params = args
    try:
        obs_corr, obs_lag, p_corr, obs_sim, p_sim = causal_relationship_test(
            j_group, z_group,
            n_permutations=params["n_permutations"],
            max_lag=params.get("max_lag", 20),
            time_weight=params["time_weight"],
            space_weight=params["space_weight"],
        )
        return {
            'jinshi_cluster': j_cluster_id,
            'zaihuang_cluster': z_cluster_id,
            'max_similarity': obs_sim,
            'best_lag': obs_lag,
            'p_value': p_sim,
            'cross_correlation': obs_corr,
            'p_value_corr': p_corr,
        }
    except Exception as e:
        print(f"Error processing ({j_cluster_id}, {z_cluster_id}): {e}")
        return None


def compare_clusters_lagged(jinshi_df, zaihuang_df, params=None):
    params = params or COMPARE_PARAMS

    j_clusters = {cid: g for cid, g in jinshi_df[jinshi_df['cluster'] != -1].groupby('cluster')}
    z_clusters = {cid: g for cid, g in zaihuang_df[zaihuang_df['cluster'] != -1].groupby('cluster')}

    tasks = []
    for j_id, j_group in j_clusters.items():
        for z_id, z_group in z_clusters.items():
            tasks.append((j_id, j_group, z_id, z_group, params))

    results = []
    for task in tqdm(tasks, desc="聚类比较(重写置换检验)"):
        res = _process_cluster_pair(task)
        if res:
            results.append(res)

    result_df = pd.DataFrame(results)
    if len(result_df) > 0:
        result_df['significant'] = result_df['p_value'] < params["significance_level"]
        result_df['significant_corr'] = result_df['p_value_corr'] < params["significance_level"]
    return result_df


def grid_permutation_test(grid_data, n_permutations=1000, max_lag=20, significance=0.05):
    z_grid = grid_data[grid_data['zaihuang_level'] > 0].copy()
    j_grid = grid_data[grid_data['jinshi_count'] > 0].copy()

    if len(z_grid) == 0 or len(j_grid) == 0:
        return pd.DataFrame()

    year_min = int(grid_data['year'].min())
    year_max = int(grid_data['year'].max())
    n_years = year_max - year_min + 1

    grid_cells = grid_data.groupby(['grid_x', 'grid_y'])
    cell_results = []

    for (gx, gy), cell_data in grid_cells:
        cell_data = cell_data.sort_values('year')
        z_series = cell_data['zaihuang_severity'].values
        j_series = cell_data['jinshi_count'].values

        if np.sum(z_series > 0) < 3 or np.sum(j_series > 0) < 3:
            continue
        if len(z_series) < 20:
            continue

        observed_corr, observed_lag = _cross_correlation(z_series, j_series, max_lag)

        null_corrs = np.empty(n_permutations)
        null_lags = np.empty(n_permutations)

        for i in range(n_permutations):
            shift = np.random.randint(1, n_years)
            perm_z = np.roll(z_series, shift)
            corr, lag = _cross_correlation(perm_z, j_series, max_lag)
            null_corrs[i] = corr
            null_lags[i] = lag

        p_value = (np.sum(null_corrs >= observed_corr) + 1) / (n_permutations + 1)

        cell_results.append({
            'grid_x': gx,
            'grid_y': gy,
            'n_years': len(z_series),
            'observed_corr': observed_corr,
            'observed_lag': observed_lag,
            'p_value': p_value,
            'significant': p_value < significance,
            'null_corr_mean': np.mean(null_corrs),
            'null_corr_std': np.std(null_corrs),
            'null_lag_mode': pd.Series(null_lags).mode().iloc[0] if len(null_lags) > 0 else 0,
        })

    if not cell_results:
        print("  格网置换检验: 无合格格网单元")
        return {}

    result_df = pd.DataFrame(cell_results)

    if len(result_df) > 0:
        from src.analysis.similarity import fdr_correction
        p_vals = result_df['p_value'].values
        sig, q_vals = fdr_correction(p_vals, alpha=0.05)
        result_df['q_value'] = q_vals
        result_df['fdr_significant'] = sig

    n_sig = result_df['significant'].sum()
    n_fdr = result_df['fdr_significant'].sum() if 'fdr_significant' in result_df.columns else 0
    p_val_distribution = result_df['p_value'].describe()

    print(f"  格网置换检验结果 (环形时间平移, {n_permutations}次置换):")
    print(f"    合格格网: {len(result_df)}")
    print(f"    显著格网 (p<0.05): {n_sig}")
    print(f"    FDR显著格网 (q<0.05): {n_fdr}")
    print(f"    p值分布: min={p_val_distribution['min']:.4f}, "
          f"25%={p_val_distribution['25%']:.4f}, "
          f"50%={p_val_distribution['50%']:.4f}, "
          f"75%={p_val_distribution['75%']:.4f}, "
          f"max={p_val_distribution['max']:.4f}")

    if n_sig > 0:
        sig_cells = result_df[result_df['significant']]
        lag_dist = sig_cells['observed_lag'].value_counts().sort_index()
        print(f"    显著格网滞后分布:")
        for lag, count in lag_dist.items():
            print(f"      滞后{lag}年: {count}个格网")

    result_df.to_excel(
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                     "output", "grid_permutation_test.xlsx"),
        index=False, engine='openpyxl'
    )

    return result_df
