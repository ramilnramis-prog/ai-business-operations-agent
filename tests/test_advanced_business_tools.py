from app.tools.priority_tools import prioritize_products
from app.tools.financial_tools import calculate_revenue_exposure
from app.tools.anomaly_tools import detect_sales_anomalies


BUSINESS_FILE = "data/business_data.xlsx"
ANOMALY_FILE = "tests/fixtures/business_data_anomaly.xlsx"


def test_prioritize_products():
    result = prioritize_products(BUSINESS_FILE)

    assert len(result) == 3

    assert result[0]["product"] == "Product A"
    assert result[0]["priority_score"] == 61.1
    assert result[0]["priority"] == "high"

    assert result[1]["product"] == "Product C"
    assert result[1]["priority"] == "medium"

    assert result[2]["product"] == "Product B"
    assert result[2]["priority"] == "low"


def test_calculate_revenue_exposure():
    result = calculate_revenue_exposure(BUSINESS_FILE)

    assert result["total_revenue"] == 47500
    assert (
        result["revenue_from_products_needing_reorder"]
        == 37500
    )
    assert result["revenue_exposure_share"] == 78.9

    products = {
        item["product"]
        for item in result["affected_products"]
    }

    assert products == {"Product A", "Product C"}


def test_detect_sales_anomalies():
    result = detect_sales_anomalies(ANOMALY_FILE)

    assert len(result) == 3

    anomalies = {
        (item["product"], item["date"]): item
        for item in result
    }

    assert anomalies[
        ("Product B", "2026-08-22")
    ]["direction"] == "spike"

    assert anomalies[
        ("Product A", "2026-08-18")
    ]["direction"] == "drop"

    assert anomalies[
        ("Product C", "2026-08-25")
    ]["direction"] == "drop"