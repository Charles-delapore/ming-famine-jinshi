import os
import sys

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import DBSCAN
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config import DATA_PATHS, OUTPUT_DIR


def load_grid_data(grid_file=None):
    grid_file = grid_file or DATA_PATHS["grid_data_20_load"]
    df = pd.read_csv(grid_file)
    df = df.rename(columns={
        'Year': 'year',
        'Center_X': 'grid_x',
        'Center_Y': 'grid_y',
        'LevelG': 'jinshi_count',
        'LevelD': 'zaihuang_level',
    })
    df['zaihuang_severity'] = df['zaihuang_level']
    df['zaihuang_count'] = (df['zaihuang_level'] > 0).astype(int)
    return df


def build_full_grid_data(zaihuang_file=None, jinshi_file=None, grid_size=1.0, use_extended=True):
    from src.data_processing.loader import load_extended_jinshi, load_extended_zaihuang

    if use_extended:
        print("  使用扩展时间序列 (1521-1619年灾荒+进士)...")
        try:
            zaihuang_ext = load_extended_zaihuang()
            jinshi_ext = load_extended_jinshi()
            print(f"    扩展灾荒: {len(zaihuang_ext)} 条 ({zaihuang_ext['year'].min()}-{zaihuang_ext['year'].max()})")
            print(f"    扩展进士: {len(jinshi_ext)} 条 ({jinshi_ext['EntryYear'].min()}-{jinshi_ext['EntryYear'].max()})")
        except Exception as e:
            print(f"    扩展数据加载失败: {e}, 回退到基础数据")
            zaihuang_ext = None
            jinshi_ext = None

    if use_extended and zaihuang_ext is not None:
        z_base = pd.read_csv(zaihuang_file or DATA_PATHS["merged_data"])
        z_base = z_base.rename(columns={'x': 'X', 'y': 'Y'})
        if 'level' not in z_base.columns and 'zaihuang_level' in z_base.columns:
            z_base = z_base.rename(columns={'zaihuang_level': 'level'})

        z_ext = zaihuang_ext[['year', 'X', 'Y', 'level']].copy()
        z_base_sub = z_base[['year', 'X', 'Y', 'level']].copy() if 'level' in z_base.columns else z_base[['year', 'X', 'Y']].copy()
        if 'level' not in z_base_sub.columns:
            z_base_sub['level'] = 0

        zaihuang = pd.concat([z_base_sub, z_ext], ignore_index=True)
        zaihuang = zaihuang.drop_duplicates(subset=['year', 'X', 'Y'], keep='last')
        print(f"    合并灾荒: {len(zaihuang)} 条 ({zaihuang['year'].min()}-{zaihuang['year'].max()})")
    else:
        zaihuang = pd.read_csv(zaihuang_file or DATA_PATHS["merged_data"])
        zaihuang = zaihuang.rename(columns={'x': 'X', 'y': 'Y'})
        if 'level' not in zaihuang.columns and 'zaihuang_level' in zaihuang.columns:
            zaihuang = zaihuang.rename(columns={'zaihuang_level': 'level'})

    if use_extended and jinshi_ext is not None:
        j_base = pd.read_csv(jinshi_file or DATA_PATHS["ming_general"])

        j_ext = jinshi_ext[['EntryYear', 'X', 'Y']].copy()
        j_base_sub = j_base[['EntryYear', 'X', 'Y']].copy()

        jinshi = pd.concat([j_base_sub, j_ext], ignore_index=True)
        jinshi = jinshi.drop_duplicates(subset=['EntryYear', 'X', 'Y'], keep='last')
        print(f"    合并进士: {len(jinshi)} 条 ({jinshi['EntryYear'].min()}-{jinshi['EntryYear'].max()})")
    else:
        jinshi = pd.read_csv(jinshi_file or DATA_PATHS["ming_general"])

    zaihuang['grid_x'] = np.floor(zaihuang['X'] / grid_size) * grid_size + grid_size / 2
    zaihuang['grid_y'] = np.floor(zaihuang['Y'] / grid_size) * grid_size + grid_size / 2
    jinshi['grid_x'] = np.floor(jinshi['X'] / grid_size) * grid_size + grid_size / 2
    jinshi['grid_y'] = np.floor(jinshi['Y'] / grid_size) * grid_size + grid_size / 2

    z_agg = zaihuang.groupby(['year', 'grid_x', 'grid_y']).agg(
        zaihuang_level=('level', 'max'),
        zaihuang_count=('level', 'count'),
        zaihuang_severity=('level', 'sum'),
    ).reset_index()

    j_agg = jinshi.groupby(['EntryYear', 'grid_x', 'grid_y']).agg(
        jinshi_count=('EntryYear', 'count'),
    ).reset_index()
    j_agg = j_agg.rename(columns={'EntryYear': 'year'})

    all_years = range(int(min(z_agg['year'].min(), j_agg['year'].min())),
                      int(max(z_agg['year'].max(), j_agg['year'].max())) + 1)
    all_grids = sorted(set(zip(z_agg['grid_x'], z_agg['grid_y'])) | set(zip(j_agg['grid_x'], j_agg['grid_y'])))

    rows = [(y, gx, gy) for y in all_years for gx, gy in all_grids]
    full_df = pd.DataFrame(rows, columns=['year', 'grid_x', 'grid_y'])

    full_df = full_df.merge(
        z_agg[['year', 'grid_x', 'grid_y', 'zaihuang_level', 'zaihuang_count', 'zaihuang_severity']],
        on=['year', 'grid_x', 'grid_y'], how='left'
    )
    full_df = full_df.merge(
        j_agg[['year', 'grid_x', 'grid_y', 'jinshi_count']],
        on=['year', 'grid_x', 'grid_y'], how='left'
    )

    full_df['zaihuang_level'] = full_df['zaihuang_level'].fillna(0)
    full_df['zaihuang_count'] = full_df['zaihuang_count'].fillna(0)
    full_df['zaihuang_severity'] = full_df['zaihuang_severity'].fillna(0)
    full_df['jinshi_count'] = full_df['jinshi_count'].fillna(0)

    return full_df


