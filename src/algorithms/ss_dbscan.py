import numpy as np
from sklearn.preprocessing import StandardScaler


class SSDBSCAN:
    def __init__(self, eps, min_samples, weights, max_cluster_size, important_levels=None):
        self.eps = eps
        self.min_samples = min_samples
        self.weights = weights
        self.max_cluster_size = max_cluster_size
        self.important_levels = important_levels or [4, 5]

    def _compute_distance_matrix(self, X):
        w = self.weights
        dx = X[:, 0].reshape(-1, 1) - X[:, 0].reshape(1, -1)
        dy = X[:, 1].reshape(-1, 1) - X[:, 1].reshape(1, -1)
        dt = np.abs(X[:, 2].reshape(-1, 1) - X[:, 2].reshape(1, -1))
        dl = np.abs(X[:, 3].reshape(-1, 1) - X[:, 3].reshape(1, -1))

        spatial_dist = np.sqrt(w[0] * dx ** 2 + w[1] * dy ** 2)
        temporal_dist = w[2] * dt
        level_dist = w[3] * dl
        return spatial_dist + temporal_dist + level_dist

    def fit(self, X):
        X = np.asarray(X, dtype=np.float64)
        n = len(X)
        self.labels_ = np.zeros(n, dtype=int)
        self.core_samples_ = np.zeros(n, dtype=bool)
        C = 0

        print(f"  计算距离矩阵 ({n}x{n})...")
        dist_matrix = self._compute_distance_matrix(X)
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
        return attrs[3] in self.important_levels


def cluster_zaihuang(data, params):
    data = data.copy()
    data['x_orig'] = data['x'].values
    data['y_orig'] = data['y'].values
    data['year_orig'] = data['year'].values
    scaler = StandardScaler()
    scaled_cols = scaler.fit_transform(data[['x', 'y', 'year']])
    features = np.hstack((scaled_cols, data[['level']].values))

    clusterer = SSDBSCAN(
        eps=params["eps"],
        min_samples=params["min_samples"],
        weights=params["weights"],
        max_cluster_size=params["max_cluster_size"],
        important_levels=params["important_levels"],
    ).fit(features)

    data['cluster'] = clusterer.labels_
    data['x'] = data['x_orig']
    data['y'] = data['y_orig']
    data['year'] = data['year_orig']
    data = data.drop(columns=['x_orig', 'y_orig', 'year_orig'])
    return data, clusterer


def cluster_jinshi(data, params):
    important_data = data.dropna(subset=['EntryRank']).copy()
    important_data = important_data[
        important_data['EntryRank'].str.contains(r'第1甲|第2甲', na=False)
    ]
    important_data = important_data.dropna(subset=['EntryYear'])
    important_data['level'] = important_data['EntryRank'].apply(
        lambda x: 1 if "第1甲" in x else 2
    )

    features = important_data[['X', 'Y', 'EntryYear']].values
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    scaled_features = np.hstack((scaled_features, important_data[['level']].values))

    clusterer = SSDBSCAN(
        eps=params["eps"],
        min_samples=params["min_samples"],
        weights=params["weights"],
        max_cluster_size=params["max_cluster_size"],
        important_levels=params["important_levels"],
    ).fit(scaled_features)

    important_data['cluster'] = clusterer.labels_
    return important_data, clusterer
