from app.data_loader import load_inventory_sheet


def check_inventory(file_path: str) -> list[dict]:
    df = load_inventory_sheet(file_path)

    result = (
        df.groupby("product")
        .agg(
            total_stock=("stock", "sum"),
            total_reorder_level=("reorder_level", "sum"),
        )
        .reset_index()
    )

    result["needs_reorder"] = (
        result["total_stock"]
        < result["total_reorder_level"]
    )

    return result.to_dict(
        orient="records",
    )