class GridSTDCluster:
    def __init__(self, eps1=1.0, eps2=2.0, min_samples=3,
                 use_logistic_weight=True, logistic_k=1.7, logistic_e=8,
                 zaihuang_threshold=2):
        self.eps1 = eps1
        self.eps2 = eps2
        self.min_samples = min_samples
        self.use_logistic_weight = use_logistic_weight
        self.logistic_k = logistic_k
        self.logistic_e = logistic_e
        self.zaihuang_threshold = zaihuang_threshold

    def _logistic_weight(self, level):
        return 1.0 / (1.0 + np.exp(-self.logistic_e * (self.logistic_k - level)))

    def fit(self, grid_data):
        drought = grid_data[grid_data['zaihuang_level'] >= self.zaihuang_threshold].copy()

        if len(drought) == 0:
            self.labels_ = np.array([])
            self.n_clusters_ = 0
            self.drought_data_ = drought
            return self

        self.drought_data_ = drought

        features = drought[['grid_x', 'grid_y', 'year', 'zaihuang_level']].values
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        self._scaler = scaler

        spatial_dist = np.sqrt(
            (features_scaled[:, 0].reshape(-1, 1) - features_scaled[:, 0].reshape(1, -1)) ** 2 +
            (features_scaled[:, 1].reshape(-1, 1) - features_scaled[:, 1].reshape(1, -1)) ** 2
        )

        temporal_dist = np.abs(
            features_scaled[:, 2].reshape(-1, 1) - features_scaled[:, 2].reshape(1, -1)
        )

        condition = temporal_dist <= self.eps2
        dist_matrix = np.where(condition, spatial_dist, 2 * self.eps1)

        if self.use_logistic_weight:
            levels = drought['zaihuang_level'].values
            w = np.array([self._logistic_weight(l) for l in levels])
            weight_matrix = 0.5 * (w.reshape(-1, 1) + w.reshape(1, -1))
            dist_matrix = dist_matrix / (weight_matrix + 1e-8)

        db = DBSCAN(eps=self.eps1, min_samples=self.min_samples, metric='precomputed')
        db.fit(dist_matrix)
        self.labels_ = db.labels_
        self.n_clusters_ = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
        return self

    def compute_migration_trajectory(self):
        if not hasattr(self, 'drought_data_') or len(self.drought_data_) == 0:
            return {}

        df = self.drought_data_.copy()
        df['cluster'] = self.labels_

        trajectories = {}
        for cid in sorted(set(self.labels_)):
            if cid == -1:
                continue
            cluster = df[df['cluster'] == cid]

            yearly_data = []
            for year, year_group in cluster.groupby('year'):
                W = 1.0 / (1.0 + (year_group['zaihuang_level'].values / (-1.5)) ** 6)
                W = W / (W.sum() + 1e-8)
                cx = np.sum(year_group['grid_x'].values * W)
                cy = np.sum(year_group['grid_y'].values * W)
                yearly_data.append({
                    'year': year,
                    'centroid_x': cx,
                    'centroid_y': cy,
                    'n_grid_cells': len(year_group),
                    'total_severity': year_group['zaihuang_severity'].sum(),
                    'max_level': year_group['zaihuang_level'].max(),
                })

            yearly_centers = pd.DataFrame(yearly_data).sort_values('year')

            if len(yearly_centers) >= 2:
                xs = yearly_centers['centroid_x'].values
                ys = yearly_centers['centroid_y'].values

                dx = np.diff(xs)
                dy = np.diff(ys)
                angles = np.arctan2(dy, dx)
                mean_angle = np.mean(angles)

                beta = sum(
                    (xs[i + 1] - xs[i]) * (ys[i + 1] + ys[i])
                    for i in range(len(xs) - 1)
                )
                if beta > 0:
                    rotation = 'clockwise'
                elif beta < 0:
                    rotation = 'counterclockwise'
                else:
                    rotation = 'none'

                angle_deg = np.degrees(mean_angle) % 360
                if 337.5 <= angle_deg or angle_deg < 22.5:
                    direction = 'E'
                elif 22.5 <= angle_deg < 67.5:
                    direction = 'NE'
                elif 67.5 <= angle_deg < 112.5:
                    direction = 'N'
                elif 112.5 <= angle_deg < 157.5:
                    direction = 'NW'
                elif 157.5 <= angle_deg < 202.5:
                    direction = 'W'
                elif 202.5 <= angle_deg < 247.5:
                    direction = 'SW'
                elif 247.5 <= angle_deg < 292.5:
                    direction = 'S'
                else:
                    direction = 'SE'

                total_displacement = np.sqrt((xs[-1] - xs[0]) ** 2 + (ys[-1] - ys[0]) ** 2)
                path_length = np.sum(np.sqrt(dx ** 2 + dy ** 2))
                step_distances = np.sqrt(dx ** 2 + dy ** 2)
                avg_speed = np.mean(step_distances) if len(step_distances) > 0 else 0

                trajectories[cid] = {
                    'trajectory': yearly_centers,
                    'migration_direction_deg': np.degrees(mean_angle),
                    'migration_direction': direction,
                    'rotation': rotation,
                    'rotation_beta': beta,
                    'total_displacement': total_displacement,
                    'path_length': path_length,
                    'avg_speed': avg_speed,
                    'start_centroid': (xs[0], ys[0]),
                    'end_centroid': (xs[-1], ys[-1]),
                    'n_years': len(yearly_centers),
                    'n_grid_cells_total': yearly_centers['n_grid_cells'].sum(),
                    'duration': yearly_centers['year'].max() - yearly_centers['year'].min() + 1,
                }

        return trajectories


