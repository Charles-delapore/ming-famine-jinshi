"""End-to-end pipeline for the Ming famine / Jinshi analysis.

Requires the full raw dataset described in data/README.md and the analysis
dependencies in requirements-analysis.txt. The figure-only subset does not need
this file; use scripts/run_sample_figures.py to reproduce the figures on the
synthetic sample data.

The pipeline is intentionally explicit (14 steps) so each stage can be audited
separately. Steps 8-9 are retained as documented no-ops (the clustering metrics
were negative, so the analysis moved to the grid level).
"""
import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import DATA_PATHS, OUTPUT_PATHS, CLUSTER_PARAMS, OUTPUT_DIR
from src.data_processing.loader import (
    load_zaihuang_data, load_zaihuang_data_full,
    load_jinshi_data, load_jinshi_important,
    merge_level_city, save_processed,
)
from src.algorithms.ss_dbscan import cluster_zaihuang, cluster_jinshi
from src.algorithms.st_dbscan import cluster_zaihuang_st
from src.algorithms.gmm_cluster import cluster_zaihuang_gmm, cluster_jinshi_gmm
from src.algorithms.dynamic_weight_dbscan import cluster_zaihuang_dynamic, cluster_jinshi_dynamic
from src.algorithms.st_graph import build_zaihuang_graph, build_jinshi_graph
from src.analysis.similarity import (
    compute_similarity_matrix, preprocess_zaihuang,
    fdr_correction,
)
from src.analysis.cluster_compare import compare_clusters_lagged
from src.analysis.bayesian_optimize import evaluate_clustering
from src.analysis.grid_analysis import run_grid_analysis
from src.analysis.paleoclimate_analysis import run_paleoclimate_analysis
from src.analysis.ccm_analysis import ConvergentCrossMapping
from src.analysis.spatial_regression import run_spatial_analysis
from src.analysis.sensitivity_analysis import run_sensitivity_and_decomposition
from src.visualization.plot_3d import plot_zaihuang_3d, plot_jinshi_3d, plot_comparison_3d
from src.visualization.plot_2d import (
    plot_lagged_similarity_scatter, plot_similarity_heatmap,
    plot_cluster_comparison_2d,
)
from src.visualization.dual_axis import plot_dual_axis, plot_dual_axis_with_fit


def step1_data_loading():
    print("=" * 60)
    print("步骤1: 数据加载与预处理")
    print("=" * 60)

    zaihuang_data = load_zaihuang_data_full()
    print(f"灾荒数据加载完成: {len(zaihuang_data)} 条记录")

    jinshi_data = load_jinshi_data()
    print(f"进士数据加载完成: {len(jinshi_data)} 条记录")

    merged_data = merge_level_city()
    print(f"合并数据完成: {len(merged_data)} 条记录")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    sort_cols = [c for c in ["year", "code", "x", "y"] if c in merged_data.columns]
    merged_data = merged_data.sort_values(sort_cols, kind="mergesort").reset_index(drop=True)
    merged_data.to_excel(OUTPUT_PATHS["merged_data"], index=False, engine='openpyxl')
    print(f"合并数据已保存至 {OUTPUT_PATHS['merged_data']}")

    return zaihuang_data, jinshi_data, merged_data


def step2_zaihuang_clustering(zaihuang_data):
    print("\n" + "=" * 60)
    print("步骤2: 灾荒数据聚类 (SSDBSCAN)")
    print("=" * 60)

    data = zaihuang_data.dropna(subset=['x', 'y', 'year', 'level'])
    clustered, model = cluster_zaihuang(data, CLUSTER_PARAMS["zaihuang_ssdbcan"])

    print("灾荒聚类结果分布:")
    print(clustered['cluster'].value_counts())

    sort_cols = [c for c in ["year", "code", "x", "y", "cluster"] if c in clustered.columns]
    clustered = clustered.sort_values(sort_cols, kind="mergesort").reset_index(drop=True)
    clustered.to_excel(OUTPUT_PATHS["clustered_levels"], index=False, engine='openpyxl')
    print(f"灾荒聚类结果已保存至 {OUTPUT_PATHS['clustered_levels']}")

    return clustered


