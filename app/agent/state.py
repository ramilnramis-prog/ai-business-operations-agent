from typing import Any
from typing_extensions import TypedDict


class AgentState(TypedDict):
    messages: list[Any]
    tool_calls: list[Any]
    final_answer: str
    pending_approval: bool
    approval_request: dict | None
    approval_decision: str | None
    previous_response_id: str | None
    tool_outputs: list[dict]
    business_file_path: str | None