import os
from pathlib import Path
from typing import List, Optional, Union
import pandas as pd

def ensure_output_dir(output_path):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

def get_target_customers(df, rfm, target_segments, category_regex, min_monetary_score):
    merged_df = df.merge(rfm[["master_id", "segment", "monetary_score"]], on="master_id", how="left")

    condition = merged_df["segment"].isin(target_segments)
    if category_regex:
        condition &= merged_df["interested_in_categories_12"].str.contains(category_regex, na=False)

    if min_monetary_score is not None:
        condition &= merged_df["monetary_score"].astype(int) >= min_monetary_score

    return merged_df[condition]

def export_action_segments(df, rfm, output_dir):
    results = {}

    # Senaryo A: Yeni Lüks Kadın Markası Lansmanı
    # Hedef: Champions, Loyal Customers + Kadın Kategorisi
    luxury_women = get_target_customers(
        df=df,
        rfm=rfm,
        target_segments=["champions", "loyal_customers"],
        category_regex="KADIN",
        min_monetary_score=None
    )
    path_a = os.path.join(output_dir, "target_luxury_women_campaign.csv")
    ensure_output_dir(path_a)
    luxury_women[["master_id"]].to_csv(path_a, index=False)
    results["luxury_women_count"] = len(luxury_women)

    # Senaryo B: Erkek & Çocuk Kategorisi %40 İndirim Kampanyası
    # Hedef: cant_loose, at_Risk, hibernating, new_customers + Erkek veya Çocuk Kategorisi
    discount_target = get_target_customers(
        df=df,
        rfm=rfm,
        target_segments=["cant_loose", "at_Risk", "hibernating", "new_customers"],
        category_regex="ERKEK|ÇOCUK",
        min_monetary_score=None
    )
    path_b = os.path.join(output_dir, "target_discount_men_kids_campaign.csv")
    ensure_output_dir(path_b)
    discount_target[["master_id"]].to_csv(path_b, index=False)
    results["discount_target_count"] = len(discount_target)

    return results

def generate_segment_profiles(rfm_df):
    summary = rfm_df.groupby("segment").agg(
        customer_count=("master_id", "count"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        total_revenue=("monetary", "sum")
    ).reset_index()

    total_customers = summary["customer_count"].sum()
    total_revenue = summary["total_revenue"].sum()

    summary["customer_ratio_%"] = ((summary["customer_count"] / total_customers) * 100).round(2)
    summary["revenue_ratio_%"] = ((summary["total_revenue"] / total_revenue) * 100).round(2)

    return summary.sort_values(by="total_revenue", ascending=False).round(2)