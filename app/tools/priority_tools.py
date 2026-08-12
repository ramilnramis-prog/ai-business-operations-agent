from app.tools.business_tools import analyze_business_overview


def prioritize_products(
    file_path: str,
) -> list[dict]:
    overview = analyze_business_overview(file_path)

    total_revenue = sum(
        item["total_revenue"]
        for item in overview
    )

    result = []

    for item in overview:
        revenue_share = (
            item["total_revenue"] / total_revenue
            if total_revenue > 0
            else 0
        )

        reorder_level = item["reorder_level"]
        stock_deficit = max(
            reorder_level - item["total_stock"],
            0,
        )

        shortage_ratio = (
            stock_deficit / reorder_level
            if reorder_level > 0
            else 0
        )

        priority_score = round(
            (
                revenue_share * 0.6
                + shortage_ratio * 0.4
            )
            * 100,
            1,
        )

        if priority_score >= 50:
            priority = "high"
        elif priority_score >= 25:
            priority = "medium"
        else:
            priority = "low"

        result.append(
            {
                **item,
                "stock_deficit": stock_deficit,
                "revenue_share": round(
                    revenue_share * 100,
                    1,
                ),
                "shortage_ratio": round(
                    shortage_ratio * 100,
                    1,
                ),
                "priority_score": priority_score,
                "priority": priority,
            }
        )

    return sorted(
        result,
        key=lambda item: item["priority_score"],
        reverse=True,
    )