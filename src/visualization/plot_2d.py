import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config import VISUALIZATION, OUTPUT_DIR


def setup_chinese_font():
    plt.rcParams['font.sans-serif'] = VISUALIZATION["font_sans_serif"]
    plt.rcParams['axes.unicode_minus'] = VISUALIZATION["axes_unicode_minus"]


def plot_lagged_similarity_scatter(result_df, save_path=None):
    setup_chinese_font()
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=result_df,
        x='best_lag',
        y='max_similarity',
        hue='significant',
        palette={True: 'red', False: 'gray'},
        alpha=0.7,
    )
    plt.title("时空关联模式可视化 (红点表示P<0.05)")
    plt.xlabel('最佳滞后年数')
    plt.ylabel('最大相似度')
    plt.legend(title='显著性')

    if save_path is None:
        save_path = os.path.join(OUTPUT_DIR, 'lagged_similarity.png')
    plt.savefig(save_path, dpi=VISUALIZATION["dpi"], bbox_inches='tight')
    plt.close()
    print(f"滞后相似度散点图已保存至 {save_path}")
    return save_path


def plot_similarity_heatmap(similarity_df, save_path=None):
    setup_chinese_font()
    heatmap_data = similarity_df.pivot(
        index='zaihuang_cluster', columns='jinshi_cluster', values='similarity'
    )

    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap='YlGnBu', annot=False, fmt=".2f", linewidths=0.5)
    plt.title('灾荒聚类与进士聚类的综合时空相似度热力图')
    plt.xlabel('进士聚类编号')
    plt.ylabel('灾荒聚类编号')

    if save_path is None:
        save_path = os.path.join(OUTPUT_DIR, 'similarity_heatmap.png')
    plt.savefig(save_path, dpi=VISUALIZATION["dpi"], bbox_inches='tight')
    plt.close()
    print(f"相似度热力图已保存至 {save_path}")
    return save_path


def plot_cluster_comparison_2d(zaihuang_df, jinshi_df, z_cluster, j_cluster, save_path=None):
    setup_chinese_font()
    z_data = zaihuang_df[zaihuang_df['cluster'] == z_cluster]
    j_data = jinshi_df[jinshi_df['cluster'] == j_cluster]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    sns.histplot(z_data['year'], bins=30, color='red', label='灾荒', kde=True, ax=ax1)
    sns.histplot(j_data['EntryYear'], bins=30, color='blue', label='进士', kde=True, ax=ax1)
    ax1.set_title(f'时间分布对比（灾荒聚类{z_cluster} vs 进士聚类{j_cluster}）')
    ax1.set_xlabel('年份')
    ax1.legend()

    ax2.scatter(z_data['x'], z_data['y'], c='red', label='灾荒', alpha=0.6, s=50)
    ax2.scatter(j_data['X'], j_data['Y'], c='blue', label='进士', alpha=0.6, s=50)
    ax2.set_title(f'空间分布对比（灾荒聚类{z_cluster} vs 进士聚类{j_cluster}）')
    ax2.set_xlabel('经度')
    ax2.set_ylabel('纬度')
    ax2.legend()

    plt.tight_layout()

    if save_path is None:
        save_path = os.path.join(OUTPUT_DIR, f'cluster_comparison_z{z_cluster}_j{j_cluster}.png')
    plt.savefig(save_path, dpi=VISUALIZATION["dpi"], bbox_inches='tight')
    plt.close()
    print(f"聚类对比图已保存至 {save_path}")
    return save_path


def plot_bbox_overlap(zaihuang_clusters, jinshi_clusters, z_cluster, j_cluster, save_path=None):
    setup_chinese_font()
    z_box = zaihuang_clusters[zaihuang_clusters['cluster'] == z_cluster].iloc[0]
    j_box = jinshi_clusters[jinshi_clusters['cluster'] == j_cluster].iloc[0]

    plt.figure(figsize=(10, 6))

    plt.gca().add_patch(plt.Rectangle(
        (z_box['min_x'], z_box['min_y']),
        z_box['max_x'] - z_box['min_x'],
        z_box['max_y'] - z_box['min_y'],
        fill=False, color='red', linewidth=2, label=f'灾荒聚类{z_cluster}'
    ))
    plt.gca().add_patch(plt.Rectangle(
        (j_box['min_x'], j_box['min_y']),
        j_box['max_x'] - j_box['min_x'],
        j_box['max_y'] - j_box['min_y'],
        fill=False, color='blue', linewidth=2, label=f'进士聚类{j_cluster}'
    ))

    plt.title(f'空间边界框重叠情况（灾荒聚类{z_cluster} vs 进士聚类{j_cluster}）')
    plt.xlabel('经度')
    plt.ylabel('纬度')
    plt.legend()

    if save_path is None:
        save_path = os.path.join(OUTPUT_DIR, f'bbox_overlap_z{z_cluster}_j{j_cluster}.png')
    plt.savefig(save_path, dpi=VISUALIZATION["dpi"], bbox_inches='tight')
    plt.close()
    print(f"边界框重叠图已保存至 {save_path}")
    return save_path
