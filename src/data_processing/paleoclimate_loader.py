import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config import DATA_PATHS


def load_mann2009_nh_temp(filepath=None):
    filepath = filepath or DATA_PATHS["mann2009_nhall"]
    df = pd.read_csv(filepath, sep=r'\s+', header=None,
                     names=['year', 'nh_temp_anomaly', 'nh_temp_lower', 'nh_temp_upper'])
    df['year'] = df['year'].astype(int)
    return df


def load_mann2009_amo(filepath=None):
    filepath = filepath or DATA_PATHS["mann2009_amo"]
    df = pd.read_csv(filepath, sep=r'\s+', header=None,
                     names=['year', 'amo_index', 'amo_lower', 'amo_upper'])
    df['year'] = df['year'].astype(int)
    return df


def load_schneider2015_temp(filepath=None):
    filepath = filepath or DATA_PATHS["schneider2015_temp"]
    data_lines = []
    var_names = []
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('##'):
                parts = stripped[2:].strip().split('\t')
                if len(parts) >= 1:
                    var_names.append(parts[0].strip())
                continue
            if stripped.startswith('#'):
                continue
            if stripped == '':
                continue
            try:
                vals = [float(v) for v in stripped.split() if v]
                if vals:
                    data_lines.append(vals)
            except ValueError:
                continue

    if not data_lines:
        return pd.DataFrame()

    max_cols = max(len(row) for row in data_lines)
    for i in range(len(data_lines)):
        while len(data_lines[i]) < max_cols:
            data_lines[i].append(np.nan)

    if var_names and len(var_names) >= max_cols:
        col_names = var_names[:max_cols]
    else:
        col_names = ['age_AD', 'tempanom-JJA', 'tempanom-JJA-', 'tempanom-JJA+', 'tempanom-JJAtarg'][:max_cols]
        if max_cols > 5:
            col_names += [f'col_{i}' for i in range(5, max_cols)]

    df = pd.DataFrame(data_lines, columns=col_names)
    if 'age_AD' in df.columns:
        df = df.rename(columns={'age_AD': 'year'})
    if 'year' in df.columns:
        df['year'] = df['year'].astype(int)

    instrument_cols = [c for c in df.columns if 'targ' in c.lower()]
    for col in instrument_cols:
        n_valid = df[col].notna().sum()
        if n_valid > 0:
            valid_years = df.loc[df[col].notna(), 'year']
            if valid_years.min() > 1850:
                print(f"    Schneider2015温度: 列'{col}'为仪器观测数据({valid_years.min()}-{valid_years.max()}), "
                      f"与明代数据无重叠, 已排除")
                df = df.drop(columns=[col])

    df = df.replace(-9999, np.nan)

    return df


def load_schneider2015_mxd(filepath=None):
    filepath = filepath or DATA_PATHS["schneider2015_mxd"]
    data_lines = []
    var_names = []
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('##'):
                parts = stripped[2:].strip().split('\t')
                if len(parts) >= 1:
                    var_names.append(parts[0].strip())
                continue
            if stripped.startswith('#'):
                continue
            if stripped == '':
                continue
            try:
                vals = [float(v) for v in stripped.split() if v]
                if vals:
                    data_lines.append(vals)
            except ValueError:
                continue

    if not data_lines:
        return pd.DataFrame()

    max_cols = max(len(row) for row in data_lines)
    for i in range(len(data_lines)):
        while len(data_lines[i]) < max_cols:
            data_lines[i].append(np.nan)

    if var_names and len(var_names) >= max_cols:
        col_names = var_names[:max_cols]
    else:
        col_names = ['age_AD', 'mxd_value', 'mxd_lower', 'mxd_upper'][:max_cols]
        if max_cols > 4:
            col_names += [f'col_{i}' for i in range(4, max_cols)]

    df = pd.DataFrame(data_lines, columns=col_names)
    if 'age_AD' in df.columns:
        df = df.rename(columns={'age_AD': 'year'})
    if 'year' in df.columns:
        df['year'] = df['year'].astype(int)

    df = df.replace(-9999, np.nan)

    return df


def load_all_paleoclimate_data():
    datasets = {}

    print("加载Mann et al. 2009 北半球温度重建...")
    try:
        nh_temp = load_mann2009_nh_temp()
        datasets['mann2009_nh_temp'] = nh_temp
        print(f"  北半球温度: {len(nh_temp)} 年 ({nh_temp['year'].min()}-{nh_temp['year'].max()})")
    except Exception as e:
        print(f"  加载失败: {e}")

    print("加载Mann et al. 2009 AMO重建...")
    try:
        amo = load_mann2009_amo()
        datasets['mann2009_amo'] = amo
        print(f"  AMO指数: {len(amo)} 年 ({amo['year'].min()}-{amo['year'].max()})")
    except Exception as e:
        print(f"  加载失败: {e}")

    print("加载Schneider et al. 2015 MXD温度重建...")
    try:
        temp = load_schneider2015_temp()
        datasets['schneider2015_temp'] = temp
        if len(temp) > 0:
            value_cols = [c for c in temp.columns if c != 'year']
            print(f"  温度重建: {len(temp)} 年, 变量: {value_cols}")
            for vc in value_cols:
                n_valid = temp[vc].notna().sum()
                valid_range = temp.loc[temp[vc].notna(), 'year']
                if len(valid_range) > 0:
                    print(f"    {vc}: {n_valid} 有效值 ({int(valid_range.min())}-{int(valid_range.max())})")
    except Exception as e:
        print(f"  加载失败: {e}")

    print("加载Schneider et al. 2015 MXD年表...")
    try:
        mxd = load_schneider2015_mxd()
        datasets['schneider2015_mxd'] = mxd
        if len(mxd) > 0:
            value_cols = [c for c in mxd.columns if c != 'year']
            print(f"  MXD年表: {len(mxd)} 年, {len(value_cols)} 个站点")
            for vc in value_cols:
                n_valid = mxd[vc].notna().sum()
                valid_range = mxd.loc[mxd[vc].notna(), 'year']
                if len(valid_range) > 0:
                    print(f"    {vc}: {n_valid} 有效值 ({int(valid_range.min())}-{int(valid_range.max())})")
    except Exception as e:
        print(f"  加载失败: {e}")

    return datasets


def merge_paleoclimate_with_grid(grid_data, paleoclimate_datasets, year_col='year'):
    merged = grid_data.copy()

    for key, pc_df in paleoclimate_datasets.items():
        if len(pc_df) == 0 or 'year' not in pc_df.columns:
            continue

        overlap_start = max(merged[year_col].min(), pc_df['year'].min())
        overlap_end = min(merged[year_col].max(), pc_df['year'].max())

        if overlap_start > overlap_end:
            print(f"  {key}: 无时间重叠 (数据: {pc_df['year'].min()}-{pc_df['year'].max()}, "
                  f"格网: {merged[year_col].min()}-{merged[year_col].max()})")
            continue

        value_cols = [c for c in pc_df.columns if c != 'year']
        pc_subset = pc_df[['year'] + value_cols].copy()

        merged = merged.merge(pc_subset, on='year', how='left')

        for vc in value_cols:
            n_valid = merged[vc].notna().sum()
            if n_valid == 0:
                print(f"  {key}.{vc}: 合并后 0 条有效值 (重叠期 {int(overlap_start)}-{int(overlap_end)}) "
                      f"[该变量在重叠期无数据, 已标记排除]")
            else:
                print(f"  {key}.{vc}: 合并后 {n_valid} 条有效值 "
                      f"(重叠期 {int(overlap_start)}-{int(overlap_end)})")

    return merged
