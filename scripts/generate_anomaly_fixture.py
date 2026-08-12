import pandas as pd


products = {
    "Product A": {
        "category": "Kitchen",
        "price": 1500,
        "units": [10, 9, 11, 10, 8, 12, 9, 10, 11, 9,
                  10, 8, 11, 10, 9, 12, 10, 1, 9, 11,
                  10, 8, 12, 9, 10, 11, 9, 10, 8, 11],
    },
    "Product B": {
        "category": "Tools",
        "price": 2000,
        "units": [5, 4, 6, 5, 5, 4, 6, 5, 4, 5,
                  6, 5, 4, 5, 6, 4, 5, 6, 5, 4,
                  5, 15, 5, 4, 6, 5, 4, 5, 6, 5],
    },
    "Product C": {
        "category": "Garden",
        "price": 3000,
        "units": [4, 3, 5, 4, 4, 3, 5, 4, 3, 4,
                  5, 4, 3, 4, 5, 3, 4, 5, 4, 3,
                  4, 5, 3, 4, 0, 4, 5, 3, 4, 5],
    },
}


rows = []

dates = pd.date_range(
    start="2026-08-01",
    periods=30,
    freq="D",
)

for product, data in products.items():
    for date, units in zip(dates, data["units"]):
        rows.append(
            {
                "date": date,
                "product": product,
                "category": data["category"],
                "units": units,
                "revenue": units * data["price"],
                "price": data["price"],
            }
        )

sales = pd.DataFrame(rows)

inventory = pd.read_excel(
    "data/business_data.xlsx",
    sheet_name="Inventory",
)

with pd.ExcelWriter(
    "tests/fixtures/business_data_anomaly.xlsx",
    engine="openpyxl",
) as writer:
    sales.to_excel(
        writer,
        sheet_name="Sales",
        index=False,
    )

    inventory.to_excel(
        writer,
        sheet_name="Inventory",
        index=False,
    )

print("Created business_data_anomaly.xlsx")
print("Sales rows:", len(sales))
print("Date range:", sales["date"].min(), "->", sales["date"].max())