def step3_jinshi_clustering(jinshi_data):
    print("\n" + "=" * 60)
    print("步骤3: 进士数据聚类 (SSDBSCAN)")
    print("=" * 60)

    clustered, model = cluster_jinshi(jinshi_data, CLUSTER_PARAMS["jinshi_ssdbcan"])

    print("进士聚类结果分布:")
    print(clustered['cluster'].value_counts())

    sort_cols = [c for c in ["EntryYear", "NameChn", "X", "Y", "cluster"] if c in clustered.columns]
    clustered = clustered.sort_values(sort_cols, kind="mergesort").reset_index(drop=True)
    clustered.to_excel(OUTPUT_PATHS["clustered_jinshi"], index=False, engine='openpyxl')
    print(f"进士聚类结果已保存至 {OUTPUT_PATHS['clustered_jinshi']}")

    return clustered


def step4_similarity_analysis(clustered_zaihuang, clustered_jinshi):
    print("\n" + "=" * 60)
    print("步骤4: 时空相似度分析")
    print("=" * 60)

    valid_zaihuang = clustered_zaihuang[clustered_zaihuang['cluster'] != -1]
    valid_jinshi = clustered_jinshi[clustered_jinshi['cluster'] != -1]

    if len(valid_zaihuang) == 0 or len(valid_jinshi) == 0:
        print("有效聚类数量不足，跳过相似度分析")
        return None

    similarity_df = compute_similarity_matrix(valid_jinshi, valid_zaihuang)
    print(f"相似度计算完成: {len(similarity_df)} 对聚类对")

    if len(similarity_df) > 0:
        top_matches = similarity_df.loc[similarity_df.groupby('jinshi_cluster')['similarity'].idxmax()]
        print("各进士聚类与最相似灾荒聚类:")
        print(top_matches[['jinshi_cluster', 'zaihuang_cluster', 'similarity']])
    else:
        print("未找到有时空重叠的聚类对")

    return similarity_df


def step5_lagged_comparison(clustered_zaihuang, clustered_jinshi):
    print("\n" + "=" * 60)
    print("步骤5: 时间滞后关联分析 (重写置换检验)")
    print("=" * 60)
    print("改进: 环形时间平移+环面空间平移+互相关相似度")

    valid_zaihuang = clustered_zaihuang[clustered_zaihuang['cluster'] != -1]
    valid_jinshi = clustered_jinshi[clustered_jinshi['cluster'] != -1]

    if len(valid_zaihuang) == 0 or len(valid_jinshi) == 0:
        print("有效聚类数量不足，跳过滞后分析")
        return None

    result_df = compare_clusters_lagged(valid_jinshi, valid_zaihuang)

    if len(result_df) > 0:
        significant_df = result_df[result_df['significant']]
        significant_corr_df = result_df[result_df['significant_corr']] if 'significant_corr' in result_df.columns else pd.DataFrame()
        print(f"\n包围盒相似度显著 (P<0.05): {len(significant_df)} 对")
        print(f"互相关显著 (P<0.05): {len(significant_corr_df)} 对")

        if len(significant_corr_df) > 0:
            print("\n互相关显著聚类对 (更可靠):")
            print(significant_corr_df.sort_values('p_value_corr').head(20).to_string())

    result_df.to_excel(OUTPUT_PATHS["lagged_similarity_results"], index=False, engine='openpyxl')
    print(f"滞后分析结果已保存至 {OUTPUT_PATHS['lagged_similarity_results']}")

    return result_df


def step6_visualization(clustered_zaihuang, clustered_jinshi, similarity_df, lagged_df):
    print("\n" + "=" * 60)
    print("步骤6: 可视化")
    print("=" * 60)

    plot_zaihuang_3d(clustered_zaihuang)
    plot_jinshi_3d(clustered_jinshi)

    valid_z = clustered_zaihuang[clustered_zaihuang['cluster'] != -1]
    valid_j = clustered_jinshi[clustered_jinshi['cluster'] != -1]
    if len(valid_z) > 0 and len(valid_j) > 0:
        plot_comparison_3d(valid_j, valid_z)

    if similarity_df is not None and len(similarity_df) > 0:
        plot_similarity_heatmap(similarity_df)

    if lagged_df is not None and len(lagged_df) > 0:
        plot_lagged_similarity_scatter(lagged_df)

    try:
        scholar_df = load_jinshi_data()
        scholar_df = scholar_df.rename(columns={'EntryYear': 'year'})
        scholar_count_by_year = scholar_df.groupby('year')['year'].count()

        disaster_df = load_zaihuang_data()
        disaster_count_by_year = disaster_df.groupby('year')['year'].count()

        plot_dual_axis(scholar_count_by_year, disaster_count_by_year)
        plot_dual_axis_with_fit(scholar_count_by_year, disaster_count_by_year)
    except Exception as e:
        print(f"双轴可视化跳过: {e}")


