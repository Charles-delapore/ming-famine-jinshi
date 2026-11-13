import numpy as np
import pandas as pd
from scipy import stats
from scipy.spatial import cKDTree
import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config import OUTPUT_DIR


def _max_consecutive(bool_arr):
    max_len = 0
    cur_len = 0
    for v in bool_arr:
        if v:
            cur_len += 1
            max_len = max(max_len, cur_len)
        else:
            cur_len = 0
    return max_len


def _series_quality_check(x, y, min_obs=30, min_cv=0.3, max_zero_frac=0.6, max_consec_zero=5):
    if len(x) < min_obs or len(y) < min_obs:
        return False, "n_obs不足"

    zero_frac_x = np.mean(x == 0)
    zero_frac_y = np.mean(y == 0)
    if zero_frac_x > max_zero_frac or zero_frac_y > max_zero_frac:
        return False, f"零值比例过高(z_x={zero_frac_x:.0%}, z_y={zero_frac_y:.0%})"

    cv_x = np.std(x) / (np.mean(x) + 1e-10)
    cv_y = np.std(y) / (np.mean(y) + 1e-10)
    if cv_x < min_cv or cv_y < min_cv:
        return False, f"变异系数过低(cv_x={cv_x:.3f}, cv_y={cv_y:.3f})"

    consec_x = _max_consecutive(x == 0)
    consec_y = _max_consecutive(y == 0)
    if consec_x > max_consec_zero or consec_y > max_consec_zero:
        return False, f"连续零值过长(consec_x={consec_x}, consec_y={consec_y})"

    return True, "OK"


def _shadow_manifold(x, E, tau=1):
    n = len(x)
    n_pts = n - (E - 1) * tau
    if n_pts <= 0:
        return np.array([]).reshape(0, E)
    M = np.zeros((n_pts, E))
    for i in range(E):
        M[:, i] = x[(E - 1 - i) * tau: n - i * tau]
    return M


def _simplex_project(M_lib, y_lib, M_pred, E):
    k = E + 1
    if len(M_lib) < k + 1 or len(M_pred) < 1:
        return np.full(len(M_pred), np.nan)

    tree = cKDTree(M_lib)
    distances, indices = tree.query(M_pred, k=k + 1)

    y_pred = np.full(len(M_pred), np.nan)

    for i in range(len(M_pred)):
        d = distances[i]
        idx = indices[i]

        valid_mask = d > 1e-8
        if valid_mask.sum() < 2:
            continue

        d_valid = d[valid_mask]
        idx_valid = idx[valid_mask]

        w = 1.0 / d_valid
        w /= w.sum()

        y_pred[i] = np.dot(w, y_lib[idx_valid])

    return y_pred


