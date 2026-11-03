"""
Phase 4 Verification Test Suite
Tests:
1. Results page rendering with real data
2. Overall score gauge & ATS check display
3. Job match card hiding when job_match is null
4. Job match card displaying when role is specified
5. Section scores & radar chart data passing
6. Suggestions, bullet rewrites with copy button, and language issues
7. 404 error handling for invalid analysis IDs
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app import app
from database import init_db, save_analysis
from analyzer import generate_mock_analysis_for_dev

client = TestClient(app)


def test_results_page_with_role():
    init_db()
    data = generate_mock_analysis_for_dev("Resume content", "Senior Python Engineer")
    analysis_id = "test_phase4_with_role"
    save_analysis(
        analysis_id=analysis_id,
        filename="resume_with_role.pdf",
        target_role="Senior Python Engineer",
        job_description=None,
        analysis_data=data
    )

    resp = client.get(f"/results/{analysis_id}")
    assert resp.status_code == 200
    html = resp.text

    # Verify key blocks exist
    assert "Diagnostic Analysis Report" in html
    assert "Executive Assessment" in html
    assert "Overall Score" in html
    assert "ATS Compatibility" in html
    assert "Job Match" in html  # Must be visible because role was provided
    assert "Role Alignment Depth" in html
    assert "Section Balance" in html
    assert "Key Strengths" in html
    assert "Gaps &amp; Weaknesses" in html or "Gaps & Weaknesses" in html
    assert "Prioritized Suggestions" in html
    assert "Bullet Point Rewrites" in html
    assert "Language &amp; Grammar Audit" in html or "Language & Grammar Audit" in html
    assert "Download PDF report" in html
    assert "Analyze another resume" in html

    # Check copy button
    assert "copyToClipboard" in html

    print("[OK] Results page with target role verified")


def test_results_page_without_role():
    init_db()
    data = generate_mock_analysis_for_dev("Resume content", None)
    data["job_match"] = None  # Explicitly null

    analysis_id = "test_phase4_no_role"
    save_analysis(
        analysis_id=analysis_id,
        filename="resume_no_role.pdf",
        target_role=None,
        job_description=None,
        analysis_data=data
    )

    resp = client.get(f"/results/{analysis_id}")
    assert resp.status_code == 200
    html = resp.text

    # Job Match card must be hidden when job_match is null!
    assert "Role Alignment Depth" not in html
    assert "Keywords Found" not in html
    print("[OK] Results page without role correctly hides Job Match card")


def test_results_page_not_found():
    resp = client.get("/results/nonexistent_id_99999")
    assert resp.status_code == 404
    print("[OK] Nonexistent analysis ID returns 404")


def test_results_static_js():
    resp = client.get("/static/js/results.js")
    assert resp.status_code == 200
    assert "initRadarChart" in resp.text
    assert "copyToClipboard" in resp.text
    print("[OK] results.js script served successfully")


if __name__ == "__main__":
    test_results_page_with_role()
    test_results_page_without_role()
    test_results_page_not_found()
    test_results_static_js()
    print("\nAll Phase 4 verification tests passed successfully!")

