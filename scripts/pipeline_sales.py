import json, pathlib, pandas as pd, numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

BASE = pathlib.Path(__file__).resolve().parents[1]
DATA = BASE / "data" / "sales.xlsx"
DIST = BASE / "dist"
DIST.mkdir(exist_ok=True, parents=True)

def monthly_summary(df):
    df["revenue"] = df["quantity"] * df["price"]
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()
    m = df.groupby("month")["revenue"].sum().reset_index()
    return m

def simple_demand_forecast(df):
    # พยากรณ์จำนวน (qty) รายสินค้า แบบ moving average 3 เดือนล่าสุด
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()
    g = df.groupby(["product_id","month"])["quantity"].sum().reset_index()
    forecasts = []
    for pid, g1 in g.groupby("product_id"):
        g1 = g1.sort_values("month")
        if len(g1) >= 3:
            f = g1["quantity"].tail(3).mean()
        else:
            f = g1["quantity"].mean()
        next_month = (g1["month"].max() + pd.offsets.MonthBegin(1)).to_pydatetime().date().isoformat()
        forecasts.append({"product_id": pid, "forecast_month": next_month, "forecast_qty": float(round(f,2))})
    return forecasts

def rfm_segmentation(df, n_clusters=3):
    df["revenue"] = df["quantity"] * df["price"]
    df["date"] = pd.to_datetime(df["date"])
    last_date = df["date"].max()
    R = df.groupby("customer_id")["date"].max().apply(lambda d: (last_date - d).days)
    F = df.groupby("customer_id")["order_id"].nunique()
    M = df.groupby("customer_id")["revenue"].sum()
    rfm = pd.DataFrame({"R":R, "F":F, "M":M}).reset_index()

    scaler = MinMaxScaler()
    X = scaler.fit_transform(rfm[["R","F","M"]])
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    rfm["segment"] = kmeans.fit_predict(X)

    # สรุปแต่ละคลัสเตอร์
    segs = []
    for s, g in rfm.groupby("segment"):
        segs.append({
            "segment": int(s),
            "count_customers": int(len(g)),
            "avg_R_days": float(round(g["R"].mean(),2)),
            "avg_F_orders": float(round(g["F"].mean(),2)),
            "avg_M_revenue": float(round(g["M"].mean(),2)),
            "top_customers_by_M": list(g.sort_values("M", ascending=False)["customer_id"].head(5))
        })
    return rfm, segs

def run():
    df = pd.read_excel(DATA)
    msum = monthly_summary(df)
    forecasts = simple_demand_forecast(df)
    _, segments = rfm_segmentation(df)

    out = {
        "generated_from": "data/sales.xlsx",
        "monthly_sales": [
            {"month": d["month"].strftime("%Y-%m-01"), "revenue": float(round(d["revenue"],2))}
            for d in msum.to_dict(orient="records")
        ],
        "demand_forecast": forecasts,
        "rfm_segments": segments
    }
    (DIST/"sales_analysis.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[ok] dist/sales_analysis.json")

if __name__ == "__main__":
    run()
