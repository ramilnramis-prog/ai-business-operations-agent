from app.tools.business_tools import analyze_business_overview


def calculate_revenue_exposure(
    file_path: str,
) -> dict:
    overview = analyze_business_overview(file_path)

    total_revenue = sum(
        item["total_revenue"]
        for item in overview
    )

    affected_products = [
        item
        for item in overview
        if item["needs_reorder"]
    ]

    exposed_revenue = sum(
        item["total_revenue"]
        for item in affected_products
    )

    exposure_share = (
        exposed_revenue / total_revenue
        if total_revenue > 0
        else 0
    )

    return {
        "total_revenue": total_revenue,
        "revenue_from_products_needing_reorder": exposed_revenue,
        "revenue_exposure_share": round(
            exposure_share * 100,
            1,
        ),
        "affected_products": [
            {
                "product": item["product"],
                "total_revenue": item["total_revenue"],
                "total_stock": item["total_stock"],
                "reorder_level": item["reorder_level"],
            }
            for item in affected_products
        ],
    }