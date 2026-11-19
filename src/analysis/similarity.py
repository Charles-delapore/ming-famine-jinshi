import numpy as np
import pandas as pd
from scipy import stats
from shapely.geometry import MultiPoint
from sklearn.linear_model import LinearRegression


def preprocess_zaihuang(df_jinshi, df_zaihuang):
    jinshi_clusters = []
    for cluster_id, cluster in df_jinshi.groupby('cluster'):
        jinshi_clusters.append({
            'time_min': cluster['EntryYear'].min(),
            'time_max': cluster['EntryYear'].max(),
            'x_min': cluster['X'].min(),
            'x_max': cluster['X'].max(),
            'y_min': cluster['Y'].min(),
            'y_max': cluster['Y'].max(),
        })

    valid_zaihuang_clusters = set()
    for z_cluster_id, z_cluster in df_zaihuang.groupby('cluster'):
        z_time_min = z_cluster['year'].min()
        z_time_max = z_cluster['year'].max()
        z_x_min = z_cluster['x'].min()
        z_x_max = z_cluster['x'].max()
        z_y_min = z_cluster['y'].min()
        z_y_max = z_cluster['y'].max()

        for jc in jinshi_clusters:
            time_overlap = (z_time_min <= jc['time_max']) & (z_time_max >= jc['time_min'])
            x_overlap = (z_x_min <= jc['x_max']) & (z_x_max >= jc['x_min'])
            y_overlap = (z_y_min <= jc['y_max']) & (z_y_max >= jc['y_min'])
            if time_overlap and x_overlap and y_overlap:
                valid_zaihuang_clusters.add(z_cluster_id)
                break

    return df_zaihuang[df_zaihuang['cluster'].isin(valid_zaihuang_clusters)]


def time_similarity(z_min, z_max, j_min, j_max):
    overlap_start = max(z_min, j_min)
    overlap_end = min(z_max, j_max)
    if overlap_start > overlap_end:
        return 0.0
    overlap = overlap_end - overlap_start + 1
    total = min(z_max - z_min + 1, j_max - j_min + 1)
    return overlap / total if total > 0 else 0


def space_iou(z_min_x, z_max_x, z_min_y, z_max_y, j_min_x, j_max_x, j_min_y, j_max_y):
    inter_min_x = max(z_min_x, j_min_x)
    inter_max_x = min(z_max_x, j_max_x)
    inter_min_y = max(z_min_y, j_min_y)
    inter_max_y = min(z_max_y, j_max_y)
    if inter_min_x >= inter_max_x or inter_min_y >= inter_max_y:
        return 0.0
    inter_area = (inter_max_x - inter_min_x) * (inter_max_y - inter_min_y)
    z_area = (z_max_x - z_min_x) * (z_max_y - z_min_y)
    j_area = (j_max_x - j_min_x) * (j_max_y - j_min_y)
    union = z_area + j_area - inter_area
    return inter_area / union if union > 0 else 0


def temporal_overlap_ratio(cluster1_time, cluster2_time, time_col1='EntryYear', time_col2='year'):
    t1_min, t1_max = cluster1_time[time_col1].min(), cluster1_time[time_col1].max()
    t2_min, t2_max = cluster2_time[time_col2].min(), cluster2_time[time_col2].max()

    overlap_start = max(t1_min, t2_min)
    overlap_end = min(t1_max, t2_max)
    if overlap_start > overlap_end:
        return 0.0

    overlap_duration = overlap_end - overlap_start + 1
    max_duration = max(t1_max - t1_min + 1, t2_max - t2_min + 1)
    return overlap_duration / max_duration if max_duration > 0 else 0


