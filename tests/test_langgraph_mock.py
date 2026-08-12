import shutil
from pathlib import Path
from types import SimpleNamespace

import app.agent.graph as graph_module


SOURCE_FILE = Path("data/business_data.xlsx")


def test_langgraph_tool_call_without_openai(
    monkeypatch,
):
    thread_id = "pytest-langgraph-tool"
    upload_dir = Path("data/uploads") / thread_id

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy(
        SOURCE_FILE,
        upload_dir / "business_data.xlsx",
    )

    responses = [
        SimpleNamespace(
            id="response-1",
            output_text="",
            output=[
                SimpleNamespace(
                    type="function_call",
                    name="check_inventory",
                    call_id="call-1",
                    arguments="{}",
                )
            ],
        ),
        SimpleNamespace(
            id="response-2",
            output_text="Inventory checked successfully.",
            output=[],
        ),
    ]

    call_count = 0

    def fake_create(**kwargs):
        nonlocal call_count

        response = responses[call_count]
        call_count += 1

        return response

    monkeypatch.setattr(
        graph_module.client.responses,
        "create",
        fake_create,
    )

    try:
        result = graph_module.run_agent_with_status(
            "Какие товары нужно пополнить?",
            thread_id=thread_id,
        )

        assert call_count == 2
        assert result["status"] == "completed"
        assert (
            result["answer"]
            == "Inventory checked successfully."
        )

    finally:
        shutil.rmtree(
            upload_dir,
            ignore_errors=True,
        )