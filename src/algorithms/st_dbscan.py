import numpy as np
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import DBSCAN
from sklearn.utils import check_array


class STDBSCANExtended:
    def __init__(self, eps1=0.5, eps2=1, eps3=1, min_samples=5, metric='euclidean', n_jobs=-1):
        self.eps1 = eps1
        self.eps2 = eps2
        self.eps3 = eps3
        self.min_samples = min_samples
        self.metric = metric
        self.n_jobs = n_jobs

    def fit(self, X):
        X = check_array(X)
        time_dist = pdist(X[:, 0].reshape(-1, 1), 'euclidean')
        level_dist = pdist(X[:, 3].reshape(-1, 1), 'euclidean')
        euc_dist = pdist(X[:, 1:3], 'euclidean')

        condition = (time_dist <= self.eps2) & (level_dist <= self.eps3)
        dist = np.where(condition, euc_dist, 2 * self.eps1)

        db = DBSCAN(eps=self.eps1, min_samples=self.min_samples, metric='precomputed')
        db.fit(squareform(dist))
        self.labels_ = db.labels_
        return self


def cluster_zaihuang_st(data, params):
    features = data[['year', 'x', 'y', 'level']].values
    model = STDBSCANExtended(
        eps1=params["eps1"],
        eps2=params["eps2"],
        eps3=params["eps3"],
        min_samples=params["min_samples"],
    )
    model.fit(features)
    data['cluster'] = model.labels_
    return data, model