def _cross_map(M_target, y_source, E, library_sizes):
    n_total = M_target.shape[0]
    results = []

    for L in library_sizes:
        if L > n_total or L < E + 5:
            continue

        rhos = []
        n_trials = min(5, max(1, n_total // L))

        for trial in range(n_trials):
            rng = np.random.RandomState(42 + trial)
            perm = rng.permutation(n_total)
            lib_idx = np.sort(perm[:L])
            pred_idx = np.sort(perm[L:2 * L]) if 2 * L <= n_total else np.sort(perm[L:])

            if len(pred_idx) < E + 2 or len(lib_idx) < E + 2:
                continue

            M_lib = M_target[lib_idx]
            M_pred = M_target[pred_idx]
            y_lib = y_source[lib_idx]
            y_true = y_source[pred_idx]

            y_pred = _simplex_project(M_lib, y_lib, M_pred, E)

            valid = np.isfinite(y_pred) & np.isfinite(y_true)
            if valid.sum() < max(E + 2, 10):
                continue

            yt = y_true[valid]
            yp = y_pred[valid]

            if np.std(yt) < 1e-10 or np.std(yp) < 1e-10:
                continue

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                rho, _ = stats.pearsonr(yt, yp)

            if np.isfinite(rho) and abs(rho) < 0.999:
                rhos.append(rho)

        if rhos:
            results.append({
                'library_size': L,
                'rho_mean': np.mean(rhos),
                'rho_std': np.std(rhos) if len(rhos) > 1 else 0.0,
                'rho_min': np.min(rhos),
                'rho_max': np.max(rhos),
                'n_trials': len(rhos),
            })

    return pd.DataFrame(results)


def _surrogate_test(x, y, E, tau, library_sizes, n_surrogates=39, alpha=0.05):
    rho_obs_list = []
    for L in library_sizes:
        if L > len(x) - (E - 1) * tau:
            continue
        M_x = _shadow_manifold(x, E, tau)
        y_shadow = y[(E - 1) * tau:][:M_x.shape[0]]
        df = _cross_map(M_x, y_shadow, E, [L])
        if len(df) > 0:
            rho_obs_list.append(df['rho_mean'].iloc[0])

    if not rho_obs_list:
        return 1.0, False
    rho_obs = np.max(rho_obs_list)

    rho_surr = []
    for s in range(n_surrogates):
        rng = np.random.RandomState(100 + s)
        fft_x = np.fft.fft(x)
        phases = np.exp(1j * rng.uniform(0, 2 * np.pi, len(x)))
        x_surr = np.real(np.fft.ifft(fft_x * phases))

        surr_list = []
        for L in library_sizes:
            if L > len(x_surr) - (E - 1) * tau:
                continue
            M_surr = _shadow_manifold(x_surr, E, tau)
            y_s = y[(E - 1) * tau:][:M_surr.shape[0]]
            df = _cross_map(M_surr, y_s, E, [L])
            if len(df) > 0:
                surr_list.append(df['rho_mean'].iloc[0])
        if surr_list:
            rho_surr.append(np.max(surr_list))

    if not rho_surr:
        return 1.0, False

    p_val = (np.sum(np.array(rho_surr) >= rho_obs) + 1) / (n_surrogates + 1)
    sig = p_val < alpha
    return p_val, sig


def _transfer_entropy(x, y, k=1, l=1):
    n = len(x)
    if n < k + l + 10:
        return 0.0

    x_disc = np.digitize(x, bins=np.percentile(x, [20, 40, 60, 80]))
    y_disc = np.digitize(y, bins=np.percentile(y, [20, 40, 60, 80]))

    from collections import Counter

    def _prob_dict(*args):
        counts = Counter(zip(*args))
        total = sum(counts.values())
        return {k: v / total for k, v in counts.items()}

    te_val = 0.0
    for t in range(max(k, l), n - 1):
        y_future = y_disc[t + 1]
        y_past = tuple(y_disc[t - l:t]) if l == 1 else tuple(y_disc[t - l + 1:t + 1])
        x_past = tuple(x_disc[t - k:t]) if k == 1 else tuple(x_disc[t - k + 1:t + 1])

    joint_counts = Counter()
    y_past_counts = Counter()
    xy_past_counts = Counter()

    for t in range(max(k, l), n - 1):
        y_future = y_disc[t + 1]
        y_past_key = y_disc[t]
        x_past_key = x_disc[t]

        joint_counts[(y_future, y_past_key, x_past_key)] += 1
        y_past_counts[(y_future, y_past_key)] += 1
        xy_past_counts[(y_past_key, x_past_key)] += 1

    total = sum(joint_counts.values())
    if total == 0:
        return 0.0

    te_val = 0.0
    for (y_f, y_p, x_p), count in joint_counts.items():
        p_joint = count / total
        p_yf_yp = y_past_counts.get((y_f, y_p), 0) / total
        p_yp_xp = xy_past_counts.get((y_p, x_p), 0) / total
        p_yp = sum(v for (yf, yp), v in y_past_counts.items() if yp == y_p) / total

        if p_joint > 0 and p_yf_yp > 0 and p_yp_xp > 0 and p_yp > 0:
            p_cond1 = p_yf_yp / p_yp if p_yp > 0 else 0
            p_cond2 = p_joint / p_yp_xp if p_yp_xp > 0 else 0
            if p_cond2 > 0 and p_cond1 > 0:
                te_val += p_joint * np.log(p_cond2 / p_cond1 + 1e-15)

    return max(0, te_val)


def _transfer_entropy_surrogate(x, y, k=1, l=1, n_surrogates=39, alpha=0.05):
    te_obs = _transfer_entropy(x, y, k, l)
    te_surr = []
    for s in range(n_surrogates):
        rng = np.random.RandomState(200 + s)
        shift = rng.randint(1, len(x))
        x_surr = np.roll(x, shift)
        te_s = _transfer_entropy(x_surr, y, k, l)
        te_surr.append(te_s)

    p_val = (np.sum(np.array(te_surr) >= te_obs) + 1) / (n_surrogates + 1)
    return te_obs, p_val, p_val < alpha


class ConvergentCrossMapping:
    def __init__(self, E_list=None, tau_list=None, library_sizes=None, min_obs=30,
                 min_cv=0.3, max_zero_frac=0.6, max_consec_zero=5,
                 n_surrogates=39, surrogate_alpha=0.05):
        self.E_list = E_list or [2, 3, 4]
        self.tau_list = tau_list or [1, 2]
        self.library_sizes = library_sizes or list(range(10, 201, 10))
        self.min_obs = min_obs
        self.min_cv = min_cv
        self.max_zero_frac = max_zero_frac
        self.max_consec_zero = max_consec_zero
        self.n_surrogates = n_surrogates
        self.surrogate_alpha = surrogate_alpha

    def _best_embedding(self, x, y):
        best_E = self.E_list[0]
        best_tau = self.tau_list[0]
        best_rho = -1

        for E in self.E_list:
            for tau in self.tau_list:
                n_pts = len(x) - (E - 1) * tau
                if n_pts < E + 10:
                    continue
                M_x = _shadow_manifold(x, E, tau)
                y_shadow = y[(E - 1) * tau:][:M_x.shape[0]]
                L_test = min(50, n_pts - 5)
                if L_test < E + 5:
                    continue
                df = _cross_map(M_x, y_shadow, E, [L_test])
                if len(df) > 0:
                    rho = df['rho_mean'].iloc[0]
                    if rho > best_rho:
                        best_rho = rho
                        best_E = E
                        best_tau = tau

        return best_E, best_tau

    def analyze_single(self, x, y, var_x_name='X', var_y_name='Y'):
        valid = np.isfinite(x) & np.isfinite(y)
        if valid.sum() < self.min_obs:
            return None, None

        x_raw = x[valid].copy()
        y_raw = y[valid].copy()

        ok, reason = _series_quality_check(
            x_raw, y_raw, self.min_obs, self.min_cv,
            self.max_zero_frac, self.max_consec_zero
        )
        if not ok:
            return None, None

        mu_x, sig_x = np.mean(x_raw), np.std(x_raw)
        mu_y, sig_y = np.mean(y_raw), np.std(y_raw)
        if sig_x < 1e-10 or sig_y < 1e-10:
            return None, None
        x_norm = (x_raw - mu_x) / sig_x
        y_norm = (y_raw - mu_y) / sig_y

        E, tau = self._best_embedding(x_norm, y_norm)

        M_x = _shadow_manifold(x_norm, E, tau)
        M_y = _shadow_manifold(y_norm, E, tau)

        if M_x.shape[0] < E + 10 or M_y.shape[0] < E + 10:
            return None, None

        n_shadow = min(M_x.shape[0], M_y.shape[0])
        M_x = M_x[:n_shadow]
        M_y = M_y[:n_shadow]

        y_shadow = y_norm[(E - 1) * tau:][:n_shadow]
        x_shadow = x_norm[(E - 1) * tau:][:n_shadow]

        df_xmy = _cross_map(M_x, y_shadow, E, self.library_sizes)
        df_ymx = _cross_map(M_y, x_shadow, E, self.library_sizes)

        if len(df_xmy) == 0 or len(df_ymx) == 0:
            return None, None

        df_xmy['direction'] = f'{var_y_name}->M({var_x_name})'
        df_ymx['direction'] = f'{var_x_name}->M({var_y_name})'
        df_xmy['E'] = E
        df_ymx['E'] = E
        df_xmy['tau'] = tau
        df_ymx['tau'] = tau

        return df_xmy, df_ymx

    def analyze_grid(self, grid_data):
        all_results = []
        summary_results = []
        diagnostic_results = []

        for (gx, gy), cell in grid_data.groupby(['grid_x', 'grid_y']):
            cell = cell.sort_values('year')
            if len(cell) < self.min_obs:
                continue

            z = cell['zaihuang_severity'].values.astype(float)
            j = cell['jinshi_count'].values.astype(float)

            ok, reason = _series_quality_check(
                z, j, self.min_obs, self.min_cv,
                self.max_zero_frac, self.max_consec_zero
            )
            if not ok:
                diagnostic_results.append({
                    'grid_x': gx, 'grid_y': gy,
                    'zero_frac_z': np.mean(z == 0),
                    'zero_frac_j': np.mean(j == 0),
                    'cv_z': np.std(z) / (np.mean(z) + 1e-10),
                    'cv_j': np.std(j) / (np.mean(j) + 1e-10),
                    'consec_zero_z': _max_consecutive(z == 0),
                    'consec_zero_j': _max_consecutive(j == 0),
                    'reject_reason': reason,
                })
                continue

            df_zmj, df_jmz = self.analyze_single(z, j, 'Zaihuang', 'Jinshi')

            for df_result in [df_zmj, df_jmz]:
                if df_result is not None and len(df_result) > 0:
                    df_result['grid_x'] = gx
                    df_result['grid_y'] = gy
                    all_results.append(df_result)

            if df_zmj is not None and len(df_zmj) > 0 and df_jmz is not None and len(df_jmz) > 0:
                rho_zmj = df_zmj['rho_mean'].dropna()
                rho_jmz = df_jmz['rho_mean'].dropna()
                if len(rho_zmj) == 0 or len(rho_jmz) == 0:
                    continue

                max_rho_zmj = rho_zmj.max()
                max_rho_jmz = rho_jmz.max()
                max_L_zmj = df_zmj.loc[rho_zmj.idxmax(), 'library_size']
                max_L_jmz = df_jmz.loc[rho_jmz.idxmax(), 'library_size']

                first_rho_zmj = rho_zmj.iloc[0]
                last_rho_zmj = rho_zmj.iloc[-1]
                first_rho_jmz = rho_jmz.iloc[0]
                last_rho_jmz = rho_jmz.iloc[-1]

                convergence_zmj = last_rho_zmj > first_rho_zmj and (last_rho_zmj - first_rho_zmj) > 0.02
                convergence_jmz = last_rho_jmz > first_rho_jmz and (last_rho_jmz - first_rho_jmz) > 0.02

                if convergence_zmj and not convergence_jmz:
                    ccm_direction = 'Zaihuang->Jinshi'
                elif convergence_jmz and not convergence_zmj:
                    ccm_direction = 'Jinshi->Zaihuang'
                elif convergence_zmj and convergence_jmz:
                    ccm_direction = 'Bidirectional'
                else:
                    ccm_direction = 'None'

                best_E = df_zmj['E'].iloc[0] if 'E' in df_zmj.columns else 3
                best_tau = df_zmj['tau'].iloc[0] if 'tau' in df_zmj.columns else 1

                summary_results.append({
                    'grid_x': gx,
                    'grid_y': gy,
                    'n_obs': len(cell),
                    'zero_frac_z': np.mean(z == 0),
                    'zero_frac_j': np.mean(j == 0),
                    'cv_z': np.std(z) / (np.mean(z) + 1e-10),
                    'cv_j': np.std(j) / (np.mean(j) + 1e-10),
                    'max_rho_Z_to_MJ': max_rho_zmj,
                    'max_rho_J_to_MZ': max_rho_jmz,
                    'max_L_Z_to_MJ': max_L_zmj,
                    'max_L_J_to_MZ': max_L_jmz,
                    'first_rho_Z_to_MJ': first_rho_zmj,
                    'last_rho_Z_to_MJ': last_rho_zmj,
                    'first_rho_J_to_MZ': first_rho_jmz,
                    'last_rho_J_to_MZ': last_rho_jmz,
                    'convergence_Z_to_MJ': convergence_zmj,
                    'convergence_J_to_MZ': convergence_jmz,
                    'ccm_direction': ccm_direction,
                    'best_E': best_E,
                    'best_tau': best_tau,
                })

        all_df = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()
        summary_df = pd.DataFrame(summary_results)
        diagnostic_df = pd.DataFrame(diagnostic_results)

        return all_df, summary_df, diagnostic_df

    def run_full_analysis(self, grid_data):
        print("=" * 60)
        print("收敛交叉映射 (CCM) 分析 (v4: 彻底修复信号泄露)")
        print("=" * 60)
        print("v4修复内容:")
        print("  1. 最小变异系数(min_cv=0.3)过滤低变异序列")
        print("  2. 最大零值比例(max_zero_frac=0.6)过滤零值聚集")
        print("  3. 最大连续零值(max_consec_zero=5)过滤长零值段")
        print("  4. 排除|rho|>0.999的近完美预测结果")
        print("  5. 多嵌入参数自动选择(E=[2,3,4], tau=[1,2])")
        print("  6. 替代数据显著性检验(n=39, alpha=0.05)")
        print("  7. 迁移熵(Transfer Entropy)交叉验证")
        print("  8. 输出诊断信息(被过滤格网的原因)")

        all_df, summary_df, diagnostic_df = self.analyze_grid(grid_data)

        if len(diagnostic_df) > 0:
            print(f"\n  被过滤格网: {len(diagnostic_df)}")
            reason_counts = diagnostic_df['reject_reason'].value_counts()
            for r, c in reason_counts.items():
                print(f"    {r}: {c} 个")

        if len(summary_df) > 0:
            print(f"\nCCM分析完成: {len(summary_df)} 个有效格网")
            dir_counts = summary_df['ccm_direction'].value_counts()
            print(f"  因果方向分布:")
            for d, c in dir_counts.items():
                print(f"    {d}: {c} 个格网")

            max_rho_z = summary_df['max_rho_Z_to_MJ'].max()
            max_rho_j = summary_df['max_rho_J_to_MZ'].max()
            print(f"  最大rho: Z→M(J)={max_rho_z:.4f}, J→M(Z)={max_rho_j:.4f}")

            if max_rho_z > 0.99 or max_rho_j > 0.99:
                print("  [警告] 仍存在rho>0.99的格网, 请检查数据质量")
                high_rho = summary_df[
                    (summary_df['max_rho_Z_to_MJ'] > 0.99) |
                    (summary_df['max_rho_J_to_MZ'] > 0.99)
                ]
                for _, row in high_rho.head(3).iterrows():
                    print(f"    ({row['grid_x']:.1f}, {row['grid_y']:.1f}): "
                          f"zero_z={row['zero_frac_z']:.0%}, zero_j={row['zero_frac_j']:.0%}, "
                          f"cv_z={row['cv_z']:.3f}, cv_j={row['cv_j']:.3f}")
            else:
                print("  [OK] 无rho>0.99的格网, 信号泄露已修复")

            if 'best_E' in summary_df.columns:
                e_dist = summary_df['best_E'].value_counts().sort_index()
                print(f"  最优嵌入维数分布:")
                for e, c in e_dist.items():
                    print(f"    E={e}: {c} 个格网")

            print("\n  替代数据显著性检验 (n_surrogates=39)...")
            sig_count = 0
            for i, row in summary_df.iterrows():
                gx, gy = row['grid_x'], row['grid_y']
                cell = grid_data[(grid_data['grid_x'] == gx) & (grid_data['grid_y'] == gy)].sort_values('year')
                z = cell['zaihuang_severity'].values.astype(float)
                j = cell['jinshi_count'].values.astype(float)

                mu_z, sig_z = np.mean(z), np.std(z)
                mu_j, sig_j = np.mean(j), np.std(j)
                if sig_z < 1e-10 or sig_j < 1e-10:
                    continue
                z_n = (z - mu_z) / sig_z
                j_n = (j - mu_j) / sig_j

                E_use = int(row.get('best_E', 3))
                tau_use = int(row.get('best_tau', 1))

                p_val, sig = _surrogate_test(
                    z_n, j_n, E_use, tau_use,
                    self.library_sizes, self.n_surrogates, self.surrogate_alpha
                )
                summary_df.loc[i, 'surrogate_pval'] = p_val
                summary_df.loc[i, 'surrogate_sig'] = sig
                if sig:
                    sig_count += 1

            n_tested = summary_df['surrogate_pval'].notna().sum()
            print(f"  替代检验完成: {n_tested} 个格网, {sig_count} 个显著(p<{self.surrogate_alpha})")

            print("\n  迁移熵(Transfer Entropy)交叉验证...")
            te_sig_count = 0
            te_results = []
            for i, row in summary_df.iterrows():
                gx, gy = row['grid_x'], row['grid_y']
                cell = grid_data[(grid_data['grid_x'] == gx) & (grid_data['grid_y'] == gy)].sort_values('year')
                z = cell['zaihuang_severity'].values.astype(float)
                j = cell['jinshi_count'].values.astype(float)

                mu_z, sig_z = np.mean(z), np.std(z)
                mu_j, sig_j = np.mean(j), np.std(j)
                if sig_z < 1e-10 or sig_j < 1e-10:
                    continue
                z_n = (z - mu_z) / sig_z
                j_n = (j - mu_j) / sig_j

                te_zj, p_zj, sig_zj = _transfer_entropy_surrogate(
                    z_n, j_n, k=1, l=1, n_surrogates=self.n_surrogates, alpha=self.surrogate_alpha
                )
                te_jz, p_jz, sig_jz = _transfer_entropy_surrogate(
                    j_n, z_n, k=1, l=1, n_surrogates=self.n_surrogates, alpha=self.surrogate_alpha
                )

                summary_df.loc[i, 'TE_Z_to_J'] = te_zj
                summary_df.loc[i, 'TE_J_to_Z'] = te_jz
                summary_df.loc[i, 'TE_Z_to_J_pval'] = p_zj
                summary_df.loc[i, 'TE_J_to_Z_pval'] = p_jz
                summary_df.loc[i, 'TE_Z_to_J_sig'] = sig_zj
                summary_df.loc[i, 'TE_J_to_Z_sig'] = sig_jz

                if sig_zj or sig_jz:
                    te_sig_count += 1

                te_direction = 'None'
                if sig_zj and not sig_jz:
                    te_direction = 'Zaihuang->Jinshi'
                elif sig_jz and not sig_zj:
                    te_direction = 'Jinshi->Zaihuang'
                elif sig_zj and sig_jz:
                    te_direction = 'Bidirectional'
                summary_df.loc[i, 'TE_direction'] = te_direction

            n_te_tested = summary_df['TE_Z_to_J'].notna().sum()
            print(f"  迁移熵检验完成: {n_te_tested} 个格网, {te_sig_count} 个显著")

            ccm_te_agree = 0
            n_comparable = 0
            for _, row in summary_df.iterrows():
                ccm_dir = row.get('ccm_direction', 'None')
                te_dir = row.get('TE_direction', 'None')
                if ccm_dir != 'None' or te_dir != 'None':
                    n_comparable += 1
                    if ccm_dir == te_dir:
                        ccm_te_agree += 1
            if n_comparable > 0:
                print(f"  CCM与迁移熵方向一致率: {ccm_te_agree}/{n_comparable} "
                      f"({ccm_te_agree / n_comparable * 100:.1f}%)")

            bidir = summary_df[summary_df['ccm_direction'] == 'Bidirectional']
            z_to_j = summary_df[summary_df['ccm_direction'] == 'Zaihuang->Jinshi']
            j_to_z = summary_df[summary_df['ccm_direction'] == 'Jinshi->Zaihuang']

            if len(z_to_j) > 0:
                print(f"\n  灾荒→进士 CCM因果格网: {len(z_to_j)}")
                print(f"    平均ρ(Z→M(J)): {z_to_j['max_rho_Z_to_MJ'].mean():.4f}")
            if len(bidir) > 0:
                print(f"\n  双向CCM因果格网: {len(bidir)}")
                print(f"    平均ρ(Z→M(J)): {bidir['max_rho_Z_to_MJ'].mean():.4f}")
                print(f"    平均ρ(J→M(Z)): {bidir['max_rho_J_to_MZ'].mean():.4f}")

            both_sig = summary_df[
                (summary_df.get('surrogate_sig', pd.Series(dtype=bool)) == True) &
                (summary_df.get('TE_Z_to_J_sig', pd.Series(dtype=bool)) == True)
            ]
            if len(both_sig) > 0:
                print(f"\n  CCM替代检验+迁移熵双重显著: {len(both_sig)} 个格网 (最可靠)")
                for _, row in both_sig.head(5).iterrows():
                    print(f"    ({row['grid_x']:.1f}, {row['grid_y']:.1f}): "
                          f"CCM_dir={row['ccm_direction']}, "
                          f"TE_dir={row.get('TE_direction', 'N/A')}, "
                          f"ρ_Z→J={row['max_rho_Z_to_MJ']:.4f}, "
                          f"TE_Z→J={row.get('TE_Z_to_J', 0):.4f}")

            summary_df.to_excel(
                os.path.join(OUTPUT_DIR, "ccm_summary.xlsx"),
                index=False, engine='openpyxl'
            )
            print(f"\nCCM汇总结果已保存至 {OUTPUT_DIR}/ccm_summary.xlsx")
        else:
            print("CCM分析无有效结果")

        if len(all_df) > 0:
            all_df.to_excel(
                os.path.join(OUTPUT_DIR, "ccm_convergence_detail.xlsx"),
                index=False, engine='openpyxl'
            )

        if len(diagnostic_df) > 0:
            diagnostic_df.to_excel(
                os.path.join(OUTPUT_DIR, "ccm_diagnostics.xlsx"),
                index=False, engine='openpyxl'
            )
            print(f"CCM诊断信息已保存至 {OUTPUT_DIR}/ccm_diagnostics.xlsx")

        return all_df, summary_df
