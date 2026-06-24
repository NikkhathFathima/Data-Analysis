"""Generate a realistic Superstore sample dataset"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random, os

random.seed(42)
np.random.seed(42)

regions = ["West", "East", "Central", "South"]
categories = {
    "Technology": ["Phones", "Computers", "Accessories", "Copiers"],
    "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
    "Office Supplies": ["Binders", "Paper", "Storage", "Art", "Labels"]
}
products = {
    "Phones": ["Apple iPhone 14", "Samsung Galaxy S23", "Motorola Edge"],
    "Computers": ["Dell Inspiron 15", "HP EliteBook", "Lenovo ThinkPad"],
    "Accessories": ["Logitech MX Keys", "Anker USB-C Hub", "Belkin Charger"],
    "Copiers": ["Canon ImageCLASS", "HP LaserJet Pro", "Brother HL-L2350DW"],
    "Chairs": ["HON 5700 Chair", "Steelcase Leap", "IKEA Markus"],
    "Tables": ["Safco Writing Desk", "Lorell Mahogany", "Bush Furniture"],
    "Bookcases": ["Sauder Bookcase", "Bush Barrister", "IKEA Billy"],
    "Furnishings": ["Deflecto Docuholder", "Eldon Wave Desk", "Rogers Easel"],
    "Binders": ["Avery Heavy Duty", "Cardinal Showcase", "Fellowes Binder"],
    "Paper": ["Hammermill Copy Paper", "Xerox 4200", "Georgia-Pacific"],
    "Storage": ["Fellowes Bankers Box", "Storex Dura", "Iris Weathertight"],
    "Art": ["Sanford Pencils", "Faber-Castell", "Dixon Ticonderoga"],
    "Labels": ["Avery Address Labels", "Maco Labels", "Pres-a-ply Labels"]
}
segments = ["Consumer", "Corporate", "Home Office"]
customers = [f"Customer_{i:04d}" for i in range(1, 201)]

rows = []
start_date = datetime(2020, 1, 1)
for i in range(2000):
    order_date = start_date + timedelta(days=random.randint(0, 1460))
    ship_date = order_date + timedelta(days=random.randint(1, 7))
    region = random.choice(regions)
    category = random.choice(list(categories.keys()))
    sub_cat = random.choice(categories[category])
    product = random.choice(products[sub_cat])
    quantity = random.randint(1, 10)
    base_price = {"Technology": 400, "Furniture": 250, "Office Supplies": 40}[category]
    sales = round(base_price * quantity * (0.5 + random.random()), 2)
    discount = round(random.choice([0, 0, 0, 0.1, 0.2, 0.3, 0.4, 0.5]), 2)
    cost_ratio = {"Technology": 0.65, "Furniture": 0.72, "Office Supplies": 0.55}[category]
    profit = round(sales * (1 - cost_ratio) - sales * discount * 0.8, 2)
    rows.append({
        "Row ID": i + 1,
        "Order ID": f"CA-{order_date.year}-{random.randint(100000,999999)}",
        "Order Date": order_date.strftime("%m/%d/%Y"),
        "Ship Date": ship_date.strftime("%m/%d/%Y"),
        "Ship Mode": random.choice(["Standard Class", "Second Class", "First Class", "Same Day"]),
        "Customer ID": f"CG-{random.randint(10000,99999)}",
        "Customer Name": random.choice(customers),
        "Segment": random.choice(segments),
        "Country": "United States",
        "City": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Seattle"]),
        "State": random.choice(["California", "New York", "Texas", "Florida", "Washington"]),
        "Postal Code": str(random.randint(10000, 99999)),
        "Region": region,
        "Product ID": f"TEC-{random.randint(1000,9999)}",
        "Category": category,
        "Sub-Category": sub_cat,
        "Product Name": product,
        "Sales": sales,
        "Quantity": quantity,
        "Discount": discount,
        "Profit": profit
    })

df = pd.DataFrame(rows)
out_path = os.path.join(os.path.dirname(__file__), "..", "sample_superstore.csv")
df.to_csv(out_path, index=False)
print(f"Generated {len(df)} rows -> sample_superstore.csv")