def spatial_overlap_ratio(cluster1, cluster2, x_col1='X', y_col1='Y', x_col2='x', y_col2='y'):
    try:
        points1 = MultiPoint(list(zip(cluster1[x_col1], cluster1[y_col1])))
        points2 = MultiPoint(list(zip(cluster2[x_col2], cluster2[y_col2])))
        hull1 = points1.convex_hull
        hull2 = points2.convex_hull
        if hull1.is_valid and hull2.is_valid and hull1.area > 0 and hull2.area > 0:
            intersection = hull1.intersection(hull2).area
            union = hull1.union(hull2).area
            return intersection / union if union > 0 else 0
    except Exception:
        pass

    x1_min, x1_max = cluster1[x_col1].min(), cluster1[x_col1].max()
    y1_min, y1_max = cluster1[y_col1].min(), cluster1[y_col1].max()
    x2_min, x2_max = cluster2[x_col2].min(), cluster2[x_col2].max()
    y2_min, y2_max = cluster2[y_col2].min(), cluster2[y_col2].max()

    return space_iou(x1_min, x1_max, y1_min, y1_max, x2_min, x2_max, y2_min, y2_max)


def calculate_time_space_similarity(cluster1, cluster2):
    t_overlap = temporal_overlap_ratio(cluster1, cluster2, 'EntryYear', 'year')
    s_overlap = spatial_overlap_ratio(cluster1, cluster2)

    return (t_overlap + s_overlap) / 2