class GridGrangerCausality:
    def __init__(self, max_lag=20, significance=0.05, min_obs=30):
        self.max_lag = max_lag
        self.significance = significance
        self.min_obs = min_obs

    def _granger_test(self, x, y, max_lag):
        n = len(x)
        if n < max_lag + 5:
            return {'is_causal': False, 'best_lag': 0, 'f_statistic': 0.0, 'p_value': 1.0}

        best_f = 0
        best_p = 1.0
        best_lag = 0
        MAX_F_STAT = 1000.0

        for lag in range(1, min(max_lag + 1, n // 3)):
            try:
                y_target = y[lag:]
                X_r = y[lag - 1:n - 1].reshape(-1, 1)
                for l in range(2, lag + 1):
                    if lag - l < n:
                        X_r = np.column_stack([X_r, y[lag - l:n - l]])

                X_u = X_r.copy()
                for l in range(lag):
                    if lag - 1 - l < n:
                        X_u = np.column_stack([X_u, x[lag - 1 - l:n - 1 - l]])

                n_obs = len(y_target)
                if n_obs < X_u.shape[1] + 2:
                    continue

                reg_r = LinearRegression().fit(X_r, y_target)
                ssr_r = np.sum((y_target - reg_r.predict(X_r)) ** 2)

                reg_u = LinearRegression().fit(X_u, y_target)
                ssr_u = np.sum((y_target - reg_u.predict(X_u)) ** 2)

                if ssr_r <= ssr_u or ssr_u <= 1e-12:
                    continue

                q = lag
                k = X_u.shape[1]
                f_stat = ((ssr_r - ssr_u) / q) / (ssr_u / (n_obs - k))

                if not np.isfinite(f_stat) or f_stat > MAX_F_STAT:
                    f_stat = MAX_F_STAT

                p_val = 1 - stats.f.cdf(f_stat, q, n_obs - k)

                if f_stat > best_f:
                    best_f = f_stat
                    best_p = p_val
                    best_lag = lag
            except Exception:
                continue

        return {
            'is_causal': best_p < self.significance,
            'best_lag': best_lag,
            'f_statistic': best_f,
            'p_value': best_p,
        }

    def analyze_grid_causality(self, grid_data):
        grid_cells = grid_data.groupby(['grid_x', 'grid_y'])

        results = []
        for (gx, gy), cell_data in grid_cells:
            cell_data = cell_data.sort_values('year')
            years = cell_data['year'].values

            z_series = cell_data['zaihuang_severity'].values
            j_series = cell_data['jinshi_count'].values

            if np.sum(z_series > 0) < 3 or np.sum(j_series > 0) < 3:
                continue

            if len(z_series) < self.min_obs:
                continue

            gc_z_to_j = self._granger_test(z_series, j_series, self.max_lag)
            gc_j_to_z = self._granger_test(j_series, z_series, self.max_lag)

            results.append({
                'grid_x': gx,
                'grid_y': gy,
                'n_years': len(z_series),
                'zaihuang_years': int(np.sum(z_series > 0)),
                'jinshi_years': int(np.sum(j_series > 0)),
                'gc_z_to_j_causal': gc_z_to_j['is_causal'],
                'gc_z_to_j_lag': gc_z_to_j['best_lag'],
                'gc_z_to_j_fstat': gc_z_to_j['f_statistic'],
                'gc_z_to_j_pval': gc_z_to_j['p_value'],
                'gc_j_to_z_causal': gc_j_to_z['is_causal'],
                'gc_j_to_z_lag': gc_j_to_z['best_lag'],
                'gc_j_to_z_fstat': gc_j_to_z['f_statistic'],
                'gc_j_to_z_pval': gc_j_to_z['p_value'],
                'causal_direction': (
                    'z->j' if gc_z_to_j['is_causal'] and not gc_j_to_z['is_causal']
                    else 'j->z' if gc_j_to_z['is_causal'] and not gc_z_to_j['is_causal']
                    else 'bidirectional' if gc_z_to_j['is_causal'] and gc_j_to_z['is_causal']
                    else 'none'
                ),
            })

        return pd.DataFrame(results)


def fdr_correction(p_values, alpha=0.05):
    n = len(p_values)
    if n == 0:
        return np.array([]), np.array([])

    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]

    thresholds = np.array([(i + 1) / n * alpha for i in range(n)])

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


def compute_grid_derived_features(grid_data):
    grid_data = grid_data.copy()
    grid_data = grid_data.sort_values(['grid_x', 'grid_y', 'year'])

    grid_data['cumulative_severity'] = grid_data.groupby(['grid_x', 'grid_y'])['zaihuang_severity'].cumsum()

    grid_data['drought_duration'] = 0
    for (gx, gy), cell in grid_data.groupby(['grid_x', 'grid_y']):
        idx = cell.index
        levels = cell['zaihuang_level'].values
        durations = np.zeros(len(levels))
        count = 0
        for i in range(len(levels)):
            if levels[i] > 0:
                count += 1
                durations[i] = count
            else:
                count = 0
                durations[i] = 0
        grid_data.loc[idx, 'drought_duration'] = durations

    grid_data['consecutive_drought_years'] = grid_data.groupby(['grid_x', 'grid_y'])['drought_duration'].transform(
        lambda x: x.rolling(5, min_periods=1).max()
    )

    grid_data['max_severity_5yr'] = grid_data.groupby(['grid_x', 'grid_y'])['zaihuang_severity'].transform(
        lambda x: x.rolling(5, min_periods=1).max()
    )
    grid_data['drought_frequency_10yr'] = grid_data.groupby(['grid_x', 'grid_y'])['zaihuang_count'].transform(
        lambda x: x.rolling(10, min_periods=1).sum()
    )

    grid_data['zaihuang_lag1'] = grid_data.groupby(['grid_x', 'grid_y'])['zaihuang_severity'].shift(1).fillna(0)
    grid_data['zaihuang_lag3'] = grid_data.groupby(['grid_x', 'grid_y'])['zaihuang_severity'].shift(3).fillna(0)
    grid_data['zaihuang_lag5'] = grid_data.groupby(['grid_x', 'grid_y'])['zaihuang_severity'].shift(5).fillna(0)
    grid_data['zaihuang_lag10'] = grid_data.groupby(['grid_x', 'grid_y'])['zaihuang_severity'].shift(10).fillna(0)
    grid_data['zaihuang_lag15'] = grid_data.groupby(['grid_x', 'grid_y'])['zaihuang_severity'].shift(15).fillna(0)
    grid_data['zaihuang_lag20'] = grid_data.groupby(['grid_x', 'grid_y'])['zaihuang_severity'].shift(20).fillna(0)

    grid_data['jinshi_lag1'] = grid_data.groupby(['grid_x', 'grid_y'])['jinshi_count'].shift(1).fillna(0)
    grid_data['jinshi_lag3'] = grid_data.groupby(['grid_x', 'grid_y'])['jinshi_count'].shift(3).fillna(0)

    grid_data['zaihuang_ma5'] = grid_data.groupby(['grid_x', 'grid_y'])['zaihuang_severity'].transform(
        lambda x: x.rolling(5, min_periods=1).mean()
    )
    grid_data['jinshi_ma5'] = grid_data.groupby(['grid_x', 'grid_y'])['jinshi_count'].transform(
        lambda x: x.rolling(5, min_periods=1).mean()
    )

    grid_data['severity_intensity'] = grid_data['zaihuang_level'] * grid_data['drought_duration']

    return grid_data


class MultiScaleCausalModel:
    def __init__(self, significance=0.05, use_ridge_when_collinear=True, vif_threshold=10.0,
                 use_lasso_filter=True, use_bic_selection=True):
        self.significance = significance
        self.use_ridge_when_collinear = use_ridge_when_collinear
        self.vif_threshold = vif_threshold
        self.use_lasso_filter = use_lasso_filter
        self.use_bic_selection = use_bic_selection

    @staticmethod
    def _compute_vif(X):
        n_cols = X.shape[1]
        vif_values = np.zeros(n_cols)
        for i in range(n_cols):
            mask = np.ones(n_cols, dtype=bool)
            mask[i] = False
            if n_cols < 2:
                vif_values[i] = 1.0
                continue
            X_other = X[:, mask]
            X_i = X[:, i]
            ss_tot = np.sum((X_i - np.mean(X_i)) ** 2)
            if ss_tot < 1e-12:
                vif_values[i] = np.inf
                continue
            reg = LinearRegression().fit(X_other, X_i)
            y_pred = reg.predict(X_other)
            ss_res = np.sum((X_i - y_pred) ** 2)
            r2 = 1 - ss_res / ss_tot
            if r2 >= 1.0:
                vif_values[i] = np.inf
            elif r2 <= 0.0:
                vif_values[i] = 1.0
            else:
                vif_values[i] = 1.0 / (1.0 - r2)
        return vif_values

    @staticmethod
    def _compute_bic(n, ss_res, k):
        if ss_res <= 0:
            ss_res = 1e-10
        return n * np.log(ss_res / n) + k * np.log(n)

    def _lasso_filter(self, X, y, feature_names):
        from sklearn.linear_model import LassoCV
        try:
            lasso = LassoCV(cv=min(5, len(y) // 10), random_state=42, max_iter=5000)
            lasso.fit(X, y)
            selected_mask = np.abs(lasso.coef_) > 1e-6
            if selected_mask.sum() < 1:
                selected_mask = np.abs(lasso.coef_) > 0
            if selected_mask.sum() < 1:
                return X, feature_names, []
            X_selected = X[:, selected_mask]
            names_selected = [feature_names[i] for i in range(len(feature_names)) if selected_mask[i]]
            dropped = [feature_names[i] for i in range(len(feature_names)) if not selected_mask[i]]
            return X_selected, names_selected, dropped
        except Exception:
            return X, feature_names, []

    def _bic_select_lags(self, X, y, feature_names):
        n = len(y)
        if n < 10:
            return X, feature_names

        best_bic = np.inf
        best_mask = np.ones(X.shape[1], dtype=bool)

        from itertools import combinations
        n_features = X.shape[1]
        for k in range(1, n_features + 1):
            for combo in combinations(range(n_features), k):
                X_sub = X[:, list(combo)]
                try:
                    reg = LinearRegression().fit(X_sub, y)
                    ss_res = np.sum((y - reg.predict(X_sub)) ** 2)
                    bic = self._compute_bic(n, ss_res, k + 1)
                    if bic < best_bic:
                        best_bic = bic
                        best_mask = np.zeros(n_features, dtype=bool)
                        best_mask[list(combo)] = True
                except Exception:
                    continue

        X_selected = X[:, best_mask]
        names_selected = [feature_names[i] for i in range(n_features) if best_mask[i]]
        return X_selected, names_selected

    def _ols_regression(self, X, y):
        try:
            vif = self._compute_vif(X)
            has_collinearity = np.any(vif > self.vif_threshold)

            if has_collinearity and self.use_ridge_when_collinear:
                reg = Ridge(alpha=1.0).fit(X, y)
            else:
                reg = LinearRegression().fit(X, y)

            y_pred = reg.predict(X)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

            n = len(y)
            k = X.shape[1]
            if n > k + 1:
                f_stat = (r_squared / k) / ((1 - r_squared) / (n - k - 1)) if r_squared < 1 else 0
                p_val = 1 - stats.f.cdf(f_stat, k, n - k - 1)
            else:
                f_stat = 0
                p_val = 1.0

            model_type = 'ridge' if (has_collinearity and self.use_ridge_when_collinear) else 'ols'

            return reg, r_squared, f_stat, p_val, vif, has_collinearity, model_type
        except Exception:
            return None, 0, 0, 1.0, np.array([]), False, 'failed'

    def fit_stratified_model(self, grid_data, target_grids=None):
        results = {
            'short_term': [],
            'medium_term': [],
            'long_term': [],
        }

        if target_grids is not None and len(target_grids) > 0:
            grid_set = set(zip(target_grids['grid_x'], target_grids['grid_y']))
            grid_groups = [(k, v) for k, v in grid_data.groupby(['grid_x', 'grid_y']) if k in grid_set]
        else:
            grid_groups = [(k, v) for k, v in grid_data.groupby(['grid_x', 'grid_y'])]

        for (gx, gy), cell in grid_groups:
            cell = cell.sort_values('year')
            if len(cell) < 30:
                continue

            j_series = cell['jinshi_count'].values

            z_lag1 = cell['zaihuang_lag1'].values
            z_lag3 = cell['zaihuang_lag3'].values
            z_lag5 = cell['zaihuang_lag5'].values
            z_lag10 = cell['zaihuang_lag10'].values
            z_lag15 = cell['zaihuang_lag15'].values
            z_lag20 = cell['zaihuang_lag20'].values

            if np.sum(cell['zaihuang_severity'] > 0) < 3 or np.sum(j_series > 0) < 3:
                continue

            lag_configs = {
                'short_term': (np.column_stack([z_lag1, z_lag3, z_lag5]),
                               ['lag1', 'lag3', 'lag5']),
                'medium_term': (np.column_stack([z_lag5, z_lag10]),
                                ['lag5', 'lag10']),
                'long_term': (np.column_stack([z_lag10, z_lag15, z_lag20]),
                              ['lag10', 'lag15', 'lag20']),
            }

            for scale_name, (X_base, feat_names) in lag_configs.items():
                X = X_base.copy()
                names = feat_names[:]

                if self.use_lasso_filter and X.shape[1] > 1:
                    X, names, dropped = self._lasso_filter(X, j_series, names)

                if self.use_bic_selection and X.shape[1] > 1:
                    X, names = self._bic_select_lags(X, j_series, names)

                if X.shape[1] < 1:
                    continue

                reg, r2, f_stat, p_val, vif, collin, model_type = self._ols_regression(X, j_series)
                if reg is None:
                    continue

                row = {
                    'grid_x': gx, 'grid_y': gy,
                    'r_squared': r2, 'f_stat': f_stat, 'p_value': p_val,
                    'significant': p_val < self.significance,
                    'n_obs': len(j_series),
                    'has_collinearity': collin,
                    'model_type': model_type,
                    'selected_features': ','.join(names),
                    'n_features': len(names),
                }

                for ci, cn in enumerate(names):
                    row[f'coef_{cn}'] = reg.coef_[ci]
                if len(vif) == len(names):
                    for ci, cn in enumerate(names):
                        row[f'vif_{cn}'] = vif[ci]
                    row['max_vif'] = np.max(vif)

                results[scale_name].append(row)

        for scale in results:
            if results[scale]:
                results[scale] = pd.DataFrame(results[scale])
                p_vals = results[scale]['p_value'].values
                if len(p_vals) > 0:
                    sig, q_vals = fdr_correction(p_vals, alpha=0.05)
                    results[scale]['q_value'] = q_vals
                    results[scale]['fdr_significant'] = sig
            else:
                results[scale] = pd.DataFrame()

        return results


class GridDynamicWeightCluster:
    def __init__(self, eps=0.7, min_samples=5, logistic_k=1.7, logistic_e=8):
        self.eps = eps
        self.min_samples = min_samples
        self.logistic_k = logistic_k
        self.logistic_e = logistic_e

    def _logistic_weight(self, level):
        return 1.0 / (1.0 + np.exp(-self.logistic_e * (self.logistic_k - level)))

    def _compute_local_density(self, coords):
        from scipy.spatial import cKDTree
        k = min(self.min_samples * 2, len(coords) - 1)
        if k < 1:
            return np.ones(len(coords))
        tree = cKDTree(coords)
        distances, _ = tree.query(coords, k=k + 1)
        avg_dist = np.mean(distances[:, 1:], axis=1)
        density = 1.0 / (avg_dist + 1e-8)
        density = (density - density.min()) / (density.max() - density.min() + 1e-8)
        return density

    def fit(self, grid_data, threshold=2):
        drought = grid_data[grid_data['zaihuang_level'] >= threshold].copy()
        if len(drought) == 0:
            self.labels_ = np.array([])
            self.n_clusters_ = 0
            return self

        self.drought_data_ = drought
        features = drought[['grid_x', 'grid_y', 'year', 'zaihuang_level']].values
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        coords = drought[['grid_x', 'grid_y']].values
        density = self._compute_local_density(coords)

        levels = drought['zaihuang_level'].values
        logistic_w = np.array([self._logistic_weight(l) for l in levels])

        w_spatial = 1.0 + 0.5 * (1 - density)
        w_temporal = 0.3
        w_level = 0.1 * (0.5 + logistic_w)

        n = len(features_scaled)
        dist_matrix = np.zeros((n, n))
        for i in range(n):
            dx = features_scaled[i, 0] - features_scaled[:, 0]
            dy = features_scaled[i, 1] - features_scaled[:, 1]
            dt = np.abs(features_scaled[i, 2] - features_scaled[:, 2])
            dl = np.abs(features_scaled[i, 3] - features_scaled[:, 3])
            dist_matrix[i] = np.sqrt(w_spatial[i] * dx ** 2 + w_spatial[i] * dy ** 2) + w_temporal * dt + w_level[i] * dl

        db = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric='precomputed')
        db.fit(dist_matrix)
        self.labels_ = db.labels_
        self.n_clusters_ = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
        self.avg_spatial_weight_ = np.mean(w_spatial)
        self.avg_level_weight_ = np.mean(w_level)
        return self


def run_grid_analysis():
    print("=" * 60)
    print("格网化时空分析 (v3核心流程)")
    print("=" * 60)

    print("\n构建1°×1°全时段格网数据 (扩展时间序列)...")
    try:
        grid_data = build_full_grid_data(grid_size=1.0, use_extended=True)
        n_years = grid_data['year'].nunique()
        n_grids = grid_data.groupby(['grid_x', 'grid_y']).ngroups
        print(f"全时段格网数据: {len(grid_data)} 条, {n_years} 年, {n_grids} 格网单元")
    except Exception as e:
        print(f"全时段格网构建失败: {e}, 尝试加载旧格网数据")
        try:
            grid_data = load_grid_data()
            print(f"旧格网数据: {len(grid_data)} 条")
        except Exception as e2:
            print(f"旧格网数据也加载失败: {e2}")
            return None, None, None, None

    print("\n--- 格网化STD-CLUSTER迁移分析 (替代旧行政点分析) ---")
    grid_summary = grid_data[grid_data['zaihuang_severity'] > 0].groupby(['grid_x', 'grid_y']).agg(
        zaihuang_level=('zaihuang_level', 'max'),
        zaihuang_count=('zaihuang_count', 'sum'),
        zaihuang_severity=('zaihuang_severity', 'sum'),
        year_mean=('year', 'mean'),
    ).reset_index()
    grid_summary['year'] = grid_summary['year_mean']
    print(f"  格网摘要: {len(grid_summary)} 个非空格网单元")

    grid_cluster = GridSTDCluster(
        eps1=1.0, eps2=2.0, min_samples=3,
        use_logistic_weight=True, logistic_k=1.7, logistic_e=8,
        zaihuang_threshold=2,
    )
    grid_cluster.fit(grid_summary)
    print(f"格网化聚类: {grid_cluster.n_clusters_} 个灾荒簇")

    trajectories = grid_cluster.compute_migration_trajectory()
    if trajectories:
        print(f"计算到 {len(trajectories)} 条格网化迁移轨迹")
        direction_counts = {}
        rotation_counts = {}
        displacements = []
        nonzero_displacements = []
        for cid, traj in trajectories.items():
            d = traj['migration_direction']
            r = traj['rotation']
            direction_counts[d] = direction_counts.get(d, 0) + 1
            rotation_counts[r] = rotation_counts.get(r, 0) + 1
            displacements.append(traj['total_displacement'])
            if traj['total_displacement'] > 0:
                nonzero_displacements.append(traj['total_displacement'])

        print("  迁移方向分布:")
        for d, c in sorted(direction_counts.items(), key=lambda x: -x[1]):
            print(f"    {d}: {c} 条轨迹")
        print("  旋转方向分布:")
        for r, c in sorted(rotation_counts.items(), key=lambda x: -x[1]):
            print(f"    {r}: {c} 条轨迹")
        print(f"  非零位移轨迹: {len(nonzero_displacements)}/{len(displacements)} "
              f"({len(nonzero_displacements)/len(displacements)*100:.1f}%)")
        if nonzero_displacements:
            print(f"  非零位移均值: {np.mean(nonzero_displacements):.4f}°")

    traj_rows = []
    for cid, traj in trajectories.items():
        traj_rows.append({
            'cluster_id': cid,
            'migration_direction': traj['migration_direction'],
            'migration_direction_deg': traj['migration_direction_deg'],
            'rotation': traj['rotation'],
            'total_displacement': traj['total_displacement'],
            'path_length': traj['path_length'],
            'avg_speed': traj['avg_speed'],
            'duration': traj['duration'],
            'n_years': traj['n_years'],
            'n_grid_cells': traj['n_grid_cells_total'],
        })
    if traj_rows:
        pd.DataFrame(traj_rows).to_excel(
            os.path.join(OUTPUT_DIR, "grid_migration_trajectories.xlsx"),
            index=False, engine='openpyxl'
        )
        print(f"  迁移轨迹已保存至 {OUTPUT_DIR}/grid_migration_trajectories.xlsx")

    print("\n--- 格网化Granger因果推断 (替代失效的聚类级分析) ---")
    gc_analyzer = GridGrangerCausality(max_lag=20, significance=0.05, min_obs=30)
    gc_grid_df = gc_analyzer.analyze_grid_causality(grid_data)

    if len(gc_grid_df) > 0:
        print(f"格网因果分析完成: {len(gc_grid_df)} 个格网单元")

        causal_cells = gc_grid_df[gc_grid_df['causal_direction'] != 'none']
        print(f"存在因果关系的格网: {len(causal_cells)}/{len(gc_grid_df)}")

        if len(causal_cells) > 0:
            print("\n因果方向分布:")
            print(causal_cells['causal_direction'].value_counts().to_string())

            z_to_j = causal_cells[causal_cells['gc_z_to_j_causal']]
            if len(z_to_j) > 0:
                print(f"\n灾荒→进士因果格网: {len(z_to_j)}")
                print(f"  最优滞后分布: {z_to_j['gc_z_to_j_lag'].value_counts().sort_index().to_string()}")
                print(f"  平均滞后: {z_to_j['gc_z_to_j_lag'].mean():.1f} 年")
                print(f"  中位滞后: {z_to_j['gc_z_to_j_lag'].median():.0f} 年")

        p_values = gc_grid_df['gc_z_to_j_pval'].values
        if len(p_values) > 0:
            sig, q_values = fdr_correction(p_values, alpha=0.05)
            gc_grid_df['gc_z_to_j_qval'] = q_values
            gc_grid_df['gc_z_to_j_fdr_sig'] = sig
            print(f"\nFDR校正后显著 (q<0.05): {sig.sum()} 个格网")

            fdr_sig = gc_grid_df[gc_grid_df['gc_z_to_j_fdr_sig']]
            if len(fdr_sig) > 0:
                print("  FDR显著格网详情:")
                for _, row in fdr_sig.iterrows():
                    lag_scale = "短期" if row['gc_z_to_j_lag'] <= 5 else "中期" if row['gc_z_to_j_lag'] <= 10 else "长期"
                    print(f"    ({row['grid_x']:.1f}, {row['grid_y']:.1f}): "
                          f"滞后={row['gc_z_to_j_lag']}年[{lag_scale}], "
                          f"F={row['gc_z_to_j_fstat']:.2f}, q={row['gc_z_to_j_qval']:.4f}")

        gc_grid_df.to_excel(
            os.path.join(OUTPUT_DIR, "grid_granger_causality.xlsx"),
            index=False, engine='openpyxl'
        )
        print(f"格网因果结果已保存至 {OUTPUT_DIR}/grid_granger_causality.xlsx")

    print("\n--- 分层假说检验 (短期/中期/长期) ---")
    if len(gc_grid_df) > 0:
        z_to_j_cells = gc_grid_df[gc_grid_df['gc_z_to_j_causal']]
        if len(z_to_j_cells) > 0:
            short_lag = z_to_j_cells[z_to_j_cells['gc_z_to_j_lag'] <= 5]
            medium_lag = z_to_j_cells[(z_to_j_cells['gc_z_to_j_lag'] > 5) & (z_to_j_cells['gc_z_to_j_lag'] <= 10)]
            long_lag = z_to_j_cells[z_to_j_cells['gc_z_to_j_lag'] > 10]

            print(f"分层假说检验结果:")
            print(f"  短期响应 (滞后1-5年): {len(short_lag)} 个格网 — 直接经济冲击")
            print(f"  中期影响 (滞后6-10年): {len(medium_lag)} 个格网 — 教育资源耗竭")
            print(f"  长期影响 (滞后11-20年): {len(long_lag)} 个格网 — 社会结构性影响")

            if 'gc_z_to_j_fdr_sig' in gc_grid_df.columns:
                fdr_z = gc_grid_df[gc_grid_df['gc_z_to_j_fdr_sig'] & gc_grid_df['gc_z_to_j_causal']]
                if len(fdr_z) > 0:
                    fdr_short = fdr_z[fdr_z['gc_z_to_j_lag'] <= 5]
                    fdr_medium = fdr_z[(fdr_z['gc_z_to_j_lag'] > 5) & (fdr_z['gc_z_to_j_lag'] <= 10)]
                    fdr_long = fdr_z[fdr_z['gc_z_to_j_lag'] > 10]
                    print(f"\n  FDR校正后分层结果:")
                    print(f"    短期 (1-5年): {len(fdr_short)} 个格网")
                    print(f"    中期 (6-10年): {len(fdr_medium)} 个格网")
                    print(f"    长期 (11-20年): {len(fdr_long)} 个格网")

    print("\n--- 格网衍生特征与多尺度分层因果模型 (LASSO+BIC) ---")
    grid_enriched = compute_grid_derived_features(grid_data)
    print(f"衍生特征计算完成: {len(grid_enriched.columns)} 列")
    print(f"  基础特征: cumulative_severity, drought_duration, consecutive_drought_years")
    print(f"  新增特征: max_severity_5yr, drought_frequency_10yr, severity_intensity")
    print(f"  滞后特征: zaihuang_lag1/3/5/10/15/20, jinshi_lag1/3")
    print(f"  移动平均: zaihuang_ma5, jinshi_ma5")

    ms_model = MultiScaleCausalModel(significance=0.05, use_ridge_when_collinear=True, vif_threshold=10.0,
                                     use_lasso_filter=True, use_bic_selection=True)
    stratified_results = ms_model.fit_stratified_model(grid_enriched)

    for scale_name, scale_df in stratified_results.items():
        if len(scale_df) > 0:
            n_sig = scale_df['significant'].sum()
            n_fdr = scale_df['fdr_significant'].sum() if 'fdr_significant' in scale_df.columns else 0
            avg_r2 = scale_df['r_squared'].mean()
            n_collinear = scale_df['has_collinearity'].sum() if 'has_collinearity' in scale_df.columns else 0
            n_ridge = (scale_df['model_type'] == 'ridge').sum() if 'model_type' in scale_df.columns else 0
            print(f"\n  {scale_name} 模型 (LASSO+BIC筛选):")
            print(f"    格网数: {len(scale_df)}, 显著: {n_sig}, FDR显著: {n_fdr}")
            print(f"    平均R²: {avg_r2:.4f}")
            print(f"    共线性格网 (VIF>10): {n_collinear}, 自动切换岭回归: {n_ridge}")
            if 'selected_features' in scale_df.columns:
                feat_dist = scale_df['selected_features'].value_counts().head(5)
                print(f"    最常见特征组合:")
                for feat, cnt in feat_dist.items():
                    print(f"      {feat}: {cnt} 个格网")
            if 'max_vif' in scale_df.columns:
                print(f"    VIF统计: max={scale_df['max_vif'].max():.1f}, "
                      f"mean={scale_df['max_vif'].mean():.1f}, "
                      f"median={scale_df['max_vif'].median():.1f}")
            if n_fdr > 0:
                sig_cells = scale_df[scale_df['fdr_significant']]
                print(f"    FDR显著格网坐标:")
                for _, row in sig_cells.head(5).iterrows():
                    vif_info = f", maxVIF={row['max_vif']:.1f}" if 'max_vif' in row else ""
                    model_info = f", model={row['model_type']}" if 'model_type' in row else ""
                    feat_info = f", features={row['selected_features']}" if 'selected_features' in row else ""
                    print(f"      ({row['grid_x']:.1f}, {row['grid_y']:.1f}): R²={row['r_squared']:.4f}, "
                          f"p={row['p_value']:.4f}, q={row['q_value']:.4f}{vif_info}{model_info}{feat_info}")

    if len(gc_grid_df) > 0 and 'gc_z_to_j_fdr_sig' in gc_grid_df.columns:
        fdr_sig_grids = gc_grid_df[gc_grid_df['gc_z_to_j_fdr_sig']]
        if len(fdr_sig_grids) > 0:
            print(f"\n--- 靶向分析: 仅对Granger FDR显著格网建立多尺度模型 ---")
            targeted_results = ms_model.fit_stratified_model(grid_enriched, target_grids=fdr_sig_grids)
            for scale_name, scale_df in targeted_results.items():
                if len(scale_df) > 0:
                    n_sig = scale_df['significant'].sum()
                    n_fdr = scale_df['fdr_significant'].sum() if 'fdr_significant' in scale_df.columns else 0
                    avg_r2 = scale_df['r_squared'].mean()
                    print(f"  靶向{scale_name}: {len(scale_df)}格网, {n_sig}显著, {n_fdr}FDR显著, R²={avg_r2:.4f}")
                    if n_sig > 0:
                        sig_cells = scale_df[scale_df['significant']]
                        for _, row in sig_cells.head(3).iterrows():
                            feat_info = f", features={row['selected_features']}" if 'selected_features' in row else ""
                            print(f"    ({row['grid_x']:.1f}, {row['grid_y']:.1f}): "
                                  f"R²={row['r_squared']:.4f}, p={row['p_value']:.4f}{feat_info}")

            if all(len(targeted_results[s]) == 0 for s in targeted_results):
                print("  靶向分析: 所有FDR显著格网在多变量模型中均不显著")
                print("  → 说明灾荒影响可能被衍生特征部分中介, 这本身是重要发现")

    print("\n--- 格网动态权重聚类 (融合动态权重与格网化) ---")
    dw_cluster = GridDynamicWeightCluster(eps=1.2, min_samples=3)
    dw_cluster.fit(grid_summary, threshold=2)
    print(f"格网动态权重聚类: {dw_cluster.n_clusters_} 个灾荒簇")
    if hasattr(dw_cluster, 'avg_spatial_weight_'):
        print(f"  平均空间权重: {dw_cluster.avg_spatial_weight_:.4f}")
        print(f"  平均级别权重: {dw_cluster.avg_level_weight_:.4f}")

    print("\n--- 格网置换检验 (环形时间平移+互相关, 替代旧版) ---")
    from src.analysis.cluster_compare import grid_permutation_test
    perm_result = grid_permutation_test(grid_data, n_permutations=1000, max_lag=20)

    grid_enriched.to_csv(
        os.path.join(OUTPUT_DIR, "grid_data_enriched.csv"),
        index=False
    )
    print(f"\n增强格网数据已保存至 {OUTPUT_DIR}/grid_data_enriched.csv")

    for scale_name, scale_df in stratified_results.items():
        if len(scale_df) > 0:
            scale_df.to_excel(
                os.path.join(OUTPUT_DIR, f"multiscale_causal_{scale_name}.xlsx"),
                index=False, engine='openpyxl'
            )

    return grid_data, grid_cluster, trajectories, gc_grid_df


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    run_grid_analysis()
