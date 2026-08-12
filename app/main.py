from typing import Literal

from pathlib import Path
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field

from app.agent.graph import (
    resume_agent,
    run_agent_with_status,
)

from app.data_loader import validate_business_file

app = FastAPI(
    title="AI Business Operations Agent"
)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AgentRequest(BaseModel):
    request: str
    history: list[ChatMessage] = Field(default_factory=list)
    thread_id: str = "default"


class AgentResponse(BaseModel):
    status: Literal["completed", "pending_approval"]
    answer: str
    approval_request: dict | None = None
    thread_id: str


class ApprovalRequest(BaseModel):
    thread_id: str
    decision: Literal["approved", "rejected"]


class ApprovalResponse(BaseModel):
    status: str
    answer: str
    approval_decision: str | None = None
    thread_id: str


@app.get("/api/v1/health")
def health():
    return {
        "status": "ok",
        "service": "AI Business Operations Agent",
    }


@app.post(
    "/api/v1/agent/run",
    response_model=AgentResponse,
)
def run_agent_endpoint(payload: AgentRequest):
    history = [
        message.model_dump()
        for message in payload.history
    ]

    result = run_agent_with_status(
        payload.request,
        history=history,
        thread_id=payload.thread_id,
    )

    return AgentResponse(
        **result,
        thread_id=payload.thread_id,
    )


@app.post(
    "/api/v1/agent/approval",
    response_model=ApprovalResponse,
)
def approval_endpoint(payload: ApprovalRequest):
    result = resume_agent(
        thread_id=payload.thread_id,
        decision=payload.decision,
    )

    return ApprovalResponse(
        **result,
        thread_id=payload.thread_id,
    )

@app.post("/api/v1/files/upload")
async def upload_business_file(
    thread_id: str = Form(...),
    business_file: UploadFile = File(...),
):
    upload_dir = Path("data/uploads") / thread_id
    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    business_path = upload_dir / "business_data.xlsx"

    with business_path.open("wb") as buffer:
        shutil.copyfileobj(
            business_file.file,
            buffer,
        )
    validation = validate_business_file(
        str(business_path)
    )

    if not validation["valid"]:
        business_path.unlink(
            missing_ok=True,
        )

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid business data file.",
                "errors": validation["errors"],
            },
        )

    return {
        "status": "uploaded",
        "thread_id": thread_id,
        "business_file_path": str(business_path),
    }