import pytest

from app.data_loader import validate_business_file
from app.agent.tool_registry import execute_tool


BUSINESS_FILE = "data/business_data.xlsx"
INVALID_FILE = "tests/fixtures/business_data_invalid.xlsx"


def test_valid_business_file():
    result = validate_business_file(BUSINESS_FILE)

    assert result["valid"] is True
    assert result["errors"] == []


def test_invalid_business_file_missing_inventory():
    result = validate_business_file(INVALID_FILE)

    assert result["valid"] is False
    assert "Missing sheet: Inventory" in result["errors"]


def test_tool_requires_uploaded_business_file():
    with pytest.raises(
        ValueError,
        match="Business data file is not uploaded",
    ):
        execute_tool("check_inventory")