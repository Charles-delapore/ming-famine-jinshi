import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class RunTheoryExtractor:
    def __init__(self, level_threshold=3, min_duration=1):
        self.level_threshold = level_threshold
        self.min_duration = min_duration

    def extract_events(self, data, coord_col='code', time_col='year', level_col='level'):
        events = []
        for code, group in data.groupby(coord_col):
            group = group.sort_values(time_col)
            years = group[time_col].values
            levels = group[level_col].values

            in_event = False
            event_start = None
            event_levels = []

            for i in range(len(years)):
                if levels[i] >= self.level_threshold:
                    if not in_event:
                        in_event = True
                        event_start = years[i]
                        event_levels = [levels[i]]
                    else:
                        event_levels.append(levels[i])
                else:
                    if in_event:
                        duration = years[i - 1] - event_start + 1
                        if duration >= self.min_duration:
                            events.append({
                                'code': code,
                                'start_year': event_start,
                                'end_year': years[i - 1],
                                'duration': duration,
                                'max_level': max(event_levels),
                                'avg_level': np.mean(event_levels),
                                'severity': sum(event_levels),
                            })
                        in_event = False
                        event_levels = []

            if in_event:
                duration = years[-1] - event_start + 1
                if duration >= self.min_duration:
                    events.append({
                        'code': code,
                        'start_year': event_start,
                        'end_year': years[-1],
                        'duration': duration,
                        'max_level': max(event_levels),
                        'avg_level': np.mean(event_levels),
                        'severity': sum(event_levels),
                    })

        events_df = pd.DataFrame(events)
        return events_df


class STDCluster:
    def __init__(self, eps1=1.0, eps2=5, min_samples=3,
                 use_logistic_weight=True, logistic_k=1.7, logistic_e=8,
                 min_cluster_area=0, temporal_overlap_ratio=0.5):
        self.eps1 = eps1
        self.eps2 = eps2
        self.min_samples = min_samples
        self.use_logistic_weight = use_logistic_weight
        self.logistic_k = logistic_k
        self.logistic_e = logistic_e
        self.min_cluster_area = min_cluster_area
        self.temporal_overlap_ratio = temporal_overlap_ratio

    def _logistic_weight(self, level):
        return 1.0 / (1.0 + np.exp(-self.logistic_e * (self.logistic_k - level)))

    def fit(self, events_df, city_coords):
        from sklearn.cluster import DBSCAN

        if len(events_df) == 0:
            self.labels_ = np.array([])
            self.n_clusters_ = 0
            return self

        merged = events_df.merge(city_coords, on='code', how='left')
        merged = merged.dropna(subset=['x', 'y'])

        if self.use_logistic_weight and 'max_level' in merged.columns:
            merged['weight'] = merged['max_level'].apply(self._logistic_weight)
        else:
            merged['weight'] = 1.0

        features = merged[['x', 'y', 'start_year', 'end_year', 'max_level', 'duration']].copy()
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        spatial_dist = np.sqrt(
            (features_scaled[:, 0].reshape(-1, 1) - features_scaled[:, 0].reshape(1, -1)) ** 2 +
            (features_scaled[:, 1].reshape(-1, 1) - features_scaled[:, 1].reshape(1, -1)) ** 2
        )

        temporal_dist = np.minimum(
            np.abs(features_scaled[:, 2].reshape(-1, 1) - features_scaled[:, 2].reshape(1, -1)),
            np.abs(features_scaled[:, 3].reshape(-1, 1) - features_scaled[:, 3].reshape(1, -1))
        )

        condition = temporal_dist <= self.eps2
        dist_matrix = np.where(condition, spatial_dist, 2 * self.eps1)

        if self.use_logistic_weight:
            w = merged['weight'].values
            weight_matrix = 0.5 * (w.reshape(-1, 1) + w.reshape(1, -1))
            dist_matrix = dist_matrix / (weight_matrix + 1e-8)

        db = DBSCAN(eps=self.eps1, min_samples=self.min_samples, metric='precomputed')
        db.fit(dist_matrix)
        self.labels_ = db.labels_
        self.n_clusters_ = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
        self.merged_df = merged
        return self

    def _severity_weighted_centroid(self, cluster_df):
        W = 1.0 / (1.0 + (cluster_df['max_level'].values / (-1.5)) ** 6)
        W = W / (W.sum() + 1e-8)
        cx = np.sum(cluster_df['x'].values * W)
        cy = np.sum(cluster_df['y'].values * W)
        return cx, cy

    def _compute_rotation(self, xs, ys):
        n = len(xs)
        if n < 3:
            return 0.0, 'none'
        beta = sum(
            (xs[i + 1] - xs[i]) * (ys[i + 1] + ys[i])
            for i in range(n - 1)
        )
        if beta > 0:
            return beta, 'clockwise'
        elif beta < 0:
            return beta, 'counterclockwise'
        else:
            return 0.0, 'none'

    def _classify_direction(self, angle_deg):
        angle_deg = angle_deg % 360
        if 337.5 <= angle_deg or angle_deg < 22.5:
            return 'E'
        elif 22.5 <= angle_deg < 67.5:
            return 'NE'
        elif 67.5 <= angle_deg < 112.5:
            return 'N'
        elif 112.5 <= angle_deg < 157.5:
            return 'NW'
        elif 157.5 <= angle_deg < 202.5:
            return 'W'
        elif 202.5 <= angle_deg < 247.5:
            return 'SW'
        elif 247.5 <= angle_deg < 292.5:
            return 'S'
        else:
            return 'SE'

    def compute_cluster_characteristics(self):
        if not hasattr(self, 'merged_df') or len(self.merged_df) == 0:
            return pd.DataFrame()

        df = self.merged_df.copy()
        df['cluster'] = self.labels_

        results = []
        for cid in sorted(set(self.labels_)):
            if cid == -1:
                continue
            cluster = df[df['cluster'] == cid]

            cx, cy = self._severity_weighted_centroid(cluster)

            ts = cluster['start_year'].min()
            te = cluster['end_year'].max()
            du = te - ts + 1

            dv = cluster['duration'].sum()

            threshold = self.logistic_k if self.use_logistic_weight else 1.0
            ds = np.sum(np.abs(threshold - cluster['max_level'].values))

            results.append({
                'cluster_id': cid,
                'n_events': len(cluster),
                'start_year': ts,
                'end_year': te,
                'duration': du,
                'centroid_x': cx,
                'centroid_y': cy,
                'volume': dv,
                'severity': ds,
                'max_level': cluster['max_level'].max(),
                'avg_severity': cluster['severity'].mean(),
                'total_severity': cluster['severity'].sum(),
                'n_locations': cluster['code'].nunique(),
            })

        return pd.DataFrame(results)

    def compute_migration_trajectory(self):
        if not hasattr(self, 'merged_df') or len(self.merged_df) == 0:
            return {}

        df = self.merged_df.copy()
        df['cluster'] = self.labels_

        trajectories = {}
        for cid in sorted(set(self.labels_)):
            if cid == -1:
                continue
            cluster = df[df['cluster'] == cid]

            yearly_data = []
            for year, year_group in cluster.groupby('start_year'):
                W = 1.0 / (1.0 + (year_group['max_level'].values / (-1.5)) ** 6)
                W = W / (W.sum() + 1e-8)
                cx = np.sum(year_group['x'].values * W)
                cy = np.sum(year_group['y'].values * W)
                yearly_data.append({
                    'year': year,
                    'centroid_x': cx,
                    'centroid_y': cy,
                    'n_events': len(year_group),
                    'total_severity': year_group['severity'].sum(),
                })

            yearly_centers = pd.DataFrame(yearly_data).sort_values('year')

            if len(yearly_centers) >= 2:
                xs = yearly_centers['centroid_x'].values
                ys = yearly_centers['centroid_y'].values

                dx = np.diff(xs)
                dy = np.diff(ys)
                angles = np.arctan2(dy, dx)
                mean_angle = np.mean(angles)

                beta, rotation = self._compute_rotation(xs, ys)

                direction = self._classify_direction(np.degrees(mean_angle))

                total_displacement = np.sqrt(
                    (xs[-1] - xs[0]) ** 2 + (ys[-1] - ys[0]) ** 2
                )

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
                }

        return trajectories


