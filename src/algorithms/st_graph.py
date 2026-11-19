import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


class SpatialTemporalGraph:
    def __init__(self, spatial_k=10, temporal_window=20):
        self.spatial_k = spatial_k
        self.temporal_window = temporal_window

    def build(self, data, coord_cols, time_col, feature_cols=None):
        coords = data[coord_cols].values
        times = data[time_col].values
        n = len(data)

        spatial_graph = self._build_spatial_graph(coords)
        temporal_graph = self._build_temporal_graph(times)
        st_graph = self._build_st_graph_from_adj(spatial_graph, temporal_graph)

        features = data[feature_cols].values if feature_cols else coords
        node_features = self._compute_node_features(data, coords, times, spatial_graph)

        self.spatial_adj = spatial_graph
        self.temporal_adj = temporal_graph
        self.st_adj = st_graph
        self.node_features = node_features
        self.n_nodes = n
        self.coords = coords
        self.times = times

        return self

    def _build_spatial_graph(self, coords):
        k = min(self.spatial_k, len(coords) - 1)
        nbrs = NearestNeighbors(n_neighbors=k + 1, metric='euclidean').fit(coords)
        distances, indices = nbrs.kneighbors(coords)

        n = len(coords)
        adj = np.zeros((n, n))
        for i in range(n):
            for j_idx in range(1, k + 1):
                j = indices[i, j_idx]
                dist = distances[i, j_idx]
                adj[i, j] = 1.0 / (dist + 1e-8)
                adj[j, i] = 1.0 / (dist + 1e-8)

        adj = adj / (adj.max() + 1e-8)
        return adj

    def _build_temporal_graph(self, times):
        n = len(times)
        adj = np.zeros((n, n))
        for i in range(n):
            time_diff = np.abs(times - times[i])
            mask = (time_diff > 0) & (time_diff <= self.temporal_window)
            adj[i, mask] = 1.0 / (time_diff[mask] + 1e-8)

        adj = adj / (adj.max() + 1e-8)
        return adj

    def _build_st_graph_from_adj(self, spatial_adj, temporal_adj):
        st = 0.5 * spatial_adj + 0.5 * temporal_adj
        st[st < 0.01] = 0
        return st

    def _compute_node_features(self, data, coords, times, spatial_adj):
        n = len(data)
        degree = spatial_adj.sum(axis=1)

        features = np.zeros((n, 8))
        features[:, 0] = coords[:, 0]
        features[:, 1] = coords[:, 1]
        features[:, 2] = times
        features[:, 3] = degree

        if 'level' in data.columns:
            features[:, 4] = data['level'].values
        elif 'EntryRank' in data.columns:
            features[:, 4] = data['level'].values if 'level' in data.columns else 0

        for i in range(n):
            neighbors = np.where(spatial_adj[i] > 0)[0]
            if len(neighbors) > 0:
                features[i, 5] = np.mean(times[neighbors]) - times[i]
                features[i, 6] = np.std(coords[neighbors, 0]) if len(neighbors) > 1 else 0
                features[i, 7] = np.std(coords[neighbors, 1]) if len(neighbors) > 1 else 0

        scaler = StandardScaler()
        features = scaler.fit_transform(features)
        return features

    def get_graph_statistics(self):
        stats = {
            'n_nodes': self.n_nodes,
            'spatial_edges': int((self.spatial_adj > 0).sum() / 2),
            'temporal_edges': int((self.temporal_adj > 0).sum() / 2),
            'st_edges': int((self.st_adj > 0).sum() / 2),
            'spatial_density': (self.spatial_adj > 0).sum() / (self.n_nodes ** 2),
            'temporal_density': (self.temporal_adj > 0).sum() / (self.n_nodes ** 2),
            'avg_spatial_degree': self.spatial_adj.sum(axis=1).mean(),
            'avg_temporal_degree': self.temporal_adj.sum(axis=1).mean(),
        }
        return stats

    def graph_based_clustering(self, n_clusters=None):
        from sklearn.cluster import SpectralClustering

        adj = self.st_adj.copy()
        adj[adj < 0.01] = 0

        if n_clusters is None:
            eigenvalues = np.linalg.eigvalsh(adj)
            eigenvalues = np.sort(eigenvalues)[::-1]
            gaps = np.diff(eigenvalues[:30])
            n_clusters = max(2, np.argmax(gaps[:20]) + 2)

        n_clusters = min(n_clusters, self.n_nodes - 1)

        try:
            sc = SpectralClustering(
                n_clusters=n_clusters,
                affinity='precomputed',
                random_state=42,
                assign_labels='kmeans',
            )
            labels = sc.fit_predict(adj)
        except Exception:
            from sklearn.cluster import KMeans
            km = KMeans(n_clusters=n_clusters, random_state=42)
            labels = km.fit_predict(self.node_features)

        return labels


def build_zaihuang_graph(data, spatial_k=10, temporal_window=20):
    graph = SpatialTemporalGraph(spatial_k=spatial_k, temporal_window=temporal_window)
    graph.build(
        data,
        coord_cols=['x', 'y'],
        time_col='year',
        feature_cols=['x', 'y', 'year', 'level']
    )
    return graph


def build_jinshi_graph(data, spatial_k=10, temporal_window=20):
    graph = SpatialTemporalGraph(spatial_k=spatial_k, temporal_window=temporal_window)
    graph.build(
        data,
        coord_cols=['X', 'Y'],
        time_col='EntryYear',
        feature_cols=['X', 'Y', 'EntryYear', 'level']
    )
    return graph
