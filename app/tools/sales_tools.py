import pandas as pd


def load_sales_data(file_path: str) -> dict:
    df = pd.read_csv(file_path)

    return {
        "rows": len(df),
        "columns": df.columns.tolist(),
        "total_revenue": float(df["revenue"].sum()),
        "total_units": int(df["units"].sum()),
    }