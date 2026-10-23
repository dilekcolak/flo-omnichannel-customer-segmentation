import pandas as pd
import os
from pathlib import Path

def load_data(file_path):
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Veri dosyası belirtilen konumda bulunamadı: {path.resolve()}")

    return pd.read_csv(path)

def clean_and_transform_dates(df, date_suffix="_date"):
    df = df.copy()
    date_cols = [col for col in df.columns if date_suffix in col]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

def create_omnichannel_features(df):
    df = df.copy()
    df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
    df["customer_value_total"] = df["customer_value_total_ever_online"] + df["customer_value_total_ever_offline"]
    df["online_order_ratio"] = (df["order_num_total_ever_online"] / df["order_num_total"].replace(0, pd.NA)).fillna(0.0).round(3)
    df["online_value_ratio"] = (df["customer_value_total_ever_online"] / df["customer_value_total"].replace(0, pd.NA)).fillna(0.0).round(3)
    return df

def prep_data_pipeline(file_path):
    df = load_data(file_path)
    df = clean_and_transform_dates(df)
    df = create_omnichannel_features(df)
    return df