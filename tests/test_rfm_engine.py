import datetime as dt
import pandas as pd
import pytest
from src.rfm_engine import calculate_rfm_metrics, calculate_rfm_scores, map_rfm_segments, create_rfm_pipeline

@pytest.fixture
def sample_clean_dataframe():
    data = {
        "master_id": [f"user_{i}" for i in range(1, 11)],
        "last_order_date": pd.to_datetime([
            "2021-05-30", "2021-05-28", "2021-04-15", "2021-03-10", "2021-02-01",
            "2021-01-20", "2020-12-10", "2020-11-05", "2020-10-01", "2020-06-15"
        ]),
        "order_num_total": [12, 10, 8, 7, 5, 4, 3, 2, 2, 1],
        "customer_value_total": [2500.0, 2100.0, 1800.0, 1400.0, 950.0, 800.0, 600.0, 450.0, 300.0, 150.0]
    }
    return pd.DataFrame(data)

def test_calculate_rfm_metrics(sample_clean_dataframe):
    analysis_date = pd.to_datetime("2021-06-01")
    rfm = calculate_rfm_metrics(sample_clean_dataframe, analysis_date)

    #recency negatif olamaz
    assert (rfm["recency"] > 0).all()

    assert rfm.loc[0, "recency"] == 2

    #önemli olan sütunlar eklendi mi kontrol edilir
    assert set(["master_id", "recency", "frequency", "monetary"]).issubset(rfm.columns)

def test_calculate_rfm_scores(sample_clean_dataframe):
    analysis_date = pd.to_datetime("2021-06-01")
    rfm = calculate_rfm_metrics(sample_clean_dataframe, analysis_date)
    rfm_scored = calculate_rfm_scores(rfm)

    #skorların 1-5 aralığında skorlandığı doğrulanır
    for score_col in ["recency_score", "frequency_score", "monetary_score"]:
        scores = rfm_scored[score_col].astype(int)
        assert scores.min() >= 1
        assert scores.max() <= 5

    assert rfm_scored["RF_SCORE"].str.len().eq(2).all()

def test_rfm_pipeline_end_to_end(sample_clean_dataframe):
    final_rfm = create_rfm_pipeline(sample_clean_dataframe)

    #segmentsiz müşteri kalmamalı
    assert not final_rfm["segment"].isnull().any()

    #segmentler string olmalı
    assert final_rfm["segment"].dtype == "object"

    #satır sayısı ham veri ile eşleşmeli
    assert len(final_rfm) == len(sample_clean_dataframe)