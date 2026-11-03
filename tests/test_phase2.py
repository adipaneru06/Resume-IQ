"""
Phase 2 Verification Test Suite
Tests text extraction across:
1. Digital PDF (PyMuPDF Direct Text)
2. Scanned / Flattened PDF (PyMuPDF render + Tesseract OCR)
3. Image file (PNG / Tesseract OCR)
4. Temporary file privacy cleanup
5. Web route /test-extract and /api/extract
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app import app
from extractor import process_resume_upload, ExtractionError, EmptyExtractionError
from config import UPLOAD_DIR

client = TestClient(app)
test_resumes_dir = Path(__file__).resolve().parent / "test_resumes"


def test_digital_pdf_extraction():
    pdf_path = test_resumes_dir / "resume_software_engineer.pdf"
    assert pdf_path.exists(), "Digital test resume missing"

    result = process_resume_upload(pdf_path.read_bytes(), pdf_path.name)
    assert result.method == "PyMuPDF (Direct Text)", f"Unexpected method: {result.method}"
    assert result.is_ocr is False
    assert result.page_count == 1
    assert "ALEX RIVERA" in result.text
    assert "FastAPI" in result.text
    assert "Berkeley" in result.text
    assert result.word_count > 100
    print("[OK] Digital PDF direct extraction verified")


def test_image_ocr_extraction():
    img_path = test_resumes_dir / "resume_screenshot.png"
    assert img_path.exists(), "Image test resume missing"

    result = process_resume_upload(img_path.read_bytes(), img_path.name)
    assert "Tesseract OCR" in result.method, f"Unexpected method: {result.method}"
    assert result.is_ocr is True
    assert "JORDAN CHEN" in result.text.upper()
    assert "ANALYST" in result.text.upper()
    print("[OK] PNG image OCR extraction verified")


def test_scanned_pdf_ocr_extraction():
    scanned_path = test_resumes_dir / "resume_scanned_flattened.pdf"
    assert scanned_path.exists(), "Scanned test resume missing"

    result = process_resume_upload(scanned_path.read_bytes(), scanned_path.name)
    assert result.method == "PyMuPDF + Tesseract OCR (Scanned PDF)", f"Unexpected method: {result.method}"
    assert result.is_ocr is True
    assert "JORDAN CHEN" in result.text.upper()
    assert result.page_count == 1
    print("[OK] Scanned PDF automatic OCR fallback verified")


def test_privacy_cleanup():
    # Verify uploads directory contains no leftover files
    leftover_files = list(UPLOAD_DIR.glob("*"))
    assert len(leftover_files) == 0, f"Found leaked temporary files in uploads: {leftover_files}"
    print("[OK] Privacy cleanup verified: zero files retained in uploads/")


def test_web_routes():
    # 1. GET /test-extract
    resp_get = client.get("/test-extract")
    assert resp_get.status_code == 200
    assert "Extraction Sandbox" in resp_get.text
    assert "Phase 2 Test Route" in resp_get.text

    # 2. POST /test-extract with PDF
    pdf_path = test_resumes_dir / "resume_software_engineer.pdf"
    with open(pdf_path, "rb") as f:
        resp_post = client.post(
            "/test-extract",
            files={"file": (pdf_path.name, f, "application/pdf")}
        )
    assert resp_post.status_code == 200
    assert "ALEX RIVERA" in resp_post.text
    assert "PyMuPDF (Direct Text)" in resp_post.text
    assert "Temporary file purged from disk immediately" in resp_post.text

    # 3. POST /api/extract JSON endpoint
    with open(pdf_path, "rb") as f:
        resp_api = client.post(
            "/api/extract",
            files={"file": (pdf_path.name, f, "application/pdf")}
        )
    assert resp_api.status_code == 200
    data = resp_api.json()
    assert data["success"] is True
    assert data["is_ocr"] is False
    assert "FastAPI" in data["text"]

    # 4. Error testing: Unsupported extension
    resp_bad_ext = client.post(
        "/api/extract",
        files={"file": ("invalid.txt", b"plain text content", "text/plain")}
    )
    assert resp_bad_ext.status_code == 400
    assert "Unsupported file format" in resp_bad_ext.json()["detail"]

    # 5. Error testing: File too large (> 5MB)
    huge_bytes = b"0" * (6 * 1024 * 1024)  # 6MB
    resp_huge = client.post(
        "/api/extract",
        files={"file": ("huge.pdf", huge_bytes, "application/pdf")}
    )
    assert resp_huge.status_code == 400
    assert "exceeds" in resp_huge.json()["detail"]

    print("[OK] Web test routes and error validations verified")


if __name__ == "__main__":
    test_digital_pdf_extraction()
    test_image_ocr_extraction()
    test_scanned_pdf_ocr_extraction()
    test_privacy_cleanup()
    test_web_routes()
    print("\nAll Phase 2 verification tests passed successfully!")

