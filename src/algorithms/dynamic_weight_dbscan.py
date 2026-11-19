import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

from src.data_processing.jinshi_rank import rank_level


class DynamicWeightSSDBSCAN:
    def __init__(self, eps, min_samples, max_cluster_size=100,
                 important_levels=None, n_weight_clusters=5,
                 base_weights=None, use_logistic=True,
                 logistic_k=1.7, logistic_e=8,
                 use_fgs=True, fgs_minpts_range=None):
        self.eps = eps
        self.min_samples = min_samples
        self.max_cluster_size = max_cluster_size
        self.important_levels = important_levels or [4, 5]
        self.n_weight_clusters = n_weight_clusters
        self.base_weights = np.array(base_weights or [1.0, 1.0, 0.3, 0.1])
        self.use_logistic = use_logistic
        self.logistic_k = logistic_k
        self.logistic_e = logistic_e
        self.use_fgs = use_fgs
        self.fgs_minpts_range = fgs_minpts_range or (3, 20)

    def _logistic_weight(self, level):
        return 1.0 / (1.0 + np.exp(-self.logistic_e * (self.logistic_k - level)))

    def _compute_local_density(self, X):
        from scipy.spatial import cKDTree
        coords = X[:, :2]
        k = min(self.min_samples * 2, len(X) - 1)
        if k < 1:
            return np.ones(len(X))
        tree = cKDTree(coords)
        distances, _ = tree.query(coords, k=k + 1)
        avg_dist = np.mean(distances[:, 1:], axis=1)
        density = 1.0 / (avg_dist + 1e-8)
        density = (density - density.min()) / (density.max() - density.min() + 1e-8)
        return density

    def _compute_temporal_variance(self, X):
        from scipy.spatial import cKDTree
        coords = X[:, :2]
        n = len(X)
        if n < 3:
            return np.ones(n)
        tree = cKDTree(coords)
        k = min(20, n - 1)
        temporal_vars = np.zeros(n)
        distances, indices = tree.query(coords, k=k + 1)
        for i in range(n):
            neighbor_years = X[indices[i, 1:], 2]
            temporal_vars[i] = np.std(neighbor_years) if len(neighbor_years) > 1 else 0
        if temporal_vars.max() > temporal_vars.min():
            temporal_vars = (temporal_vars - temporal_vars.min()) / (temporal_vars.max() - temporal_vars.min())
        return temporal_vars

    def _fast_grid_search_minpts(self, X):
        if not self.use_fgs:
            return self.min_samples

        from scipy.spatial import cKDTree
        coords = X[:, :2]
        n = len(X)
        if n < 10:
            return self.min_samples

        tree = cKDTree(coords)
        min_pts_low, min_pts_high = self.fgs_minpts_range
        best_minpts = self.min_samples
        best_score = -1

        for min_pts in range(min_pts_low, min_pts_high + 1):
            k = min(min_pts, n - 1)
            distances, _ = tree.query(coords, k=k + 1)
            avg_k_dist = np.mean(distances[:, 1:])

            local_densities = 1.0 / (distances[:, 1:] + 1e-8)
            density_variance = np.var(np.mean(local_densities, axis=1))

            score = -avg_k_dist - 0.01 * density_variance

            if score > best_score:
                best_score = score
                best_minpts = min_pts

        return best_minpts

    def _adaptive_eps_range(self, X):
        from scipy.spatial import cKDTree
        coords = X[:, :2]
        n = len(X)
        if n < 10:
            return self.eps

        tree = cKDTree(coords)
        k = min(self.min_samples, n - 1)
        distances, _ = tree.query(coords, k=k + 1)
        k_distances = np.sort(distances[:, -1])

        try:
            from kneed import KneeLocator
            kneedle = KneeLocator(
                range(len(k_distances)), k_distances,
                curve='convex', direction='increasing'
            )
            if kneedle.knee is not None:
                adaptive_eps = k_distances[kneedle.knee]
                return float(np.clip(adaptive_eps, self.eps * 0.8, self.eps * 1.2))
        except ImportError:
            pass

        d_diff = np.diff(k_distances)
        elbow_idx = np.argmax(d_diff > 2 * np.median(d_diff))
        if elbow_idx > 0:
            adaptive_eps = k_distances[elbow_idx]
            return float(np.clip(adaptive_eps, self.eps * 0.8, self.eps * 1.2))

        return self.eps

    def _learn_dynamic_weights(self, X):
        n = len(X)
        density = self._compute_local_density(X)
        temporal_var = self._compute_temporal_variance(X)

        weights = np.zeros((n, 4))
        weights[:, 0] = self.base_weights[0]
        weights[:, 1] = self.base_weights[1]
        weights[:, 2] = self.base_weights[2] * (0.5 + temporal_var)
        weights[:, 3] = self.base_weights[3] * (1.5 - density)

        if self.use_logistic and X.shape[1] >= 4:
            levels = X[:, 3]
            logistic_w = np.array([self._logistic_weight(l) for l in levels])
            weights[:, 3] = weights[:, 3] * (0.5 + logistic_w)

        weights = np.clip(weights, 0.05, 3.0)
        return weights

    def _compute_distance_matrix(self, X, point_weights):
        n = len(X)
        chunk_size = min(2000, n)
        dist_matrix = np.zeros((n, n))

        for start in range(0, n, chunk_size):
            end = min(start + chunk_size, n)
            w = point_weights[start:end]

            dx = X[start:end, 0].reshape(-1, 1) - X[:, 0].reshape(1, -1)
            dy = X[start:end, 1].reshape(-1, 1) - X[:, 1].reshape(1, -1)
            dt = np.abs(X[start:end, 2].reshape(-1, 1) - X[:, 2].reshape(1, -1))
            dl = np.abs(X[start:end, 3].reshape(-1, 1) - X[:, 3].reshape(1, -1))

            spatial_dist = np.sqrt(w[:, 0:1] * dx ** 2 + w[:, 1:2] * dy ** 2)
            temporal_dist = w[:, 2:3] * dt
            level_dist = w[:, 3:4] * dl
            dist_matrix[start:end] = spatial_dist + temporal_dist + level_dist

        return dist_matrix

    def fit(self, X):
        X = np.asarray(X, dtype=np.float64)
        n = len(X)
        self.labels_ = np.zeros(n, dtype=int)
        self.core_samples_ = np.zeros(n, dtype=bool)
        C = 0

        if self.use_fgs:
            optimized_minpts = self._fast_grid_search_minpts(X)
            if optimized_minpts != self.min_samples:
                print(f"  FGS优化MinPts: {self.min_samples} -> {optimized_minpts}")
                self.min_samples = optimized_minpts

        adaptive_eps = self._adaptive_eps_range(X)
        if abs(adaptive_eps - self.eps) > 0.01:
            print(f"  自适应Eps: {self.eps:.3f} -> {adaptive_eps:.3f}")
            self.eps = adaptive_eps

        print(f"  学习动态权重 ({n}个数据点, Logistic={'开启' if self.use_logistic else '关闭'})...")
        point_weights = self._learn_dynamic_weights(X)
        self.point_weights_ = point_weights

        print(f"  计算动态距离矩阵 ({n}x{n})...")
        dist_matrix = self._compute_distance_matrix(X, point_weights)
        print(f"  距离矩阵计算完成，开始聚类...")

        for P in range(n):
            if self.labels_[P] != 0:
                continue
            neighbors = self._region_query(P, dist_matrix)
            if len(neighbors) < self.min_samples:
                self.labels_[P] = -1
            else:
                C += 1
                self._grow_cluster(P, neighbors, C, dist_matrix, X)
            if P % 1000 == 0 and P > 0:
                print(f"  已处理 {P}/{n} 个点, 当前聚类数: {C}")

        self.n_clusters_ = C
        return self

    def _grow_cluster(self, P, neighbors, C, dist_matrix, X):
        self.labels_[P] = C
        self.core_samples_[P] = True
        current_cluster_size = 1
        i = 0
        while i < len(neighbors):
            if self.max_cluster_size and current_cluster_size >= self.max_cluster_size:
                break
            Pn = neighbors[i]
            if self.labels_[Pn] == -1:
                self.labels_[Pn] = C
                current_cluster_size += 1
            elif self.labels_[Pn] == 0:
                self.labels_[Pn] = C
                current_cluster_size += 1
                new_neighbors = self._region_query(Pn, dist_matrix)
                if len(new_neighbors) >= self.min_samples and self._is_important(X[Pn]):
                    self.core_samples_[Pn] = True
                    neighbors += new_neighbors
            i += 1

    def _region_query(self, P, dist_matrix):
        indices = np.where((dist_matrix[P] <= self.eps) & (np.arange(len(dist_matrix[P])) != P))[0]
        return indices.tolist()

    def _is_important(self, attrs):
        if self.use_logistic:
            return self._logistic_weight(attrs[3]) > 0.5
        return attrs[3] in self.important_levels


