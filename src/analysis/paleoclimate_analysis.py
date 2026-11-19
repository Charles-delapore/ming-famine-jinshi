import os
import sys
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression, Ridge

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config import OUTPUT_DIR
from src.data_processing.paleoclimate_loader import (
    load_all_paleoclimate_data,
    merge_paleoclimate_with_grid,
)


def compute_paleoclimate_correlation(grid_data, paleoclimate_datasets):
    results = []

    for key, pc_df in paleoclimate_datasets.items():
        if len(pc_df) == 0 or 'year' not in pc_df.columns:
            continue

        value_cols = [c for c in pc_df.columns if c != 'year']
        merged = grid_data.merge(pc_df[['year'] + value_cols], on='year', how='inner')

        if len(merged) == 0:
            continue

        for (gx, gy), cell in merged.groupby(['grid_x', 'grid_y']):
            cell = cell.sort_values('year')
            if len(cell) < 20:
                continue

            z_series = cell['zaihuang_severity'].values
            j_series = cell['jinshi_count'].values

            for vc in value_cols:
                pc_series = cell[vc].values
                valid_mask = np.isfinite(pc_series) & np.isfinite(z_series) & np.isfinite(j_series)
                if valid_mask.sum() < 20:
                    continue

                z_v = z_series[valid_mask]
                j_v = j_series[valid_mask]
                p_v = pc_series[valid_mask]
                if np.std(z_v) < 1e-10 or np.std(j_v) < 1e-10 or np.std(p_v) < 1e-10:
                    continue

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    r_z_pc, p_z_pc = stats.pearsonr(z_v, p_v)
                    r_j_pc, p_j_pc = stats.pearsonr(j_v, p_v)

                results.append({
                    'paleoclimate_var': f"{key}.{vc}",
                    'grid_x': gx,
                    'grid_y': gy,
                    'n_obs': valid_mask.sum(),
                    'corr_zaihuang_pc': r_z_pc,
                    'pval_zaihuang_pc': p_z_pc,
                    'corr_jinshi_pc': r_j_pc,
                    'pval_jinshi_pc': p_j_pc,
                    'sig_zaihuang': p_z_pc < 0.05,
                    'sig_jinshi': p_j_pc < 0.05,
                })

    return pd.DataFrame(results)


def climate_conditioned_causality(grid_data, paleoclimate_datasets, max_lag=20, significance=0.05):
    from src.analysis.grid_analysis import GridGrangerCausality

    results = []

    for key, pc_df in paleoclimate_datasets.items():
        if len(pc_df) == 0 or 'year' not in pc_df.columns:
            continue

        value_cols = [c for c in pc_df.columns if c != 'year'
                      and 'lower' not in c.lower() and 'upper' not in c.lower()
                      and not c.endswith('-') and not c.endswith('+')]
        if not value_cols:
            value_cols = [c for c in pc_df.columns if c != 'year']
        if not value_cols:
            continue

        for main_vc in value_cols:
            merged = grid_data.merge(pc_df[['year', main_vc]], on='year', how='inner')

            if len(merged) == 0:
                continue

            valid_mask = merged[main_vc].notna()
            if valid_mask.sum() < 30:
                continue

            merged_valid = merged[valid_mask].copy()
            warm_years = merged_valid[merged_valid[main_vc] > merged_valid[main_vc].median()]['year'].unique()
            cold_years = merged_valid[merged_valid[main_vc] <= merged_valid[main_vc].median()]['year'].unique()

            for phase_name, phase_years in [('warm', warm_years), ('cold', cold_years)]:
                phase_data = merged[merged['year'].isin(phase_years)]
                if len(phase_data) < 30:
                    continue

                gc = GridGrangerCausality(max_lag=max_lag, significance=significance, min_obs=15)
                gc_df = gc.analyze_grid_causality(phase_data)

                if len(gc_df) > 0:
                    gc_df['climate_var'] = f"{key}.{main_vc}"
                    gc_df['climate_phase'] = phase_name
                    results.append(gc_df)

    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()


