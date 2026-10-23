import pandas as pd
import datetime as dt

DEFAULT_SEG_MAP = {
    r"[1-2][1-2]": "hibernating",
    r"[1-2][3-4]": "at_Risk",
    r"[1-2][5]": "cant_loose",
    r"[3][1-2]": "about_to_sleep",
    r"[3][3]": "need_attention",
    r"[3-4][4-5]": "loyal_customers",
    r"[4][1]": "promising",
    r"[5][1]": "new_customers",
    r"[4-5][2-3]": "potential_loyalist",
    r"[5][4-5]": "champions",
}

def calculate_rfm_metrics(df, analysis_date):
    rfm = pd.DataFrame()
    rfm["master_id"] = df["master_id"]
    rfm["recency"] = (analysis_date - df["last_order_date"]).dt.days
    rfm["frequency"] = df["order_num_total"].astype(int)
    rfm["monetary"] = df["customer_value_total"].round(2)
    return rfm

def calculate_rfm_scores(rfm):
    rfm = rfm.copy()
    rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])
    rfm["rfm"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str) + rfm["monetary_score"].astype(str)
    rfm["RF_SCORE"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str)
    return rfm

def map_rfm_segments(rfm, seg_map):
    rfm=rfm.copy()
    if seg_map is None:
        seg_map = DEFAULT_SEG_MAP
    rfm["segment"] = rfm["RF_SCORE"].replace(seg_map, regex=True)
    return rfm

def create_rfm_pipeline(df, analysis_date=None, seg_map=None):
    if analysis_date is None:
        analysis_date = df["last_order_date"].max() + dt.timedelta(days=2)
    rfm = calculate_rfm_metrics(df, analysis_date)
    rfm = calculate_rfm_scores(rfm)
    rfm = map_rfm_segments(rfm, seg_map)
    return rfm