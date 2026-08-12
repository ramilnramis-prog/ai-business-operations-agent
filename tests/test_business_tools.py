from app.tools.analysis_tools import analyze_sales_by_product
from app.tools.inventory_tools import check_inventory
from app.tools.reorder_tools import create_reorder_plan
from app.tools.order_tools import create_reorder_request


BUSINESS_FILE = "data/business_data.xlsx"


def test_analyze_sales_by_product():
    result = analyze_sales_by_product(BUSINESS_FILE)

    assert result[0]["product"] == "Product A"
    assert result[0]["total_units"] == 17
    assert result[0]["total_revenue"] == 25500


def test_check_inventory():
    result = check_inventory(BUSINESS_FILE)

    product_a = next(
        item for item in result
        if item["product"] == "Product A"
    )

    assert product_a["total_stock"] == 5
    assert product_a["total_reorder_level"] == 18
    assert product_a["needs_reorder"] is True


def test_create_reorder_plan():
    result = create_reorder_plan(BUSINESS_FILE)

    assert len(result) == 2

    product_a = next(
        item for item in result
        if item["product"] == "Product A"
    )

    assert product_a["recommended_order"] == 13


def test_create_reorder_request():
    result = create_reorder_request(BUSINESS_FILE)

    assert result["status"] == "draft"
    assert result["total_products"] == 2
    assert result["total_units"] == 18