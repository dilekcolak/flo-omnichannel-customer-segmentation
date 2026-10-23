import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import squarify
import os

from src.data_prep import prep_data_pipeline
from src.rfm_engine import create_rfm_pipeline

# Sayfa Konfigürasyonu
st.set_page_config(
    page_title="FLO Omnichannel RFM Analiz Paneli",
    page_icon="👟",
    layout="wide"
)

st.title("👟 FLO Müşteri Segmentasyon & RFM Karar Destek Paneli")
st.markdown("Omnichannel müşteri davranış analizi, RFM skorlaması ve dinamik hedef kitle filtreleme sistemi.")


# Veriyi Önbelleğe Alarak Yükleme
@st.cache_data
def load_and_process():
    path = "data/raw/flo_data_20k.csv"
    if not os.path.exists(path):
        path = "datasets/flo_data_20k.csv"

    df = prep_data_pipeline(path)
    rfm_df = create_rfm_pipeline(df)
    full_df = df.merge(rfm_df[["master_id", "recency", "frequency", "monetary", "recency_score", "frequency_score",
                               "monetary_score", "RF_SCORE", "segment"]], on="master_id")
    return full_df


try:
    data = load_and_process()
except Exception as e:
    st.error(
        f"Veri yüklenirken hata oluştu: {e}. Lütfen veri dosyasının data/raw/ veya datasets/ altında olduğunu doğrulayın.")
    st.stop()

# --- KPI METRİKLERİ ---
col1, col2, col3, col4 = st.columns(4)
total_customers = data["master_id"].nunique()
total_rev = data["customer_value_total"].sum()
avg_order = data["order_num_total"].mean()
top_segment = data["segment"].mode()[0]

col1.metric("Toplam Müşteri", f"{total_customers:,}")
col2.metric("Toplam Ciro (TL)", f"₺{total_rev:,.2f}")
col3.metric("Müşteri Başına Ort. Sipariş", f"{avg_order:.2f}")
col4.metric("En Kalabalık Segment", top_segment.replace("_", " ").title())

st.divider()

# --- YAN PANEL: DİNAMİK FİLTRELEME ---
st.sidebar.header("🎯 Hedef Kitle Filtreleri")

all_segments = sorted(data["segment"].unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Segment Seçiniz:",
    options=all_segments,
    default=["champions", "loyal_customers"]
)

category_search = st.sidebar.text_input(
    "Kategori İlgisi (Örn: KADIN, ERKEK, AKTIFCOCUK):",
    value=""
)

min_monetary = st.sidebar.slider(
    "Minimum Harcama Tutarı (TL):",
    min_value=float(data["monetary"].min()),
    max_value=float(data["monetary"].max()),
    value=float(data["monetary"].min())
)

# Filtreleri Uygula
filtered_df = data[
    (data["segment"].isin(selected_segments)) &
    (data["monetary"] >= min_monetary)
    ]

if category_search.strip():
    filtered_df = filtered_df[
        filtered_df["interested_in_categories_12"].str.contains(category_search.strip(), case=False, na=False)
    ]

# --- SEKMELER ---
tab1, tab2, tab3 = st.tabs(
    ["📋 Hedef Kitle Tablosu & Dışa Aktar", "📊 Segment Görselleştirmeleri", "🏢 Omnichannel Dinamikleri"])

with tab1:
    st.subheader(f"Filtrelenmiş Kitle ({len(filtered_df):,} Müşteri)")

    show_cols = [
        "master_id", "segment", "recency", "frequency", "monetary",
        "order_channel", "interested_in_categories_12", "online_order_ratio"
    ]
    st.dataframe(filtered_df[show_cols].head(100), use_container_width=True)

    # CSV İndirme Butonu
    csv_data = filtered_df[["master_id"]].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Bu Kitleyi İndir (master_id.csv)",
        data=csv_data,
        file_name="hedef_kitle_kampanya.csv",
        mime="text/csv",
    )

with tab2:
    st.subheader("Müşteri Tabanı Segment Dağılımı")
    seg_counts = data["segment"].value_counts().reset_index()
    seg_counts.columns = ["segment", "count"]

    labels = [
        f"{r['segment']}\n{r['count']:,} ({r['count'] / len(data):.1%})"
        for _, r in seg_counts.iterrows()
    ]

    fig, ax = plt.subplots(figsize=(12, 6))
    squarify.plot(
        sizes=seg_counts["count"],
        label=labels,
        color=sns.color_palette("Spectral", len(seg_counts)),
        alpha=0.85,
        ax=ax,
        text_kwargs={"fontsize": 9, "weight": "bold"}
    )
    plt.axis("off")
    st.pyplot(fig)

with tab3:
    st.subheader("Omnichannel Alışveriş Alışkanlıkları")
    c1, c2 = st.columns(2)

    with c1:
        st.write("**Kanal Tercihlerine Göre Sipariş Dağılımı**")
        channel_orders = data.groupby("order_channel")["order_num_total"].sum()
        st.bar_chart(channel_orders)

    with c2:
        st.write("**Kanal Tercihlerine Göre Ciro Payı (TL)**")
        channel_rev = data.groupby("order_channel")["customer_value_total"].sum()
        st.bar_chart(channel_rev)