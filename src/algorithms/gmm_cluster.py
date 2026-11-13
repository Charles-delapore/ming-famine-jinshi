import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler


def find_best_n_gmm(features, n_range, covariance_type='full'):
    bic_values = []
    for n in n_range:
        gmm = GaussianMixture(n_components=n, covariance_type=covariance_type)
        gmm.fit(features)
        bic_values.append(gmm.bic(features))
    best_n = list(n_range)[np.argmin(bic_values)]
    return best_n, bic_values


def cluster_gmm(data, feature_cols, n_components=None, n_range=None, covariance_type='full'):
    features = data[feature_cols].dropna()
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    if n_components is None and n_range is not None:
        n_components, bic_values = find_best_n_gmm(scaled_features, n_range, covariance_type)
        print(f"GMM BIC准则选择最佳聚类数: {n_components}")

    gmm = GaussianMixture(n_components=n_components, covariance_type=covariance_type)
    gmm.fit(scaled_features)
    clusters = gmm.predict(scaled_features)

    result = data.loc[features.index].copy()
    result['cluster'] = clusters
    return result, gmm, scaler


def cluster_zaihuang_gmm(data, params):
    feature_cols = ['x', 'y', 'year', 'level']
    result, gmm, scaler = cluster_gmm(
        data, feature_cols,
        n_range=params.get("n_components_range"),
        covariance_type=params.get("covariance_type", "full"),
    )
    return result, gmm


def cluster_jinshi_gmm(data, params):
    df = data.rename(columns={'X': 'x', 'Y': 'y', 'EntryYear': 'year'})
    feature_cols = ['x', 'y', 'year']
    result, gmm, scaler = cluster_gmm(
        df, feature_cols,
        n_range=params.get("n_components_range"),
        covariance_type=params.get("covariance_type", "full"),
    )
    return result, gmm
