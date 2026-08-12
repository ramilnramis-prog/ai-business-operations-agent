from app.tools.inventory_tools import check_inventory


def create_reorder_plan(file_path: str) -> list[dict]:
    inventory = check_inventory(file_path)

    reorder_plan = []

    for item in inventory:
        if item["needs_reorder"]:
            recommended_order = (
                item["total_reorder_level"]
                - item["total_stock"]
            )

            reorder_plan.append(
                {
                    "product": item["product"],
                    "current_stock": item["total_stock"],
                    "target_stock": item["total_reorder_level"],
                    "recommended_order": recommended_order,
                }
            )

    return reorder_plan