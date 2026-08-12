import shutil
from pathlib import Path
from types import SimpleNamespace

import app.agent.graph as graph_module


SOURCE_FILE = Path("data/business_data.xlsx")


def test_reorder_request_requires_approval(
    monkeypatch,
):
    thread_id = "pytest-hitl-approved"
    upload_dir = Path("data/uploads") / thread_id

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy(
        SOURCE_FILE,
        upload_dir / "business_data.xlsx",
    )

    fake_response = SimpleNamespace(
        id="response-hitl-1",
        output_text="",
        output=[
            SimpleNamespace(
                type="function_call",
                name="create_reorder_request",
                call_id="call-hitl-1",
                arguments="{}",
            )
        ],
    )

    def fake_create(**kwargs):
        return fake_response

    monkeypatch.setattr(
        graph_module.client.responses,
        "create",
        fake_create,
    )

    try:
        result = graph_module.run_agent_with_status(
            "Сделай заявку на пополнение склада",
            thread_id=thread_id,
        )

        assert result["status"] == "pending_approval"

        request = result["approval_request"]

        assert request["status"] == "draft"
        assert request["total_products"] == 2
        assert request["total_units"] == 18

        resumed = graph_module.resume_agent(
            thread_id,
            "approved",
        )

        assert resumed["status"] == "completed"
        assert (
            resumed["approval_decision"]
            == "approved"
        )
        assert (
            resumed["answer"]
            == "Заявка подтверждена."
        )

    finally:
        shutil.rmtree(
            upload_dir,
            ignore_errors=True,
        )


def test_reorder_request_can_be_rejected(
    monkeypatch,
):
    thread_id = "pytest-hitl-rejected"
    upload_dir = Path("data/uploads") / thread_id

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy(
        SOURCE_FILE,
        upload_dir / "business_data.xlsx",
    )

    fake_response = SimpleNamespace(
        id="response-hitl-2",
        output_text="",
        output=[
            SimpleNamespace(
                type="function_call",
                name="create_reorder_request",
                call_id="call-hitl-2",
                arguments="{}",
            )
        ],
    )

    def fake_create(**kwargs):
        return fake_response

    monkeypatch.setattr(
        graph_module.client.responses,
        "create",
        fake_create,
    )

    try:
        result = graph_module.run_agent_with_status(
            "Сделай заявку на пополнение склада",
            thread_id=thread_id,
        )

        assert result["status"] == "pending_approval"

        resumed = graph_module.resume_agent(
            thread_id,
            "rejected",
        )

        assert resumed["status"] == "completed"
        assert (
            resumed["approval_decision"]
            == "rejected"
        )
        assert (
            resumed["answer"]
            == "Заявка отклонена."
        )

    finally:
        shutil.rmtree(
            upload_dir,
            ignore_errors=True,
        )