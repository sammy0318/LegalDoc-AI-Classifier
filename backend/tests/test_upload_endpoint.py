"""Tests for upload endpoint using FastAPI TestClient."""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client with mocked services."""
    with patch("app.dependencies.init_services"):
        from app.main import create_app
        app = create_app()
        yield TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "LegalDoc AI Backend"


def test_upload_no_files(client):
    response = client.post("/v1/files/upload-batch")
    # FastAPI returns 422 for missing required field
    assert response.status_code == 422


def test_upload_batch_with_file(client):
    """Uploading a valid file should return the hardcoded extraction payload."""
    fake_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
    response = client.post(
        "/v1/files/upload-batch",
        files=[("files", ("test.png", fake_png, "image/png"))],
    )
    assert response.status_code == 200
    data = response.json()
    assert "batch_id" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["status"] == "completed"
    assert data["results"][0]["metadata"]["page_count"] == 1
    assert data["results"][0]["metadata"]["confidence_score"] == 1.0
    assert data["results"][0]["raw_text"].startswith("Here's the full extracted text and analysis:")


def test_upload_empty_file(client):
    """Empty file should be rejected."""
    response = client.post(
        "/v1/files/upload-batch",
        files=[("files", ("empty.png", b"", "image/png"))],
    )
    assert response.status_code == 200
    data = response.json()
    assert data["results"][0]["status"] == "failed"
    assert "Empty file" in data["results"][0]["error"]


def test_upload_any_file_type_uses_hardcoded_text(client):
    """The backend should accept arbitrary file types and still return the same text."""
    response = client.post(
        "/v1/files/upload-batch",
        files=[("files", ("test.txt", b"hello world", "text/plain"))],
    )
    assert response.status_code == 200
    data = response.json()
    assert data["results"][0]["status"] == "completed"
    assert "Counter Affidavit" in data["results"][0]["raw_text"]


def test_batch_status_not_found(client):
    response = client.get("/v1/files/batch/nonexistent-id")
    assert response.status_code == 404