def run_std_cluster_analysis(zaihuang_data, city_data, level_threshold=3):
    print("  游程理论提取灾荒事件...")
    extractor = RunTheoryExtractor(level_threshold=level_threshold, min_duration=1)
    events_df = extractor.extract_events(zaihuang_data)
    print(f"  提取到 {len(events_df)} 个灾荒事件")

    if len(events_df) == 0:
        print("  未提取到灾荒事件，降低阈值重试...")
        extractor = RunTheoryExtractor(level_threshold=1, min_duration=1)
        events_df = extractor.extract_events(zaihuang_data)
        print(f"  降低阈值后提取到 {len(events_df)} 个灾荒事件")

    city_coords = city_data[['code', 'x', 'y']].drop_duplicates('code')

    print("  STD-CLUSTER三维聚类 (含Logistic权重)...")
    std_cluster = STDCluster(
        eps1=1.0, eps2=2.0, min_samples=3,
        use_logistic_weight=True, logistic_k=1.7, logistic_e=8,
    )
    std_cluster.fit(events_df, city_coords)
    print(f"  聚类完成: {std_cluster.n_clusters_} 个灾荒簇")

    characteristics = std_cluster.compute_cluster_characteristics()
    if len(characteristics) > 0:
        print(f"  灾荒簇特征:")
        print(f"    平均持续时间: {characteristics['duration'].mean():.1f} 年")
        print(f"    平均涉及地点: {characteristics['n_locations'].mean():.1f} 个")
        print(f"    最大严重度: {characteristics['severity'].max():.0f}")
        print(f"    平均体积: {characteristics['volume'].mean():.1f}")

    trajectories = std_cluster.compute_migration_trajectory()
    if trajectories:
        print(f"  计算到 {len(trajectories)} 条灾荒迁移轨迹")
        for cid, traj in list(trajectories.items())[:3]:
            print(f"    簇{cid}: 方向={traj['migration_direction']}({traj['migration_direction_deg']:.1f}°), "
                  f"旋转={traj['rotation']}, 位移={traj['total_displacement']:.2f}, "
                  f"路径长度={traj['path_length']:.2f}")

    return events_df, std_cluster, characteristics, trajectories
