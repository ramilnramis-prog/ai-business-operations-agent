from app.tools.reorder_tools import create_reorder_plan


def create_reorder_request(file_path: str) -> dict:
    items = create_reorder_plan(file_path)

    total_units = sum(
        item["recommended_order"]
        for item in items
    )

    return {
        "status": "draft",
        "request_type": "inventory_reorder",
        "items": items,
        "total_products": len(items),
        "total_units": total_units,
    }