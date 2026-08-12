from app.data_loader import load_sales_sheet


def analyze_sales_by_product(file_path: str) -> list[dict]:
    df = load_sales_sheet(file_path)

    result = (
        df.groupby("product")
        .agg(
            total_units=("units", "sum"),
            total_revenue=("revenue", "sum"),
        )
        .reset_index()
        .sort_values(
            "total_revenue",
            ascending=False,
        )
    )

    return result.to_dict(
        orient="records",
    )