def step7_dynamic_weight_clustering(zaihuang_data, jinshi_data):
    print("\n" + "=" * 60)
    print("步骤7: 聚类质量评估 (仅SSDBSCAN固定权重)")
    print("=" * 60)
    print("改进: 移除动态权重聚类和谱聚类(Silhouette均为负值)")
    print("  仅保留SSDBSCAN固定权重聚类用于全局可视化")

    from sklearn.preprocessing import StandardScaler
    from src.analysis.bayesian_optimize import evaluate_clustering

    data_z = zaihuang_data.dropna(subset=['x', 'y', 'year', 'level'])
    clustered_z, model_z = cluster_zaihuang(data_z, CLUSTER_PARAMS["zaihuang_ssdbcan"])
    print(f"灾荒SSDBSCAN聚类: {len(set(clustered_z['cluster']))} 个聚类")

    X_z = data_z[['x', 'y', 'year', 'level']].values
    scaler = StandardScaler()
    X_z_scaled = scaler.fit_transform(X_z)
    sil_z, db_z, ch_z = evaluate_clustering(X_z_scaled, model_z.labels_)
    n_clusters = len(set(model_z.labels_[model_z.labels_ != -1]))
    noise = (model_z.labels_ == -1).sum() / len(model_z.labels_)
    print(f"  Silhouette={sil_z:.4f}, DB={db_z:.4f}, CH={ch_z:.1f}, "
          f"聚类数={n_clusters}, 噪声率={noise:.2%}")

    return clustered_z, None


def step8_graph_analysis(zaihuang_data, jinshi_data):
    print("\n" + "=" * 60)
    print("步骤8: [已精简] 跳过谱聚类 (Silhouette均为负值)")
    print("=" * 60)
    print("  聚类分析重心已转移至格网级, 行政点级谱聚类不再执行")
    return None, None, None, None


def step9_clustering_evaluation(zaihuang_data, jinshi_data):
    print("\n" + "=" * 60)
    print("步骤9: [已精简] 跳过多方法聚类对比")
    print("=" * 60)
    print("  所有聚类算法Silhouette均为负值, 聚类质量不佳")
    print("  因果推断完全依托格网级分析, 聚类仅保留全局可视化用途")
    return []


def step10_grid_analysis():
    print("\n" + "=" * 60)
    print("步骤10: 格网化时空分析 (核心分析流程)")
    print("=" * 60)
    print("替代旧版行政点分析，解决以下问题:")
    print("  [P0] 迁移分析: 行政点→格网化 (解决n_locations=1, 位移=0)")
    print("  [P0] 置换检验: 环形时间平移+互相关 (解决p值天花板/地板效应)")
    print("  [P1] 因果推断: 聚类级→格网级Granger (解决数据稀疏/数值溢出)")
    print("  [P1] 分层假说: 短期/中期/长期多尺度因果模型")
    print("  [P1] VIF共线性诊断: 自动检测并切换岭回归")
    print("  [P2] 衍生特征: 累积强度/持续时间/连续受灾年数")
    print("  [P2] 动态权重: 融合格网化方法")

    grid_data, grid_cluster, grid_trajectories, gc_grid_df = run_grid_analysis()
    return grid_data, grid_cluster, grid_trajectories, gc_grid_df


def step11_paleoclimate_integration(grid_data):
    print("\n" + "=" * 60)
    print("步骤11: 古气候数据集成分析")
    print("=" * 60)
    print("引入数据源:")
    print("  1. Mann et al. 2009: 北半球温度重建 + AMO指数")
    print("  2. Schneider et al. 2015: 北半球MXD夏季温度重建")
    print("分析内容:")
    print("  - 古气候-灾荒/进士相关性分析")
    print("  - 气候条件下的因果分析 (暖期/冷期)")
    print("  - 偏相关分析 (控制气候变量后灾荒-进士关联)")

    corr_df, cond_causal_df, partial_df = run_paleoclimate_analysis(grid_data)
    return corr_df, cond_causal_df, partial_df


def step12_ccm_analysis(grid_data):
    print("\n" + "=" * 60)
    print("步骤12: 收敛交叉映射 (CCM) 分析")
    print("=" * 60)
    print("方法来源: Sugihara et al. 2012 Science")
    print("  - 基于Takens嵌入定理的非线性因果推断")
    print("  - 检验灾荒与进士之间的双向/单向因果关系")
    print("  - 通过影子流形重构验证因果方向")

    ccm = ConvergentCrossMapping(E_list=[2, 3, 4], tau_list=[1, 2], library_sizes=list(range(10, 201, 10)))
    all_df, summary_df = ccm.run_full_analysis(grid_data)
    return all_df, summary_df


