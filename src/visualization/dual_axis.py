import matplotlib

matplotlib.use('Agg')
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config import OUTPUT_DIR, VISUALIZATION


def setup_chinese_font():
    plt.rcParams['font.sans-serif'] = VISUALIZATION["font_sans_serif"]
    plt.rcParams['axes.unicode_minus'] = VISUALIZATION["axes_unicode_minus"]


def plot_dual_axis(scholar_count_by_year, disaster_count_by_year,
                   title='进士数量与灾荒次数年度趋势', save_path=None):
    setup_chinese_font()
    fig, ax1 = plt.subplots(figsize=VISUALIZATION["figsize_2d"])
    ax2 = ax1.twinx()

    line1 = ax1.plot(scholar_count_by_year.index, scholar_count_by_year.values,
                     'b-', label='进士数量')
    ax1.set_xlabel('年份')
    ax1.set_ylabel('进士数量', color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    line2 = ax2.plot(disaster_count_by_year.index, disaster_count_by_year.values,
                     'r-', label='灾荒次数')
    ax2.set_ylabel('灾荒次数', color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    ax1.set_xlim(1300, 1700)

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')

    plt.title(title)

    if save_path is None:
        save_path = os.path.join(OUTPUT_DIR, 'dual_axis_trend.png')
    plt.savefig(save_path, dpi=VISUALIZATION["dpi"], bbox_inches='tight')
    plt.close()
    print(f"双轴趋势图已保存至 {save_path}")
    return save_path


def plot_dual_axis_with_fit(scholar_count_by_year, disaster_count_by_year,
                            title='进士数量与灾荒次数年度趋势(含拟合)', save_path=None):
    setup_chinese_font()
    fig, ax1 = plt.subplots(figsize=VISUALIZATION["figsize_2d"])
    ax2 = ax1.twinx()

    years_s = scholar_count_by_year.index.values
    vals_s = scholar_count_by_year.values
    years_d = disaster_count_by_year.index.values
    vals_d = disaster_count_by_year.values

    mask_s = (years_s >= 1300) & (years_s <= 1700)
    mask_d = (years_d >= 1300) & (years_d <= 1700)

    if mask_s.sum() > 4:
        coeffs_s = np.polyfit(years_s[mask_s], vals_s[mask_s], 3)
        fit_s = np.polyval(coeffs_s, years_s[mask_s])
        ax1.plot(years_s[mask_s], fit_s, 'b-', label='进士拟合', linewidth=2)
    else:
        ax1.plot(years_s[mask_s], vals_s[mask_s], 'b-', label='进士数量')

    if mask_d.sum() > 4:
        coeffs_d = np.polyfit(years_d[mask_d], vals_d[mask_d], 3)
        fit_d = np.polyval(coeffs_d, years_d[mask_d])
        ax2.plot(years_d[mask_d], fit_d, 'r-', label='灾荒拟合', linewidth=2)
    else:
        ax2.plot(years_d[mask_d], vals_d[mask_d], 'r-', label='灾荒次数')

    ax1.set_xlabel('年份')
    ax1.set_ylabel('进士数量', color='b')
    ax2.set_ylabel('灾荒次数', color='r')
    ax1.set_xlim(1300, 1700)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    plt.title(title)

    if save_path is None:
        save_path = os.path.join(OUTPUT_DIR, 'dual_axis_trend_fitted.png')
    plt.savefig(save_path, dpi=VISUALIZATION["dpi"], bbox_inches='tight')
    plt.close()
    print(f"双轴拟合趋势图已保存至 {save_path}")
    return save_path
