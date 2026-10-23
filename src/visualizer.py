import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import squarify

sns.set_theme(style="whitegrid")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"

def ensure_output_dir(save_path):
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

def plot_rfm_treemap(rfm_df, save_path):
    segment_counts = rfm_df["segment"].value_counts().reset_index()
    segment_counts.columns = ["segment", "count"]
    total_customers = segment_counts["count"].sum()
    labels = [
        f"{row['segment']}\n{row['count']:,} ({row['count']/total_customers:.1%})"
        for _, row in segment_counts.iterrows()
    ]
    colors = sns.color_palette("Spectral", len(segment_counts))
    plt.figure(figsize=(14, 8))
    squarify.plot(
        sizes=segment_counts["count"],
        label=labels,
        color=colors,
        alpha=0.85,
        text_kwargs={"fontsize": 10, "weight": "bold"}
    )
    plt.title("Müşteri Segment Dağılımı (RFM Treemap)", fontsize=16, weight="bold", pad=15)
    plt.axis("off")
    plt.tight_layout()

    if save_path:
        ensure_output_dir(save_path)
        plt.savefig(save_path, dpi=300)
    plt.close()

def plot_segment_summary_heatmap(rfm_df, save_path):
    agg_df = rfm_df.groupby("segment").agg(
        mean_recency=("recency", "mean"),
        mean_frequency=("frequency", "mean"),
        mean_monetary=("monetary", "mean"),
        customer_count=("master_id", "count")
    ).round(1)
    metrics_to_show = ["mean_recency", "mean_frequency", "mean_monetary"]
    normalized_matrix = (agg_df[metrics_to_show] - agg_df[metrics_to_show].min()) / (
            agg_df[metrics_to_show].max() - agg_df[metrics_to_show].min()
    )
    plt.figure(figsize=(10, 6))
    sns.heatmap(
        normalized_matrix,
        annot=agg_df[metrics_to_show],
        fmt=".1f",
        cmap="Blues",
        cbar=False,
        linewidths=0.5
    )
    plt.title("Segment Profil Ortalamaları (Isı Haritası)", fontsize=14, weight="bold", pad=15)
    plt.ylabel("Segmentler", fontsize=11)
    plt.xlabel("Ortalama Metrikler", fontsize=11)
    plt.tight_layout()

    if save_path:
        ensure_output_dir(save_path)
        plt.savefig(save_path, dpi=300)
    plt.close()

def plot_omnichannel_distribution(df, save_path):
    channel_summary = df.groupby("order_channel").agg(
        total_orders=("order_num_total", "sum"),
        total_revenue=("customer_value_total", "sum")
    ).reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    #sipariş sayısı
    sns.barplot(data=channel_summary, x="order_channel", y="total_orders", hue="order_channel", ax=axes[0], palette="Blues_d", legend=False)
    axes[0].set_title("Kanal Bazlı Toplam Sipariş Sayısı", fontsize=12, weight="bold")
    axes[0].set_ylabel("Toplam Sipariş")
    axes[0].set_xlabel("Alışveriş Kanalı")

    #toplam kazanç
    sns.barplot(data=channel_summary, x="order_channel", y="total_revenue", hue="order_channel", ax=axes[1], palette="Greens_d", legend=False)
    axes[1].set_title("Kanal Bazlı Toplam Ciro (TL)", fontsize=12, weight="bold")
    axes[1].set_ylabel("Toplam Harcama (TL)")
    axes[1].set_xlabel("Alışveriş Kanalı")

    plt.tight_layout()

    if save_path:
        ensure_output_dir(save_path)
        plt.savefig(save_path, dpi=300)
    plt.close()