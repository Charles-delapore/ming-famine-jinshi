import matplotlib

matplotlib.use('Agg')
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config import OUTPUT_DIR, VISUALIZATION


def setup_chinese_font():
    plt.rcParams['font.sans-serif'] = VISUALIZATION["font_sans_serif"]
    plt.rcParams['axes.unicode_minus'] = VISUALIZATION["axes_unicode_minus"]


def plot_3d_scatter(data, x_col, y_col, z_col, c_col, title='3D Scatter',
                    save_path=None, cmap='tab20'):
    setup_chinese_font()
    fig = plt.figure(figsize=VISUALIZATION["figsize_3d"])
    ax = fig.add_subplot(111, projection='3d')

    scatter = ax.scatter(
        data[x_col], data[y_col], data[z_col],
        c=data[c_col], cmap=cmap, s=40, alpha=0.8, edgecolor='w'
    )

    ax.set_xlabel('经度')
    ax.set_ylabel('纬度')
    ax.set_zlabel('年份')
    plt.colorbar(scatter)
    plt.title(title)

    if save_path is None:
        save_path = os.path.join(OUTPUT_DIR, title.replace(' ', '_') + '.png')
    plt.savefig(save_path, dpi=VISUALIZATION["dpi"], bbox_inches='tight')
    plt.close()
    print(f"3D图已保存至 {save_path}")
    return save_path


def plot_zaihuang_3d(data, title='SSDBSCAN灾荒聚类'):
    return plot_3d_scatter(data, 'x', 'y', 'year', 'cluster', title)


def plot_jinshi_3d(data, title='SSDBSCAN进士聚类'):
    return plot_3d_scatter(data, 'X', 'Y', 'EntryYear', 'cluster', title)


def plot_comparison_3d(jinshi_df, zaihuang_df, title='时空聚类三维分布'):
    setup_chinese_font()
    fig = plt.figure(figsize=VISUALIZATION["figsize_3d"])
    ax = fig.add_subplot(111, projection='3d')

    for _, cluster in jinshi_df.groupby('cluster'):
        ax.scatter(cluster['X'], cluster['Y'], cluster['EntryYear'],
                   c='blue', s=30, alpha=0.6, label='进士聚类')

    for _, cluster in zaihuang_df.groupby('cluster'):
        ax.scatter(cluster['x'], cluster['y'], cluster['year'],
                   c='red', s=30, alpha=0.6, marker='^', label='灾荒聚类')

    ax.set_xlabel('经度')
    ax.set_ylabel('纬度')
    ax.set_zlabel('年份')
    ax.set_title(title)

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())

    save_path = os.path.join(OUTPUT_DIR, 'comparison_3d.png')
    plt.savefig(save_path, dpi=VISUALIZATION["dpi"], bbox_inches='tight')
    plt.close()
    print(f"对比3D图已保存至 {save_path}")
    return save_path