def cluster_zaihuang_dynamic(data, params):
    data = data.copy()
    data['x_orig'] = data['x'].values
    data['y_orig'] = data['y'].values
    data['year_orig'] = data['year'].values
    scaler = StandardScaler()
    scaled_cols = scaler.fit_transform(data[['x', 'y', 'year']])
    features = np.hstack((scaled_cols, data[['level']].values))

    clusterer = DynamicWeightSSDBSCAN(
        eps=params["eps"],
        min_samples=params["min_samples"],
        max_cluster_size=params["max_cluster_size"],
        important_levels=params["important_levels"],
        base_weights=params.get("weights", [1.0, 1.0, 0.3, 0.1]),
        use_logistic=params.get("use_logistic", True),
        logistic_k=params.get("logistic_k", 1.7),
        logistic_e=params.get("logistic_e", 8),
        use_fgs=params.get("use_fgs", True),
    ).fit(features)

    data['cluster'] = clusterer.labels_
    data['x'] = data['x_orig']
    data['y'] = data['y_orig']
    data['year'] = data['year_orig']
    data = data.drop(columns=['x_orig', 'y_orig', 'year_orig'])
    return data, clusterer


def cluster_jinshi_dynamic(data, params):
    # Normalize ranks with the shared module (src/data_processing/jinshi_rank):
    # the old literal filter `第1甲|第2甲` silently dropped Chinese-numeral
    # ranks (第一甲/第二甲). Keep 1甲/2甲 only, drop 3甲 and unparsed rows.
    important_data = data.dropna(subset=['EntryRank']).copy()
    important_data['level'] = important_data['EntryRank'].map(rank_level)
    important_data = important_data[important_data['level'].isin([1, 2])]
    important_data = important_data.dropna(subset=['EntryYear'])

    features = important_data[['X', 'Y', 'EntryYear']].values
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    scaled_features = np.hstack((scaled_features, important_data[['level']].values))

    clusterer = DynamicWeightSSDBSCAN(
        eps=params["eps"],
        min_samples=params["min_samples"],
        max_cluster_size=params["max_cluster_size"],
        important_levels=params["important_levels"],
        base_weights=params.get("weights", [1.0, 1.0, 0.3, 0.1]),
        use_logistic=params.get("use_logistic", True),
        logistic_k=params.get("logistic_k", 1.7),
        logistic_e=params.get("logistic_e", 8),
        use_fgs=params.get("use_fgs", True),
    ).fit(scaled_features)

    important_data['cluster'] = clusterer.labels_
    return important_data, clusterer
