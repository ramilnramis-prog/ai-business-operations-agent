import os
import uuid

os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"

import requests
import streamlit as st


BACKEND_URL = "http://127.0.0.1:8000/api/v1"


st.set_page_config(
    page_title="AI Business Operations Agent",
    page_icon="🤖",
)

st.title("AI Business Operations Agent")

st.subheader("Business Data")

business_file = st.file_uploader(
    "Business Excel",
    type=["xlsx"],
    key="business_file",
)

if st.button("Upload Data"):
    if business_file is None:
        st.warning("Upload business_data.xlsx first.")
    else:
        new_thread_id = str(uuid.uuid4())
        st.session_state.thread_id = new_thread_id
        st.session_state.history = []
        st.session_state.pending_approval = None
        st.session_state.files_uploaded = False

        files = {
            "business_file": (
                business_file.name,
                business_file.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
        }

        response = requests.post(
            f"{BACKEND_URL}/files/upload",
            data={
                "thread_id": new_thread_id,
            },
            files=files,
            timeout=120,
        )

        if response.status_code == 200:
            st.session_state.thread_id = new_thread_id
            st.session_state.history = []
            st.session_state.pending_approval = None
            st.session_state.files_uploaded = True

            st.success("Data uploaded successfully.")
        else:
            try:
                error_data = response.json()
                detail = error_data.get("detail", {})

                if isinstance(detail, dict):
                    message = detail.get(
                        "message",
                        "Upload failed.",
                    )

                    errors = detail.get(
                        "errors",
                        [],
                    )

                    error_text = "\n".join(
                        f"- {error}"
                        for error in errors
                    )

                    if error_text:
                        st.error(
                            f"{message}\n\n{error_text}"
                        )
                    else:
                        st.error(message)

                else:
                    st.error(str(detail))

            except ValueError:
                st.error(
                    f"Upload error: "
                    f"{response.status_code}"
                )

if "history" not in st.session_state:
    st.session_state.history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None

if "files_uploaded" not in st.session_state:
    st.session_state.files_uploaded = False


for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.write(message["content"])


if st.session_state.pending_approval:
    request = st.session_state.pending_approval

    st.subheader("Заявка ожидает подтверждения")

    for item in request["items"]:
        st.write(
            f'{item["product"]}: '
            f'{item["recommended_order"]} шт.'
        )

    st.write(
        f'Итого: {request["total_units"]} шт.'
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Approve"):
            response = requests.post(
                f"{BACKEND_URL}/agent/approval",
                json={
                    "thread_id": st.session_state.thread_id,
                    "decision": "approved",
                },
                timeout=120,
            )

            if response.status_code == 200:
                answer = response.json()["answer"]

                st.session_state.history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                st.session_state.pending_approval = None
                st.rerun()

    with col2:
        if st.button("Reject"):
            response = requests.post(
                f"{BACKEND_URL}/agent/approval",
                json={
                    "thread_id": st.session_state.thread_id,
                    "decision": "rejected",
                },
                timeout=120,
            )

            if response.status_code == 200:
                answer = response.json()["answer"]

                st.session_state.history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                st.session_state.pending_approval = None
                st.rerun()


user_request = st.chat_input(
    "Напишите задачу...",
    disabled=st.session_state.pending_approval is not None,
)


if user_request:
    history_for_backend = list(st.session_state.history)

    st.session_state.history.append(
        {
            "role": "user",
            "content": user_request,
        }
    )

    with st.chat_message("user"):
        st.write(user_request)

    response = requests.post(
        f"{BACKEND_URL}/agent/run",
        json={
            "request": user_request,
            "history": history_for_backend,
            "thread_id": st.session_state.thread_id,
        },
        timeout=120,
    )

    if response.status_code == 200:
        data = response.json()

        if data["status"] == "pending_approval":
            st.session_state.pending_approval = (
                data["approval_request"]
            )

            st.rerun()

        else:
            answer = data["answer"]

            st.session_state.history.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

            st.rerun()

    else:
        st.error(
            f"Backend error: {response.status_code}"
        )