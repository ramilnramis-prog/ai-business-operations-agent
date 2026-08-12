from pathlib import Path
import json
import os
from typing import Literal

from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from openai import OpenAI

from app.agent.state import AgentState
from app.agent.tool_registry import TOOL_DEFINITIONS, execute_tool


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL")
AGENT_INSTRUCTIONS = """
You are an AI Business Operations Agent.

Rules:
1. Use the available tools whenever the user's question depends on sales
   or inventory data.
2. Never invent products, revenue, stock levels, quantities, or other
   business data.
3. If the user's request is unclear, ask one short clarifying question.
4. If the requested task is outside the capabilities of the available
   tools, clearly explain what you can currently do.
5. Do not create generic applications, orders, emails, or documents unless
   the agent has a dedicated tool for that task.
6. Answer in the same language as the user.
7. If a tool returns an error, do not invent additional requirements,
   formats, columns, or capabilities. Briefly explain the error and
   tell the user the next required action.
8. If the business data file is missing, tell the user to upload
   business_data.xlsx. Do not suggest CSV or other file formats.
9. Clearly distinguish facts from recommendations.
   Facts must be supported by tool output.
10. Do not claim customer loss, future demand, stockout timing,
   supplier lead times, promotions, or other business conditions
   unless those facts are present in tool results.
11. You may give recommendations based on the available data,
   but clearly present them as recommendations rather than facts.
12. Never claim that you can perform an action unless there is an
    available tool that actually supports that action.

13. Do not claim that existing tools support filters, date-level
    analysis, returns, cancellations, promotions, listing status,
    supplier data, or order logs unless those capabilities are
    explicitly available in the tool definitions.

14. When explaining anomaly detection results, do not invent a
    statistical threshold. Describe the detected events using the
    z-scores returned by the tool. If the threshold is not present
    in the tool output, do not state a threshold value.

15. Possible causes of anomalies may be mentioned only as hypotheses.
    Clearly state that the available data does not establish the cause.
"""

def llm_node(state: AgentState):
    print("\nNODE: LLM")

    request_kwargs = {
        "model": model,
        "instructions": AGENT_INSTRUCTIONS,
        "tools": TOOL_DEFINITIONS,
        "parallel_tool_calls": False,
    }

    if state.get("previous_response_id"):
        request_kwargs["previous_response_id"] = state["previous_response_id"]
        request_kwargs["input"] = state.get("tool_outputs", [])
    else:
        request_kwargs["input"] = state["messages"]

    response = client.responses.create(
        **request_kwargs
    )

    tool_calls = [
        {
            "name": item.name,
            "call_id": item.call_id,
            "arguments": item.arguments,
        }
        for item in response.output
        if item.type == "function_call"
    ]

    return {
        "tool_calls": tool_calls,
        "final_answer": response.output_text,
        "previous_response_id": response.id,
        "tool_outputs": [],
    }

def tool_node(state: AgentState):
    print("NODE: TOOLS")

    tool_outputs = []

    pending_approval = state.get(
        "pending_approval",
        False,
    )

    approval_request = state.get(
        "approval_request"
    )

    for item in state["tool_calls"]:
        print("Tool:", item["name"])

        try:
            result = execute_tool(
                item["name"],
                business_file_path=state.get("business_file_path"),
            )
        except Exception as exc:
            result = {
                "error": str(exc),
                "tool": item["name"],
            }

        print("Result:", result)

        if (
            item["name"] == "create_reorder_request"
            and "error" not in result
        ):
            pending_approval = True
            approval_request = result

            print(
                "APPROVAL: human confirmation required"
            )
        tool_outputs.append(
            {
                "type": "function_call_output",
                "call_id": item["call_id"],
                "output": json.dumps(
                    result,
                    ensure_ascii=False,
                ),
            }
        )

    return {
        "tool_calls": [],
        "tool_outputs": tool_outputs,
        "pending_approval": pending_approval,
        "approval_request": approval_request,
    }

def approval_node(state: AgentState):
    print("NODE: APPROVAL")

    decision = interrupt(
        {
            "message": "Подтвердить заявку на пополнение?",
            "request": state["approval_request"],
        }
    )

    print("APPROVAL DECISION:", decision)

    return {
        "pending_approval": False,
        "approval_decision": decision,
    }


def route_after_tools(
    state: AgentState,
) -> Literal["approval", "llm"]:

    if state.get("pending_approval"):
        print("ROUTER: требуется Approval")
        return "approval"

    return "llm"

def route_after_llm(
    state: AgentState,
) -> Literal["tools", "__end__"]:

    if state["tool_calls"]:
        print("ROUTER: идем в Tools")
        return "tools"

    print("ROUTER: задача закончена")
    return END


builder = StateGraph(AgentState)

builder.add_node("llm", llm_node)
builder.add_node("tools", tool_node)
builder.add_node("approval", approval_node)

builder.add_edge(START, "llm")

builder.add_conditional_edges(
    "llm",
    route_after_llm,
)

builder.add_conditional_edges(
    "tools",
    route_after_tools,
)

builder.add_edge("approval", END)

memory = InMemorySaver()

graph = builder.compile(
    checkpointer=memory,
)


def run_agent(
    user_request: str,
    history: list[dict] | None = None,
    thread_id: str = "default",
) -> str:

    messages = list(history or [])

    messages.append(
        {
            "role": "user",
            "content": user_request,
        }
    )

    initial_state: AgentState = {
        "messages": messages,
        "tool_calls": [],
        "final_answer": "",
    }

    config = {
    "configurable": {
        "thread_id": thread_id,
    }
}

    result = graph.invoke(
    initial_state,
    config=config,
)

    return result["final_answer"]
def run_agent_with_status(
    user_request: str,
    history: list[dict] | None = None,
    thread_id: str = "default",
) -> dict:

    messages = list(history or [])

    messages.append(
        {
            "role": "user",
            "content": user_request,
        }
    )

    upload_dir = Path("data/uploads") / thread_id

    business_path = upload_dir / "business_data.xlsx"

    business_file_path = (
        str(business_path)
        if business_path.exists()
        else None
    )

    initial_state: AgentState = {
        "messages": messages,
        "tool_calls": [],
        "final_answer": "",
        "pending_approval": False,
        "approval_request": None,
        "approval_decision": None,
        "previous_response_id": None,
        "tool_outputs": [],
        "business_file_path": business_file_path,
    }

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    result = graph.invoke(
        initial_state,
        config=config,
    )

    if "__interrupt__" in result:
        interrupt_data = result["__interrupt__"][0].value

        return {
            "status": "pending_approval",
            "answer": "",
            "approval_request": interrupt_data["request"],
        }

    return {
        "status": "completed",
        "answer": result.get("final_answer", ""),
        "approval_request": None,
    }


def resume_agent(
    thread_id: str,
    decision: str,
) -> dict:

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    result = graph.invoke(
        Command(resume=decision),
        config=config,
    )

    if decision == "approved":
        answer = "Заявка подтверждена."
    else:
        answer = "Заявка отклонена."

    return {
        "status": "completed",
        "answer": answer,
        "approval_decision": result.get(
            "approval_decision"
        ),
    }