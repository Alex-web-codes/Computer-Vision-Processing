import os
import json
import pytest
from fastapi.testclient import TestClient
from server import app, OUTPUT_DIR, UPLOADS_DIR

client = TestClient(app)

def test_health_and_ui():
    response = client.get("/")
    assert response.status_code == 200
    assert "Automatic Timetable Parser" in response.text

def test_list_timetables():
    response = client.get("/api/timetables")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "files" in data

def test_upload_pdf_timetable():
    sample_pdf = os.path.join(os.path.dirname(__file__), "7th Sem CSEA.pdf")
    assert os.path.exists(sample_pdf)

    with open(sample_pdf, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("test_csea.pdf", f, "application/pdf")}
        )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert "download_urls" in result
    assert "data" in result
    assert "metadata" in result["data"]
    assert result["data"]["metadata"]["total_days"] > 0

def test_download_file():
    # Verify that listing output files and downloading works
    response_list = client.get("/api/timetables")
    files = response_list.json()["files"]
    if files:
        target_file = files[0]["filename"]
        response_download = client.get(f"/api/download/{target_file}")
        assert response_download.status_code == 200

if __name__ == "__main__":
    pytest.main(["-v", __file__])
