import pandas as pd
import numpy as np
import pytest
from src.data_prep import clean_and_transform_dates, create_omnichannel_features

@pytest.fixture
def sample_raw_dataframe():
    #testler için örnek ham veri seti üretilir ve her testte kullanılır.
    data = {
        "master_id": ["cust_1", "cust_2", "cust_3"],
        "order_num_total_ever_online": [3.0, 0.0, 5.0],
        "order_num_total_ever_offline": [2.0, 4.0, 0.0],
        "customer_value_total_ever_online": [300.0, 0.0, 1000.0],
        "customer_value_total_ever_offline": [200.0, 400.0, 0.0],
        "first_order_date": ["2020-05-15", "2021-01-10", "2020-11-20"],
        "last_order_date": ["2021-04-10", "2021-05-25", "2021-02-18"],
        "interested_in_categories": ["[KADIN]", "[ERKEK, COCUK]", "[KADIN, AKTIFSPOR]"]
    }
    return pd.DataFrame(data)

def test_clean_and_transform_dates(sample_raw_dataframe):
    transformed = clean_and_transform_dates(sample_raw_dataframe)

    assert pd.api.types.is_datetime64_any_dtype(transformed["first_order_date"])
    assert pd.api.types.is_datetime64_any_dtype(transformed["first_order_date"])
    assert not transformed["last_order_date"].isnull().any()

def test_create_omnichannel_features(sample_raw_dataframe):
    result = create_omnichannel_features(sample_raw_dataframe)

    #toplam sipariş kontrolleri
    assert result.loc[0, "order_num_total"] == 5.0
    assert result.loc[1, "order_num_total"] == 4.0

    #toplam harcama kontrolleri
    assert result.loc[0, "customer_value_total"] == 500.0
    assert result.loc[2, "customer_value_total"] == 1000.0

    #online alışveriş oranı kontrolleri
    assert result.loc[1, "online_order_ratio"] == 0.0
    assert result.loc[2, "online_order_ratio"] == 1.0

    #oranların [0, 1] aralığınd aolduğunu doğrular
    assert (result["online_order_ratio"] >= 0.0).all()
    assert (result["online_order_ratio"] <= 1.0).all()
