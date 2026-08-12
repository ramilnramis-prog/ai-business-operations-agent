from app.data_loader import load_sales_sheet


def detect_sales_anomalies(
    file_path: str,
    z_threshold: float = 2.5,
) -> list[dict]:
    df = load_sales_sheet(file_path).copy()

    df["date"] = df["date"].astype(str)

    anomalies = []

    for product, product_df in df.groupby("product"):
        mean_units = product_df["units"].mean()
        std_units = product_df["units"].std(ddof=0)

        if std_units == 0:
            continue

        product_df = product_df.copy()

        product_df["z_score"] = (
            product_df["units"] - mean_units
        ) / std_units

        abnormal_rows = product_df[
            product_df["z_score"].abs() >= z_threshold
        ]

        for _, row in abnormal_rows.iterrows():
            anomalies.append(
                {
                    "date": row["date"],
                    "product": product,
                    "units": int(row["units"]),
                    "average_units": round(
                        float(mean_units),
                        2,
                    ),
                    "z_score": round(
                        float(row["z_score"]),
                        2,
                    ),
                    "direction": (
                        "spike"
                        if row["z_score"] > 0
                        else "drop"
                    ),
                }
            )

    return sorted(
        anomalies,
        key=lambda item: abs(item["z_score"]),
        reverse=True,
    )