def paleoclimate_partial_correlation(grid_data, paleoclimate_datasets):
    results = []

    for key, pc_df in paleoclimate_datasets.items():
        if len(pc_df) == 0 or 'year' not in pc_df.columns:
            continue

        value_cols = [c for c in pc_df.columns if c != 'year'
                      and 'lower' not in c.lower() and 'upper' not in c.lower()
                      and '-' not in c.replace('-', '', 1).replace('+', '', 1) if c[0] != '-'
                      and '+' not in c.replace('+', '', 1)]
        value_cols = [c for c in value_cols if not c.endswith('-') and not c.endswith('+')]
        if not value_cols:
            value_cols = [c for c in pc_df.columns if c != 'year']
        if not value_cols:
            continue

        for main_vc in value_cols:
            merged = grid_data.merge(pc_df[['year', main_vc]], on='year', how='inner')

            if len(merged) == 0:
                continue

            for (gx, gy), cell in merged.groupby(['grid_x', 'grid_y']):
                cell = cell.sort_values('year')
                if len(cell) < 30:
                    continue

                z = cell['zaihuang_severity'].values
                j = cell['jinshi_count'].values
                c = cell[main_vc].values

                valid = np.isfinite(z) & np.isfinite(j) & np.isfinite(c)
                if valid.sum() < 30:
                    continue

                z_v, j_v, c_v = z[valid], j[valid], c[valid]

                if np.std(c_v) < 1e-10:
                    continue

                X_zc = np.column_stack([z, c])
                reg_j_on_zc = LinearRegression().fit(X_zc[valid], j_v)
                resid_j = j_v - reg_j_on_zc.predict(X_zc[valid])

                X_jc = np.column_stack([j, c])
                reg_z_on_jc = LinearRegression().fit(X_jc[valid], z_v)
                resid_z = z_v - reg_z_on_jc.predict(X_jc[valid])

                if np.std(resid_j) < 1e-10 or np.std(resid_z) < 1e-10:
                    continue

                r_partial, p_partial = stats.pearsonr(resid_z, resid_j)

                results.append({
                    'paleoclimate_var': f"{key}.{main_vc}",
                    'grid_x': gx,
                    'grid_y': gy,
                    'n_obs': valid.sum(),
                    'partial_corr_z_j': r_partial,
                    'partial_corr_pval': p_partial,
                    'partial_corr_sig': p_partial < 0.05,
                })

    return pd.DataFrame(results)


def run_paleoclimate_analysis(grid_data):
    print("=" * 60)
    print("古气候数据集成分析")
    print("=" * 60)

    print("\n加载古气候数据...")
    pc_datasets = load_all_paleoclimate_data()

    if not pc_datasets:
        print("未加载到任何古气候数据，跳过分析")
        return None, None, None

    print("\n--- 古气候数据与格网数据合并 ---")
    merged = merge_paleoclimate_with_grid(grid_data, pc_datasets)
    print(f"合并后数据: {len(merged)} 条, {len(merged.columns)} 列")

    print("\n--- 古气候-灾荒/进士相关性分析 ---")
    corr_df = compute_paleoclimate_correlation(grid_data, pc_datasets)
    if len(corr_df) > 0:
        print(f"相关性分析完成: {len(corr_df)} 条记录")
        sig_z = corr_df[corr_df['sig_zaihuang']]
        sig_j = corr_df[corr_df['sig_jinshi']]
        print(f"  灾荒-古气候显著相关: {len(sig_z)} 条")
        print(f"  进士-古气候显著相关: {len(sig_j)} 条")

        if len(sig_z) > 0:
            for var, group in sig_z.groupby('paleoclimate_var'):
                mean_r = group['corr_zaihuang_pc'].mean()
                print(f"    {var}: 平均r={mean_r:.4f}, 显著格网数={len(group)}")

        corr_df.to_excel(
            os.path.join(OUTPUT_DIR, "paleoclimate_correlation.xlsx"),
            index=False, engine='openpyxl'
        )
    else:
        print("  无有效相关性结果")

    print("\n--- 气候条件下的因果分析 (暖期/冷期) ---")
    cond_causal_df = climate_conditioned_causality(grid_data, pc_datasets)
    if len(cond_causal_df) > 0:
        print(f"条件因果分析完成: {len(cond_causal_df)} 条记录")
        for (var, phase), group in cond_causal_df.groupby(['climate_var', 'climate_phase']):
            n_causal = (group['causal_direction'] != 'none').sum()
            print(f"  {var} {phase}期: {n_causal}/{len(group)} 格网存在因果关系")

        cond_causal_df.to_excel(
            os.path.join(OUTPUT_DIR, "paleoclimate_conditioned_causality.xlsx"),
            index=False, engine='openpyxl'
        )
    else:
        print("  无有效条件因果结果")

    print("\n--- 偏相关分析 (控制气候变量后灾荒-进士关联) ---")
    partial_df = paleoclimate_partial_correlation(grid_data, pc_datasets)
    if len(partial_df) > 0:
        print(f"偏相关分析完成: {len(partial_df)} 条记录")
        sig_partial = partial_df[partial_df['partial_corr_sig']]
        print(f"  控制气候后仍显著: {len(sig_partial)} 条")

        for var, group in partial_df.groupby('paleoclimate_var'):
            mean_r = group['partial_corr_z_j'].mean()
            n_sig = group['partial_corr_sig'].sum()
            print(f"    控制{var}: 平均偏相关r={mean_r:.4f}, 显著={n_sig}/{len(group)}")

        partial_df.to_excel(
            os.path.join(OUTPUT_DIR, "paleoclimate_partial_correlation.xlsx"),
            index=False, engine='openpyxl'
        )
    else:
        print("  无有效偏相关结果")

    merged.to_csv(
        os.path.join(OUTPUT_DIR, "grid_data_with_paleoclimate.csv"),
        index=False
    )
    print(f"\n古气候-格网合并数据已保存至 {OUTPUT_DIR}/grid_data_with_paleoclimate.csv")

    return corr_df, cond_causal_df, partial_df
