import shutil
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

BUSINESS_FILE = Path("data/business_data.xlsx")
INVALID_FILE = Path("tests/fixtures/business_data_invalid.xlsx")

MIME_XLSX = (
    "application/vnd.openxmlformats-officedocument."
    "spreadsheetml.sheet"
)


def test_health_endpoint():
    response = client.get("/api/v1/health")

    assert response.status_code == 200


def test_upload_valid_business_file():
    thread_id = "pytest-upload-valid"
    upload_dir = Path("data/uploads") / thread_id

    try:
        with BUSINESS_FILE.open("rb") as file:
            response = client.post(
                "/api/v1/files/upload",
                data={
                    "thread_id": thread_id,
                },
                files={
                    "business_file": (
                        "business_data.xlsx",
                        file,
                        MIME_XLSX,
                    ),
                },
            )

        assert response.status_code == 200
        assert response.json()["status"] == "uploaded"

        saved_file = (
            upload_dir / "business_data.xlsx"
        )

        assert saved_file.exists()

    finally:
        shutil.rmtree(
            upload_dir,
            ignore_errors=True,
        )


def test_upload_invalid_business_file():
    thread_id = "pytest-upload-invalid"
    upload_dir = Path("data/uploads") / thread_id

    try:
        with INVALID_FILE.open("rb") as file:
            response = client.post(
                "/api/v1/files/upload",
                data={
                    "thread_id": thread_id,
                },
                files={
                    "business_file": (
                        "business_data_invalid.xlsx",
                        file,
                        MIME_XLSX,
                    ),
                },
            )

        assert response.status_code == 400

        detail = response.json()["detail"]

        assert (
            detail["message"]
            == "Invalid business data file."
        )

        assert (
            "Missing sheet: Inventory"
            in detail["errors"]
        )

        assert not (
            upload_dir / "business_data.xlsx"
        ).exists()

    finally:
        shutil.rmtree(
            upload_dir,
            ignore_errors=True,
        )
def test_upload_rejects_unsafe_thread_id():
    unsafe_thread_id = "../outside"

    with BUSINESS_FILE.open("rb") as file:
        response = client.post(
            "/api/v1/files/upload",
            data={
                "thread_id": unsafe_thread_id,
            },
            files={
                "business_file": (
                    "business_data.xlsx",
                    file,
                    MIME_XLSX,
                ),
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid thread_id."

def test_upload_rejects_unreadable_excel_file():
    thread_id = "pytest-upload-corrupt"
    upload_dir = Path("data/uploads") / thread_id

    try:
        fake_excel = BytesIO(b"this is not a real Excel file")

        response = client.post(
            "/api/v1/files/upload",
            data={
                "thread_id": thread_id,
            },
            files={
                "business_file": (
                    "business_data.xlsx",
                    fake_excel,
                    MIME_XLSX,
                ),
            },
        )

        assert response.status_code == 400

        detail = response.json()["detail"]

        assert detail["message"] == "Invalid business data file."
        assert "Unable to read Excel file." in detail["errors"]

        assert not (
            upload_dir / "business_data.xlsx"
        ).exists()

    finally:
        shutil.rmtree(
            upload_dir,
            ignore_errors=True,
        )