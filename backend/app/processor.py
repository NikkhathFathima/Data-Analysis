import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from .database import ProcessedData, SalesData

# Flexible column mapping: maps common alternative names -> standard names
COLUMN_MAP = {
    # Order ID
    "orderid": "Order ID", "order_id": "Order ID", "order id": "Order ID",
    "id": "Order ID", "order no": "Order ID", "ordernumber": "Order ID",
    # Order Date
    "date": "Order Date", "order date": "Order Date", "orderdate": "Order Date",
    "purchase date": "Order Date", "transaction date": "Order Date",
    # Ship Date
    "ship date": "Ship Date", "shipdate": "Ship Date", "shipped date": "Ship Date",
    "delivery date": "Ship Date",
    # Customer
    "customerid": "Customer Name", "customer id": "Customer Name",
    "customer name": "Customer Name", "customername": "Customer Name",
    "customer": "Customer Name",
    # Segment
    "segment": "Segment", "customer segment": "Segment", "customersegment": "Segment",
    "paymentmethod": "Segment", "payment method": "Segment",
    # Region
    "region": "Region", "shippingaddress": "Region", "shipping address": "Region",
    "state": "Region", "city": "Region", "location": "Region", "country": "Region",
    # Category
    "category": "Category", "product category": "Category",
    "referralsource": "Category", "referral source": "Category",
    "orderstatus": "Category", "order status": "Category",
    # Sub-Category
    "sub-category": "Sub-Category", "subcategory": "Sub-Category",
    "sub category": "Sub-Category", "couponcode": "Sub-Category",
    "coupon code": "Sub-Category", "trackingnumber": "Sub-Category",
    "tracking number": "Sub-Category",
    # Product Name
    "product": "Product Name", "product name": "Product Name",
    "productname": "Product Name", "item": "Product Name", "sku": "Product Name",
    "itemsincart": "Product Name", "items in cart": "Product Name",
    # Sales
    "sales": "Sales", "totalprice": "Sales", "total price": "Sales",
    "total": "Sales", "revenue": "Sales", "amount": "Sales",
    "total amount": "Sales", "sale amount": "Sales",
    # Quantity
    "quantity": "Quantity", "qty": "Quantity", "units": "Quantity",
    "count": "Quantity",
    # Discount
    "discount": "Discount", "discount amount": "Discount", "disc": "Discount",
    # Profit
    "profit": "Profit", "net profit": "Profit", "gross profit": "Profit",
    "margin": "Profit",
    # Unit Price (used to derive profit if missing)
    "unitprice": "Unit Price", "unit price": "Unit Price", "price": "Unit Price",
    "unit cost": "Unit Price",
}

REQUIRED = {"Order ID", "Order Date", "Product Name", "Sales", "Quantity"}


def _normalize(col: str) -> str:
    return col.strip().lower()


def auto_map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remap any column names to standard names using COLUMN_MAP."""
    rename = {}
    for col in df.columns:
        mapped = COLUMN_MAP.get(_normalize(col))
        if mapped and mapped not in rename.values():
            rename[col] = mapped
    df = df.rename(columns=rename)
    return df


def validate_schema(df: pd.DataFrame) -> list:
    df = auto_map_columns(df)
    missing = REQUIRED - set(df.columns)
    return list(missing)


def clean_and_process(df: pd.DataFrame) -> pd.DataFrame:
    df = auto_map_columns(df)
    df.drop_duplicates(inplace=True)

    # Fill missing standard columns with sensible defaults
    defaults = {
        "Ship Date": None, "Customer Name": "Unknown", "Segment": "General",
        "Region": "Unknown", "Category": "General", "Sub-Category": "General",
        "Discount": 0.0, "Profit": None
    }
    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default

    # Parse dates
    df["Order Date"] = pd.to_datetime(df["Order Date"], infer_datetime_format=True, errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], infer_datetime_format=True, errors="coerce")
    if df["Ship Date"].isna().all():
        df["Ship Date"] = df["Order Date"]

    # Numeric coercion
    for col in ["Sales", "Quantity", "Discount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Derive Profit from Unit Price if missing
    if "Profit" not in df.columns or df["Profit"].isna().all():
        if "Unit Price" in df.columns:
            df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce").fillna(0)
            cost_ratio = 0.65
            df["Profit"] = (df["Sales"] - df["Unit Price"] * df["Quantity"] * cost_ratio).round(2)
        else:
            df["Profit"] = (df["Sales"] * 0.25).round(2)  # assume 25% margin
    else:
        df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce").fillna(0)

    # Derived columns
    df["Profit %"] = np.where(df["Sales"] != 0,
                              (df["Profit"] / df["Sales"]) * 100, 0).round(2)
    df["Month-Year"] = df["Order Date"].dt.to_period("M").astype(str)

    # Ensure Order ID is string
    df["Order ID"] = df["Order ID"].astype(str)
    df["Product Name"] = df["Product Name"].astype(str)
    df["Customer Name"] = df["Customer Name"].astype(str)
    df["Region"] = df["Region"].astype(str)
    df["Category"] = df["Category"].astype(str)
    df["Sub-Category"] = df["Sub-Category"].astype(str)
    df["Segment"] = df["Segment"].astype(str)

    # Drop rows where Sales or Order Date is null
    df = df[df["Sales"].notna() & df["Order Date"].notna()]
    df = df.reset_index(drop=True)
    return df


def save_to_db(df: pd.DataFrame, dataset_id: int, db: Session):
    records = []
    for _, row in df.iterrows():
        records.append(ProcessedData(
            dataset_id=dataset_id,
            order_id=str(row.get("Order ID", "")),
            order_date=row.get("Order Date"),
            ship_date=row.get("Ship Date"),
            customer_name=str(row.get("Customer Name", "")),
            segment=str(row.get("Segment", "")),
            region=str(row.get("Region", "")),
            category=str(row.get("Category", "")),
            sub_category=str(row.get("Sub-Category", "")),
            product_name=str(row.get("Product Name", "")),
            sales=float(row.get("Sales", 0)),
            quantity=int(row.get("Quantity", 0)),
            discount=float(row.get("Discount", 0)),
            profit=float(row.get("Profit", 0)),
            profit_pct=float(row.get("Profit %", 0)),
            month_year=str(row.get("Month-Year", "")),
        ))
    db.bulk_save_objects(records)
    db.commit()
