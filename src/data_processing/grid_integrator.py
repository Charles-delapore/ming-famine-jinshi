import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config import DATA_PATHS, OUTPUT_PATHS, GRID_PARAMS


def integrate_grid_data(general_csv=None, merged_csv=None, params=None):
    params = params or GRID_PARAMS
    general_csv = general_csv or DATA_PATHS["ming_general"]
    merged_csv = merged_csv or DATA_PATHS["merged_data"]

    df_general = pd.read_csv(general_csv)
    df_merged = pd.read_csv(merged_csv)

    x_min = params["x_min"]
    x_max = params["x_max"]
    y_min = params["y_min"]
    y_max = params["y_max"]
    grid_size = params["grid_size"]
    num_x = int((x_max - x_min) / grid_size)
    num_y = int((y_max - y_min) / grid_size)

    results = []
    for year in range(params["year_start"], params["year_end"]):
        print(f"处理年份: {year}")
        year_data = df_general[df_general['EntryYear'] == year]
        year_merged_data = df_merged[df_merged['year'] == year]
        for i in range(num_x):
            for j in range(num_y):
                x_center = x_min + i * grid_size + 0.5 * grid_size
                y_center = y_min + j * grid_size + 0.5 * grid_size

                mask1 = (
                    (year_data['X'] >= x_min + i * grid_size) &
                    (year_data['X'] < x_min + (i + 1) * grid_size) &
                    (year_data['Y'] >= y_min + j * grid_size) &
                    (year_data['Y'] < y_min + (j + 1) * grid_size)
                )
                level_g = mask1.sum()

                mask2 = (
                    (year_merged_data['X'] >= x_min + i * grid_size) &
                    (year_merged_data['X'] < x_min + (i + 1) * grid_size) &
                    (year_merged_data['Y'] >= y_min + j * grid_size) &
                    (year_merged_data['Y'] < y_min + (j + 1) * grid_size)
                )
                filtered_data = year_merged_data[mask2]
                level_d = filtered_data['level'].max() if not filtered_data.empty else 0

                results.append({
                    'Year': year,
                    'Center_X': x_center,
                    'Center_Y': y_center,
                    'LevelG': level_g,
                    'LevelD': level_d,
                })

    result_df = pd.DataFrame(results)
    return result_df
