from app.tools.analysis_tools import analyze_sales_by_product
from app.tools.inventory_tools import check_inventory


def analyze_business_overview(
    file_path: str,
) -> list[dict]:
    sales = analyze_sales_by_product(file_path)
    inventory = check_inventory(file_path)

    sales_by_product = {
        item["product"]: item
        for item in sales
    }

    inventory_by_product = {
        item["product"]: item
        for item in inventory
    }

    products = (
        set(sales_by_product)
        | set(inventory_by_product)
    )

    result = []

    for product in sorted(products):
        sales_item = sales_by_product.get(
            product,
            {},
        )

        inventory_item = inventory_by_product.get(
            product,
            {},
        )

        result.append(
            {
                "product": product,
                "total_units": sales_item.get(
                    "total_units",
                    0,
                ),
                "total_revenue": sales_item.get(
                    "total_revenue",
                    0,
                ),
                "total_stock": inventory_item.get(
                    "total_stock",
                    0,
                ),
                "reorder_level": inventory_item.get(
                    "total_reorder_level",
                    0,
                ),
                "needs_reorder": inventory_item.get(
                    "needs_reorder",
                    False,
                ),
            }
        )

    return result