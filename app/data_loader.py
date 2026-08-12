import pandas as pd


def load_sales_sheet(file_path: str) -> pd.DataFrame:
    return pd.read_excel(
        file_path,
        sheet_name="Sales",
    )


def load_inventory_sheet(file_path: str) -> pd.DataFrame:
    return pd.read_excel(
        file_path,
        sheet_name="Inventory",
    )

REQUIRED_COLUMNS = {
    "Sales": {
        "date",
        "product",
        "category",
        "units",
        "revenue",
        "price",
    },
    "Inventory": {
        "product",
        "warehouse",
        "stock",
        "reorder_level",
    },
}


def validate_business_file(file_path: str) -> dict:
    errors = []

    with pd.ExcelFile(file_path) as excel_file:
        for sheet_name, required_columns in REQUIRED_COLUMNS.items():
            if sheet_name not in excel_file.sheet_names:
                errors.append(
                    f"Missing sheet: {sheet_name}"
                )
                continue

            df = pd.read_excel(
                excel_file,
                sheet_name=sheet_name,
                nrows=0,
            )

            actual_columns = {
                str(column).strip()
                for column in df.columns
            }

            missing_columns = (
                required_columns - actual_columns
            )

            if missing_columns:
                errors.append(
                    f"{sheet_name}: missing columns: "
                    f"{', '.join(sorted(missing_columns))}"
                )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }