import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.data_prep import prep_data_pipeline
from src.rfm_engine import create_rfm_pipeline
from src.visualizer import (
    plot_rfm_treemap,
    plot_segment_summary_heatmap,
    plot_omnichannel_distribution
)
from src.business_actions import (
    export_action_segments,
    generate_segment_profiles
)


def run_pipeline(
        raw_data_path: str = "data/raw/flo_data_20k.csv",
        output_dir: str = "data/processed",
        figure_dir: str = "reports/figures"
):
    print("*" * 60)
    print("FLO OMNICHANNEL RFM ANALYTICS PIPELINE BASLATLIYOR")
    print("*" * 60)

    print("\n[1/4] Veri okunuyor ve öznitelikler türetiliyor...")
    df = prep_data_pipeline(raw_data_path)
    print(f"-> Veri hazırlandı: {df.shape[0]:,} satır, {df.shape[1]} sütun.")

    print("\n[2/4] RFM metrikleri hesaplanıyor ve segmentasyon yapılıyor...")
    rfm_df = create_rfm_pipeline(df)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    rfm_output_path = os.path.join(output_dir, "rfm_segmented_customers.csv")
    rfm_df.to_csv(rfm_output_path, index=False)
    print(f"-> RFM sonuçları kaydedildi: {rfm_output_path}")

    print("\n[3/4] Grafiksel analizler ve rapor görselleri üretiliyor...")
    Path(figure_dir).mkdir(parents=True, exist_ok=True)

    plot_rfm_treemap(rfm_df, save_path=os.path.join(figure_dir, "rfm_treemap.png"))
    plot_segment_summary_heatmap(rfm_df, save_path=os.path.join(figure_dir, "segment_heatmap.png"))
    plot_omnichannel_distribution(df, save_path=os.path.join(figure_dir, "channel_distribution.png"))
    print(f"-> Grafikler kaydedildi: {figure_dir}/")

    print("\n[4/4] Kampanya hedef kitle listeleri dışa aktarılıyor...")
    campaign_res = export_action_segments(df, rfm_df, output_dir=output_dir)
    print(f"-> Lüks Kadın Markası Hedef Kitle: {campaign_res['luxury_women_count']:,} müşteri")
    print(f"-> İndirim Kampanyası Hedef Kitle: {campaign_res['discount_target_count']:,} müşteri")

    summary_df = generate_segment_profiles(rfm_df)
    summary_path = os.path.join(output_dir, "segment_business_summary.csv")
    summary_df.to_csv(summary_path, index=False)
    print(f"-> Segment yönetim özeti kaydedildi: {summary_path}")

    print("\n" + "*" * 60)
    print(" TÜM ADIMLAR BASARIYLA TAMAMLANDI!")
    print("*" * 60)


if __name__ == "__main__":
    DATA_PATH = "data/raw/flo_data_20k.csv"

    if not os.path.exists(DATA_PATH):
        if os.path.exists("datasets/flo_data_20k.csv"):
            DATA_PATH = "datasets/flo_data_20k.csv"

    run_pipeline(raw_data_path=DATA_PATH)