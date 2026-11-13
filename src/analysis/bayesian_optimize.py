import numpy as np
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.preprocessing import StandardScaler


def evaluate_clustering(X, labels):
    valid_mask = labels != -1
    if valid_mask.sum() < 3:
        return -1.0, float('inf'), -1.0
    X_valid = X[valid_mask]
    labels_valid = labels[valid_mask]
    n_clusters = len(set(labels_valid))
    if n_clusters < 2:
        return -1.0, float('inf'), -1.0
    try:
        sil = silhouette_score(X_valid, labels_valid, sample_size=min(5000, len(X_valid)))
    except Exception:
        sil = -1.0
    try:
        db = davies_bouldin_score(X_valid, labels_valid)
    except Exception:
        db = float('inf')
    try:
        ch = calinski_harabasz_score(X_valid, labels_valid)
    except Exception:
        ch = -1.0
    return sil, db, ch


def bayesian_optimize_ssdbcan(data, cluster_func, param_ranges, n_iterations=30):
    from scipy.stats import norm
    from scipy.spatial.distance import cdist

    param_names = list(param_ranges.keys())
    param_bounds = [(param_ranges[k][0], param_ranges[k][1]) for k in param_names]
    n_params = len(param_names)

    observed_params = []
    observed_scores = []

    def objective(params_dict):
        try:
            result, model = cluster_func(data, params_dict)
            labels = model.labels_
            if hasattr(model, 'point_weights_'):
                X = data[['x', 'y', 'year', 'level']].values if 'x' in data.columns else data[['X', 'Y', 'EntryYear', 'level']].values
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
            else:
                X = data[['x', 'y', 'year', 'level']].values if 'x' in data.columns else data[['X', 'Y', 'EntryYear', 'level']].values
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)

            sil, db, ch = evaluate_clustering(X_scaled, labels)
            n_clusters = len(set(labels[labels != -1]))
            noise_ratio = (labels == -1).sum() / len(labels)

            if n_clusters < 2 or n_clusters > 200:
                return -10.0

            score = sil - 0.5 * noise_ratio - 0.001 * abs(n_clusters - 30)
            return score
        except Exception as e:
            print(f"  参数评估失败: {e}")
            return -10.0

    def expected_improvement(x, gp_mean, gp_std, best_y):
        z = (gp_mean - best_y - 0.01) / (gp_std + 1e-8)
        ei = (gp_mean - best_y - 0.01) * norm.cdf(z) + gp_std * norm.pdf(z)
        return ei

    for i in range(min(5, n_iterations)):
        params_dict = {}
        for name, (low, high) in zip(param_names, param_bounds):
            if isinstance(low, int) and isinstance(high, int):
                params_dict[name] = np.random.randint(low, high + 1)
            else:
                params_dict[name] = np.random.uniform(low, high)
        score = objective(params_dict)
        observed_params.append([params_dict[k] for k in param_names])
        observed_scores.append(score)
        print(f"  初始化 {i+1}: {params_dict} -> score={score:.4f}")

    best_idx = np.argmax(observed_scores)
    best_params = observed_params[best_idx]
    best_score = observed_scores[best_idx]

    for i in range(5, n_iterations):
        X_obs = np.array(observed_params)
        y_obs = np.array(observed_scores)

        try:
            from sklearn.gaussian_process import GaussianProcessRegressor
            from sklearn.gaussian_process.kernels import Matern
            kernel = Matern(nu=2.5)
            gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=3, alpha=1e-6)
            gp.fit(X_obs, y_obs)

            n_candidates = 200
            candidates = np.random.uniform(
                [b[0] for b in param_bounds],
                [b[1] for b in param_bounds],
                size=(n_candidates, n_params)
            )
            for j, name in enumerate(param_names):
                if isinstance(param_ranges[name][0], int):
                    candidates[:, j] = np.round(candidates[:, j]).astype(int)

            mu, sigma = gp.predict(candidates, return_std=True)
            ei = expected_improvement(candidates, mu, sigma, best_score)
            next_params = candidates[np.argmax(ei)]

        except Exception:
            next_params = np.array([
                np.random.uniform(b[0], b[1]) for b in param_bounds
            ])

        params_dict = {}
        for j, name in enumerate(param_names):
            val = next_params[j]
            if isinstance(param_ranges[name][0], int):
                val = int(round(val))
            params_dict[name] = val

        score = objective(params_dict)
        observed_params.append([params_dict[k] for k in param_names])
        observed_scores.append(score)

        if score > best_score:
            best_score = score
            best_params = [params_dict[k] for k in param_names]
            print(f"  迭代 {i+1}: 新最优! {params_dict} -> score={score:.4f}")
        else:
            print(f"  迭代 {i+1}: {params_dict} -> score={score:.4f}")

    best_dict = {}
    for j, name in enumerate(param_names):
        best_dict[name] = best_params[j]
        if isinstance(param_ranges[name][0], int):
            best_dict[name] = int(round(best_dict[name]))

    print(f"\n贝叶斯优化完成! 最优参数: {best_dict}, 最优分数: {best_score:.4f}")
    return best_dict, best_score


def optimize_zaihuang_params(data, base_params):
    param_ranges = {
        "eps": (0.3, 1.5),
        "min_samples": (3, 15),
        "max_cluster_size": (50, 200),
    }
    from src.algorithms.ss_dbscan import cluster_zaihuang
    best_params, best_score = bayesian_optimize_ssdbcan(
        data, cluster_zaihuang, param_ranges, n_iterations=20
    )
    best_params["weights"] = base_params["weights"]
    best_params["important_levels"] = base_params["important_levels"]
    return best_params, best_score


def optimize_jinshi_params(data, base_params):
    param_ranges = {
        "eps": (0.3, 1.5),
        "min_samples": (2, 10),
        "max_cluster_size": (50, 200),
    }
    from src.algorithms.ss_dbscan import cluster_jinshi
    best_params, best_score = bayesian_optimize_ssdbcan(
        data, cluster_jinshi, param_ranges, n_iterations=20
    )
    best_params["weights"] = base_params["weights"]
    best_params["important_levels"] = base_params["important_levels"]
    return best_params, best_score
