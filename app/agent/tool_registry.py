from app.tools.anomaly_tools import detect_sales_anomalies
from app.tools.financial_tools import calculate_revenue_exposure
from app.tools.priority_tools import prioritize_products
from app.tools.business_tools import analyze_business_overview
from app.tools.analysis_tools import analyze_sales_by_product
from app.tools.inventory_tools import check_inventory
from app.tools.reorder_tools import create_reorder_plan
from app.tools.order_tools import create_reorder_request


TOOL_DEFINITIONS = [
{
    "type": "function",
    "name": "detect_sales_anomalies",
    "description": (
        "Detect unusual spikes or drops in daily product sales "
        "using statistical anomaly detection. Use this when the "
        "user asks about unusual sales, anomalies, sudden drops, "
        "unexpected spikes, or abnormal sales behavior."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },
    "strict": True,
},
{
    "type": "function",
    "name": "calculate_revenue_exposure",
    "description": (
        "Calculate what share of current revenue comes from products "
        "that currently need inventory replenishment. Use this for "
        "questions about revenue exposure, financial impact of low "
        "inventory, or how much revenue is associated with products "
        "that need reordering."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },
    "strict": True,
},
    {
        "type": "function",
        "name": "analyze_sales_by_product",
        "description": (
            "Analyze sales by product and return total units "
            "and total revenue for each product."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
{
    "type": "function",
    "name": "prioritize_products",
    "description": (
        "Calculate deterministic product priorities using sales revenue "
        "and inventory shortage. Use this when the user asks which "
        "products require attention first, what the priorities are, "
        "or asks to rank products by business priority."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },
    "strict": True,
},
    {
        "type": "function",
        "name": "check_inventory",
        "description": (
            "Check inventory levels for each product and determine "
            "whether each product needs reordering."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "create_reorder_plan",
        "description": (
             "Create a reorder plan for products that are below their "
             "reorder level. Returns current stock, target stock, and "
             "recommended order quantity for each product."
    ),
         "parameters": {
             "type": "object",
             "properties": {},
             "required": [],
             "additionalProperties": False,
          },
          "strict": True,
    },
{
    "type": "function",
    "name": "analyze_business_overview",
    "description": (
        "Analyze sales and inventory together for all products. "
        "Use this for overall business analysis, priorities, "
        "products that require attention, and combined sales "
        "and inventory questions."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },
    "strict": True,
},
{
         "type": "function",
         "name": "create_reorder_request",
         "description": (
             "Create a draft inventory reorder request. "
             "Use this when the user explicitly asks to prepare, create, "
             "or make a reorder request or order draft."
    ),
         "parameters": {
             "type": "object",
             "properties": {},
             "required": [],
             "additionalProperties": False,
    },
         "strict": True,
},
]


def execute_tool(
    tool_name: str,
    business_file_path: str | None = None,
):
    if business_file_path is None:
        raise ValueError(
            "Business data file is not uploaded."
        )

    file_path = business_file_path

    if tool_name == "calculate_revenue_exposure":
        return calculate_revenue_exposure(file_path)

    if tool_name == "prioritize_products":
        return prioritize_products(file_path)

    if tool_name == "analyze_business_overview":
        return analyze_business_overview(file_path)    

    if tool_name == "analyze_sales_by_product":
        return analyze_sales_by_product(file_path)

    if tool_name == "detect_sales_anomalies":
        return detect_sales_anomalies(file_path)

    if tool_name == "check_inventory":
        return check_inventory(file_path)

    if tool_name == "create_reorder_plan":
        return create_reorder_plan(file_path)

    if tool_name == "create_reorder_request":
        return create_reorder_request(file_path)

    raise ValueError(f"Unknown tool: {tool_name}")