def step13_spatial_regression(grid_data):
    print("\n" + "=" * 60)
    print("步骤13: 空间异质性因果模型")
    print("=" * 60)
    print("方法来源:")
    print("  - 空间杜宾模型 (SDM): libpysal + spreg")
    print("  - 地理加权回归 (GWR): mgwr")
    print("  - 解决OLS忽略空间依赖的问题")

    sdm_results, gwr_results = run_spatial_analysis(grid_data)
    return sdm_results, gwr_results


def step14_sensitivity_decomposition(grid_data):
    print("\n" + "=" * 60)
    print("步骤14: 敏感性分析 + 时间序列分解 + 地理探测器")
    print("=" * 60)
    print("方法来源:")
    print("  - 敏感性分析: 不同格网分辨率(0.5°/1°/2°) + 不同滞后分组")
    print("  - STL分解: statsmodels.tsa.seasonal.STL")
    print("  - 地理探测器: q统计量")

    sens_grid, sens_lag, stl_results, geodet = run_sensitivity_and_decomposition(grid_data)
    return sens_grid, sens_lag, stl_results, geodet


def main():
    print("明代灾荒与进士时空聚类分析 - 改进版v5")
    print("=" * 60)
    print("v5改进 (基于第三轮反馈):")
    print("  [P0] CCM v4: 多嵌入参数(E=[2,3,4],τ=[1,2])+替代数据检验(n=39)+迁移熵交叉验证")
    print("  [P0] CCM v4: min_cv=0.3+max_zero_frac=0.6+max_consec_zero=5+排除ρ>0.999")
    print("  [P1] 重新启用扩展时间序列(use_extended=True), 1521-1619年灾荒+进士")
    print("  [P1] 修复古气候0有效值: 排除仪器观测列(tempanom-JJAtarg), 使用重建值")
    print("  [P1] 偏相关分析遍历所有有效古气候变量(非仅第一个)")
    print("  [P2] 聚类对最小样本量: 3→10, 消除广播错误")
    print("  [P2] 多尺度模型: LASSO特征筛选+BIC选阶+靶向分析(FDR显著格网)")
    print("  [P3] 精简聚类: 移除动态权重聚类+谱聚类+GMM对比, 仅保留SSDBSCAN")
    print("=" * 60)

    zaihuang_data, jinshi_data, merged_data = step1_data_loading()
    clustered_zaihuang = step2_zaihuang_clustering(zaihuang_data)
    clustered_jinshi = step3_jinshi_clustering(jinshi_data)
    similarity_df = step4_similarity_analysis(clustered_zaihuang, clustered_jinshi)
    lagged_df = step5_lagged_comparison(clustered_zaihuang, clustered_jinshi)
    step6_visualization(clustered_zaihuang, clustered_jinshi, similarity_df, lagged_df)

    step7_dynamic_weight_clustering(zaihuang_data, jinshi_data)
    step8_graph_analysis(zaihuang_data, jinshi_data)
    step9_clustering_evaluation(zaihuang_data, jinshi_data)

    grid_data, grid_cluster, grid_trajectories, gc_grid_df = step10_grid_analysis()

    step11_paleoclimate_integration(grid_data)

    step12_ccm_analysis(grid_data)

    step13_spatial_regression(grid_data)

    step14_sensitivity_decomposition(grid_data)

    print("\n" + "=" * 60)
    print("全部流程执行完毕!")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)
    print("\nv5改进总结:")
    print("  [P0] CCM v4: 多嵌入参数+替代数据检验+迁移熵交叉验证, 彻底修复信号泄露")
    print("  [P1] 重新启用扩展时间序列(1521-1619年), 古气候统计效力翻倍")
    print("  [P1] 修复古气候0有效值: 排除仪器观测列, 偏相关遍历所有有效变量")
    print("  [P2] 聚类对最小样本量3→10, 消除广播错误")
    print("  [P2] 多尺度模型: LASSO特征筛选+BIC选阶+靶向分析")
    print("  [P3] 精简聚类: 移除动态权重+谱聚类+GMM, 仅保留SSDBSCAN固定权重")


if __name__ == "__main__":
    main()

