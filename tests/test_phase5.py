"""
Phase 5 Verification Test Suite
Tests:
1. ReportLab PDF report generation & structure
2. PDF download endpoint (/report/{id}/download)
3. Custom 404 & error page rendering
4. Error states: file too large, invalid format, empty file
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app import app
from database import init_db, save_analysis
from analyzer import generate_mock_analysis_for_dev
from report import generate_pdf_report

client = TestClient(app)


def test_pdf_generation_direct():
    init_db()
    mock_data = generate_mock_analysis_for_dev("Sample resume", "Product Manager")
    record = {
        "id": "pdf_test_001",
        "filename": "sample_pm_resume.pdf",
        "created_at": "2026-11-03T12:00:00Z",
        "target_role": "Product Manager"
    }

    pdf_bytes = generate_pdf_report(record, mock_data)
    assert len(pdf_bytes) > 2000, "Generated PDF buffer is too small"
    assert pdf_bytes.startswith(b"%PDF"), "Generated file does not have valid PDF magic bytes"
    print("[OK] ReportLab direct PDF generation verified")


def test_pdf_download_route():
    init_db()
    mock_data = generate_mock_analysis_for_dev("Sample resume", "Senior Systems Engineer")
    analysis_id = "test_download_123"
    save_analysis(
        analysis_id=analysis_id,
        filename="systems_engineer.pdf",
        target_role="Senior Systems Engineer",
        job_description=None,
        analysis_data=mock_data
    )

    resp = client.get(f"/report/{analysis_id}/download")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert "attachment;" in resp.headers["content-disposition"]
    assert resp.content.startswith(b"%PDF")
    print("[OK] PDF download route verified")


def test_custom_404_error_page():
    resp = client.get("/results/missing_id_404")
    assert resp.status_code == 404
    assert "Analysis Report Not Found" in resp.text
    assert "404 Not Found" in resp.text
    print("[OK] Custom 404 error page verified")


def test_validation_errors():
    # Unsupported file extension
    resp_ext = client.post(
        "/api/extract",
        files={"file": ("malicious.exe", b"binarycontent", "application/octet-stream")}
    )
    assert resp_ext.status_code == 400
    assert "Unsupported file format" in resp_ext.json()["detail"]

    # Oversized file
    big_content = b"x" * (6 * 1024 * 1024)
    resp_size = client.post(
        "/api/extract",
        files={"file": ("huge.pdf", big_content, "application/pdf")}
    )
    assert resp_size.status_code == 400
    assert "exceeds" in resp_size.json()["detail"]
    print("[OK] Edge-case validation errors verified")


if __name__ == "__main__":
    test_pdf_generation_direct()
    test_pdf_download_route()
    test_custom_404_error_page()
    test_validation_errors()
    print("\nAll Phase 5 verification tests passed successfully!")

