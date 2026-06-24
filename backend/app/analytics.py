from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import ProcessedData
import numpy as np

def get_filtered_query(db: Session, dataset_id: int, region=None, category=None,
                       date_from=None, date_to=None):
    q = db.query(ProcessedData).filter(ProcessedData.dataset_id == dataset_id)
    if region:
        q = q.filter(ProcessedData.region == region)
    if category:
        q = q.filter(ProcessedData.category == category)
    if date_from:
        q = q.filter(ProcessedData.order_date >= date_from)
    if date_to:
        q = q.filter(ProcessedData.order_date <= date_to)
    return q

def compute_kpis(db: Session, dataset_id: int, **filters):
    q = get_filtered_query(db, dataset_id, **filters)
    rows = q.all()
    if not rows:
        return {}
    sales = [r.sales for r in rows]
    profits = [r.profit for r in rows]
    total_sales = sum(sales)
    total_profit = sum(profits)
    return {
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "profit_margin": round((total_profit / total_sales * 100) if total_sales else 0, 2),
        "total_orders": len(set(r.order_id for r in rows)),
        "avg_discount": round(sum(r.discount for r in rows) / len(rows) * 100, 2),
    }

def sales_trend(db: Session, dataset_id: int, **filters):
    q = get_filtered_query(db, dataset_id, **filters)
    rows = q.all()
    from collections import defaultdict
    trend = defaultdict(lambda: {"sales": 0, "profit": 0})
    for r in rows:
        trend[r.month_year]["sales"] += r.sales
        trend[r.month_year]["profit"] += r.profit
    return [{"month": k, "sales": round(v["sales"], 2), "profit": round(v["profit"], 2)}
            for k, v in sorted(trend.items())]

def region_sales(db: Session, dataset_id: int, **filters):
    q = get_filtered_query(db, dataset_id, **filters)
    rows = q.all()
    from collections import defaultdict
    data = defaultdict(lambda: {"sales": 0, "profit": 0})
    for r in rows:
        data[r.region]["sales"] += r.sales
        data[r.region]["profit"] += r.profit
    return [{"region": k, "sales": round(v["sales"], 2), "profit": round(v["profit"], 2)}
            for k, v in data.items()]

def category_performance(db: Session, dataset_id: int, **filters):
    q = get_filtered_query(db, dataset_id, **filters)
    rows = q.all()
    from collections import defaultdict
    data = defaultdict(lambda: {"sales": 0, "profit": 0, "count": 0})
    for r in rows:
        data[r.category]["sales"] += r.sales
        data[r.category]["profit"] += r.profit
        data[r.category]["count"] += 1
    result = []
    for k, v in data.items():
        margin = (v["profit"] / v["sales"] * 100) if v["sales"] else 0
        result.append({"category": k, "sales": round(v["sales"], 2),
                       "profit": round(v["profit"], 2), "margin": round(margin, 2)})
    return result

def top_products(db: Session, dataset_id: int, n=5, **filters):
    q = get_filtered_query(db, dataset_id, **filters)
    rows = q.all()
    from collections import defaultdict
    data = defaultdict(float)
    for r in rows:
        data[r.product_name] += r.sales
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    return [{"product": k, "sales": round(v, 2)} for k, v in sorted_items[:n]]

def worst_categories(db: Session, dataset_id: int, **filters):
    cats = category_performance(db, dataset_id, **filters)
    return sorted(cats, key=lambda x: x["profit"])[:3]

def generate_insights(db: Session, dataset_id: int, **filters):
    regions = region_sales(db, dataset_id, **filters)
    cats = category_performance(db, dataset_id, **filters)
    kpis = compute_kpis(db, dataset_id, **filters)
    insights = []
    if not regions or not kpis:
        return insights
    total_sales = kpis["total_sales"]
    # Region insight
    top_region = max(regions, key=lambda x: x["sales"])
    pct = round(top_region["sales"] / total_sales * 100, 1) if total_sales else 0
    insights.append(f"{top_region['region']} region contributes {pct}% of total sales.")
    # Category margin insight
    if cats:
        top_cat = max(cats, key=lambda x: x["margin"])
        insights.append(f"{top_cat['category']} category has the highest profit margin at {top_cat['margin']}%.")
        worst_cat = min(cats, key=lambda x: x["profit"])
        insights.append(f"{worst_cat['category']} category has the lowest profit at ${worst_cat['profit']:,.0f}.")
    # Profit margin insight
    if kpis["profit_margin"] < 10:
        insights.append(f"Overall profit margin is low at {kpis['profit_margin']}%. Consider reviewing discounts.")
    elif kpis["profit_margin"] > 20:
        insights.append(f"Strong overall profit margin of {kpis['profit_margin']}%.")
    # Discount insight
    if kpis["avg_discount"] > 20:
        insights.append(f"Average discount of {kpis['avg_discount']}% is high — this may be eroding margins.")
    return insights

def detect_anomalies(db: Session, dataset_id: int):
    rows = db.query(ProcessedData).filter(ProcessedData.dataset_id == dataset_id).all()
    if not rows:
        return []
    sales_vals = np.array([r.sales for r in rows])
    mean, std = sales_vals.mean(), sales_vals.std()
    threshold = mean + 2.5 * std
    anomalies = [
        {"order_id": r.order_id, "product": r.product_name,
         "sales": round(r.sales, 2), "date": str(r.order_date)[:10]}
        for r in rows if r.sales > threshold
    ]
    return anomalies[:20]

def forecast_sales(db: Session, dataset_id: int):
    from sklearn.linear_model import LinearRegression
    trend = sales_trend(db, dataset_id)
    if len(trend) < 3:
        return []
    X = np.arange(len(trend)).reshape(-1, 1)
    y = np.array([t["sales"] for t in trend])
    model = LinearRegression().fit(X, y)
    next_idx = np.array([[len(trend)], [len(trend) + 1], [len(trend) + 2]])
    predictions = model.predict(next_idx)
    from datetime import datetime
    try:
        last_period = trend[-1]["month"]
        last_date = datetime.strptime(last_period, "%Y-%m")
        forecast = []
        for i, pred in enumerate(predictions):
            month = last_date.month + i + 1
            year = last_date.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            forecast.append({"month": f"{year}-{month:02d}", "predicted_sales": round(max(pred, 0), 2)})
        return forecast
    except Exception:
        return [{"month": f"Month+{i+1}", "predicted_sales": round(max(p, 0), 2)}
                for i, p in enumerate(predictions)]