def granger_causality_test(x, y, max_lag=10, significance=0.05):
    results = {
        'is_causal': False,
        'best_lag': 0,
        'f_statistic': 0.0,
        'p_value': 1.0,
    }

    n = len(x)
    if n < max_lag + 5:
        return results

    best_f = 0
    best_p = 1.0
    best_lag = 0

    for lag in range(1, min(max_lag + 1, n // 3)):
        try:
            y_target = y[lag:]
            X_restricted = np.column_stack([y[lag - 1:n - 1]])
            for l in range(2, lag + 1):
                if lag - l < n:
                    X_restricted = np.column_stack([X_restricted, y[lag - l:n - l]])

            X_unrestricted = X_restricted.copy()
            for l in range(lag):
                if lag - 1 - l < n:
                    X_unrestricted = np.column_stack([X_unrestricted, x[lag - 1 - l:n - 1 - l]])

            n_obs = len(y_target)
            if n_obs < X_unrestricted.shape[1] + 2:
                continue

            reg_r = LinearRegression().fit(X_restricted, y_target)
            resid_r = y_target - reg_r.predict(X_restricted)
            ssr_r = np.sum(resid_r ** 2)

            reg_u = LinearRegression().fit(X_unrestricted, y_target)
            resid_u = y_target - reg_u.predict(X_unrestricted)
            ssr_u = np.sum(resid_u ** 2)

            if ssr_r <= ssr_u or ssr_u <= 0:
                continue

            q = lag
            k = X_unrestricted.shape[1]
            f_stat = ((ssr_r - ssr_u) / q) / (ssr_u / (n_obs - k))
            p_val = 1 - stats.f.cdf(f_stat, q, n_obs - k)

            if f_stat > best_f:
                best_f = f_stat
                best_p = p_val
                best_lag = lag
        except Exception:
            continue

    results['best_lag'] = best_lag
    results['f_statistic'] = best_f
    results['p_value'] = best_p
    results['is_causal'] = best_p < significance

    return results


def build_cluster_time_series(cluster, time_col, value_col, year_range=None):
    if year_range is None:
        year_range = (cluster[time_col].min(), cluster[time_col].max())

    years = np.arange(year_range[0], year_range[1] + 1)
    counts = np.zeros(len(years))

    for i, year in enumerate(years):
        mask = cluster[time_col] == year
        if mask.any():
            counts[i] = cluster.loc[mask, value_col].sum() if value_col in cluster.columns else mask.sum()

    return years, counts


def compute_granger_causality_matrix(jinshi_df, zaihuang_df, max_lag=10, significance=0.05):
    import warnings
    warnings.warn(
        "聚类级Granger因果分析已废弃: 时序长度不足导致F统计量溢出(如3.79e27), "
        "结果在统计学上完全无效。请使用 grid_analysis.GridGrangerCausality 进行格网级因果分析, "
        "输出文件为 grid_granger_causality.xlsx。",
        DeprecationWarning,
        stacklevel=2
    )
    zaihuang_filtered = preprocess_zaihuang(jinshi_df, zaihuang_df)

    jinshi_clusters = list(jinshi_df.groupby('cluster'))
    zaihuang_clusters = list(zaihuang_filtered.groupby('cluster'))

    all_years = (
        min(jinshi_df['EntryYear'].min(), zaihuang_filtered['year'].min()),
        max(jinshi_df['EntryYear'].max(), zaihuang_filtered['year'].max()),
    )

    results = []
    for j_id, j_cluster in jinshi_clusters:
        if j_id == -1:
            continue
        _, j_series = build_cluster_time_series(
            j_cluster, 'EntryYear', 'level', all_years
        )

        for z_id, z_cluster in zaihuang_clusters:
            if z_id == -1:
                continue
            _, z_series = build_cluster_time_series(
                z_cluster, 'year', 'level', all_years
            )

            overlap_sim = calculate_time_space_similarity(j_cluster, z_cluster)

            gc_z_to_j = granger_causality_test(z_series, j_series, max_lag, significance)
            gc_j_to_z = granger_causality_test(j_series, z_series, max_lag, significance)

            results.append({
                'jinshi_cluster': j_id,
                'zaihuang_cluster': z_id,
                'overlap_similarity': overlap_sim,
                'granger_z_to_j': gc_z_to_j['is_causal'],
                'granger_j_to_z': gc_j_to_z['is_causal'],
                'gc_z_to_j_fstat': gc_z_to_j['f_statistic'],
                'gc_z_to_j_pval': gc_z_to_j['p_value'],
                'gc_z_to_j_lag': gc_z_to_j['best_lag'],
                'gc_j_to_z_fstat': gc_j_to_z['f_statistic'],
                'gc_j_to_z_pval': gc_j_to_z['p_value'],
                'gc_j_to_z_lag': gc_j_to_z['best_lag'],
                'causal_direction': (
                    'z->j' if gc_z_to_j['is_causal'] and not gc_j_to_z['is_causal']
                    else 'j->z' if gc_j_to_z['is_causal'] and not gc_z_to_j['is_causal']
                    else 'bidirectional' if gc_z_to_j['is_causal'] and gc_j_to_z['is_causal']
                    else 'none'
                ),
            })

    return pd.DataFrame(results)


def compute_similarity_matrix(jinshi_df, zaihuang_df):
    zaihuang_filtered = preprocess_zaihuang(jinshi_df, zaihuang_df)

    results = []
    for j_cluster_id, j_cluster in jinshi_df.groupby('cluster'):
        for z_cluster_id, z_cluster in zaihuang_filtered.groupby('cluster'):
            sim = calculate_time_space_similarity(j_cluster, z_cluster)
            results.append({
                'jinshi_cluster': j_cluster_id,
                'zaihuang_cluster': z_cluster_id,
                'similarity': sim,
            })

    return pd.DataFrame(results)


def fdr_correction(p_values, alpha=0.05):
    n = len(p_values)
    if n == 0:
        return np.array([]), np.array([])

    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]

    thresholds = np.zeros(n)
    for i in range(n):
        thresholds[i] = (i + 1) / n * alpha

    significant = np.zeros(n, dtype=bool)
    for i in range(n - 1, -1, -1):
        if sorted_p[i] <= thresholds[i]:
            significant[:i + 1] = True
            break

    corrected = np.zeros(n, dtype=bool)
    for i in range(n):
        corrected[sorted_indices[i]] = significant[i]

    q_values = np.zeros(n)
    for i in range(n):
        q_values[sorted_indices[i]] = sorted_p[i] * n / (sorted_indices[i] + 1)
    q_values = np.clip(q_values, 0, 1)

    return corrected, q_values
