import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config import DATA_PATHS, OUTPUT_PATHS, DATA_PROCESSED_DIR
from src.data_processing.jinshi_rank import normalize_rank


def load_zaihuang_data(city_file=None, level_file=None):
    city_file = city_file or DATA_PATHS["table_citys"]
    level_file = level_file or DATA_PATHS["table_level"]

    cities = pd.read_excel(city_file, sheet_name='Sheet1')
    cities = cities[['code', 'x', 'y']].drop_duplicates('code')

    levels = pd.read_excel(level_file, sheet_name='Sheet1')
    levels['year'] = levels['year'].astype(int)

    merged = pd.merge(levels, cities, on='code')
    return merged


def load_zaihuang_data_full(city_file=None, level_file=None):
    city_file = city_file or DATA_PATHS["table_citys"]
    level_file = level_file or DATA_PATHS["table_level"]

    cities = pd.read_excel(city_file, sheet_name='Sheet1')
    cities = cities.drop_duplicates('code', keep='first')

    levels = pd.read_excel(level_file, sheet_name='Sheet1')
    levels['year'] = levels['year'].astype(int)

    merged = pd.merge(levels, cities, on='code', how='outer', suffixes=('_level', '_city'))
    merged = merged.drop(columns=[col for col in merged.columns if 'Unnamed' in col])
    return merged


def load_jinshi_data(general_file=None):
    general_file = general_file or DATA_PATHS["table_general"]
    data = pd.read_excel(general_file).dropna(subset=['EntryRank'])
    return data


def load_jinshi_important(general_file=None):
    data = load_jinshi_data(general_file)
    data = normalize_rank(data)
    important_data = data[data["level"].isin([1, 2])]
    important_data = important_data.dropna(subset=["EntryYear"])
    return important_data


def merge_level_city(level_path=None, city_path=None):
    level_path = level_path or DATA_PATHS["table_level"]
    city_path = city_path or DATA_PATHS["table_citys"]

    table1 = pd.read_excel(level_path, sheet_name='Sheet1')
    table2 = pd.read_excel(city_path, sheet_name='Sheet1')
    data = pd.merge(table1, table2, on='code')
    result = data[['year', 'code', 'level', 'x', 'y']].copy()
    return result


def save_processed(data, filename):
    os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)
    filepath = os.path.join(DATA_PROCESSED_DIR, filename)
    if filepath.endswith('.csv'):
        data.to_csv(filepath, index=False)
    else:
        data.to_excel(filepath, index=False, engine='openpyxl')
    print(f"数据已保存至 {filepath}")
    return filepath


def load_extended_zaihuang(city_file=None, ext_file=None):
    city_file = city_file or DATA_PATHS["table_citys"]
    ext_file = ext_file or DATA_PATHS["table_generals1521_1619"]

    cities = pd.read_excel(city_file, sheet_name='Sheet1')
    cities = cities[['code', 'x', 'y']].drop_duplicates('code')

    ext = pd.read_excel(ext_file, engine='openpyxl')
    ext['year'] = ext['year'].astype(int)
    ext = ext[['year', 'code', 'level']].copy()

    merged = pd.merge(ext, cities, on='code', how='inner')
    merged = merged.rename(columns={'x': 'X', 'y': 'Y'})
    return merged


def load_extended_jinshi(ext_file=None):
    ext_file = ext_file or DATA_PATHS["table_general2"]

    data = pd.read_excel(ext_file, engine="openpyxl")
    data = data.dropna(subset=["EntryRank"])
    data = normalize_rank(data)
    important = data[data["level"].isin([1, 2])]
    important = important.dropna(subset=["EntryYear"])
    important["EntryYear"] = important["EntryYear"].astype(int)
    result = important[["EntryYear", "X", "Y", "level", "EntryRank"]].copy()
    return result
