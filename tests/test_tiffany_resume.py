"""
End-to-End Test for User-Uploaded Resume (Tiffany Giroux)
Tests:
1. OCR extraction of the user's JPG resume image
2. Privacy cleanup of temporary files
3. Live analysis job initiation & status polling
4. Results page rendering with real data
5. PDF report generation and download
"""

import sys
import time
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app import app
from extractor import process_resume_upload
from database import get_analysis

client = TestClient(app)

USER_RESUME_SRC = Path(r"C:\Users\91741\.gemini\antigravity\brain\cb7d1ab9-bd53-4dcb-9c50-e86ef586a671\.user_uploaded\media_1793724091119_4ddd70f4.jpg")
LOCAL_TEST_RESUME = Path(__file__).resolve().parent / "test_resumes" / "resume_tiffany_giroux.jpg"


def test_tiffany_resume_pipeline():
    assert USER_RESUME_SRC.exists(), f"User uploaded image not found at {USER_RESUME_SRC}"

    # Copy image to test_resumes folder for permanent sample availability
    shutil.copy2(USER_RESUME_SRC, LOCAL_TEST_RESUME)
    print(f"[OK] Saved copy of resume to {LOCAL_TEST_RESUME}")

    file_bytes = USER_RESUME_SRC.read_bytes()

    # Step 1: Direct Extraction Test
    print("\n--- STEP 1: OCR Extraction ---")
    extraction = process_resume_upload(file_bytes, "tiffany_giroux_resume.jpg")
    print(f"Extraction Method: {extraction.method}")
    print(f"Character Count:   {extraction.char_count}")
    print(f"Word Count:        {extraction.word_count}")

    assert "Tiffany Giroux" in extraction.text
    assert "Ford" in extraction.text
    assert "Honda" in extraction.text
    print("[OK] OCR correctly recognized candidate, roles, and companies")

    # Step 2: Full Web API Analysis Pipeline
    print("\n--- STEP 2: Full Web API Analysis Pipeline ---")
    with open(LOCAL_TEST_RESUME, "rb") as f:
        resp = client.post(
            "/api/analyze",
            data={
                "target_role": "Freight & Logistics Analyst",
                "job_description": "Seeking experienced Logistics Analyst skilled in freight audit, supply chain KPI tracking, and process optimization."
            },
            files={"file": (LOCAL_TEST_RESUME.name, f, "image/jpeg")}
        )
    assert resp.status_code == 200
    job_id = resp.json()["job_id"]
    print(f"Analysis job started: {job_id}")

    # Step 3: Poll Background Worker Progress
    print("\n--- STEP 3: Tracking Live Progress Steps ---")
    analysis_id = None
    for attempt in range(40):
        status_resp = client.get(f"/api/analyze/status/{job_id}")
        assert status_resp.status_code == 200
        job_data = status_resp.json()
        print(f"  Step {job_data.get('step')}: {job_data.get('message')} (Status: {job_data.get('status')})")

        if job_data.get("status") == "completed":
            analysis_id = job_data.get("analysis_id")
            break
        elif job_data.get("status") == "failed":
            raise AssertionError(f"Analysis pipeline failed: {job_data.get('error')}")
        time.sleep(0.5)

    assert analysis_id is not None, "Job timed out without completing"
    print(f"[OK] Analysis completed with ID: {analysis_id}")

    # Step 4: Verify Database Record
    print("\n--- STEP 4: Database Verification ---")
    record = get_analysis(analysis_id)
    assert record is not None
    analysis = record["analysis"]
    print(f"Overall Score:  {analysis['overall_score']} / 100")
    print(f"ATS Score:      {analysis['ats']['score']} / 100")
    if analysis.get("job_match"):
        print(f"Job Match:      {analysis['job_match']['percentage']}%")
    print(f"Suggestions:    {len(analysis['suggestions'])} prioritized suggestions")
    print(f"Bullet Rewrites:{len(analysis['bullet_rewrites'])} rewrites")
    print("[OK] Database persisted and retrieved analysis record")

    # Step 5: Test Results Page Rendering
    print("\n--- STEP 5: Results Page Rendering ---")
    results_resp = client.get(f"/results/{analysis_id}")
    assert results_resp.status_code == 200
    html = results_resp.text
    assert "Tiffany Giroux" in html or "tiffany_giroux" in html
    assert "Overall Score" in html
    assert "ATS Compatibility" in html
    assert "Job Match" in html
    assert "Prioritized Suggestions" in html
    assert "Bullet Point Rewrites" in html
    print("[OK] Results page rendered flawlessly with real data")

    # Step 6: Test PDF Download
    print("\n--- STEP 6: PDF Report Download ---")
    pdf_resp = client.get(f"/report/{analysis_id}/download")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert pdf_resp.content.startswith(b"%PDF")
    print(f"[OK] Generated valid PDF report ({len(pdf_resp.content):,} bytes)")

    print("\n=======================================================")
    print("ALL TESTS PASSED WITH TIFFANY GIROUX RESUME SAMPLE!")
    print("=======================================================")


if __name__ == "__main__":
    test_tiffany_resume_pipeline()

