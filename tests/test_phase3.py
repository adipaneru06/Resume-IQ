"""
Phase 3 Verification Test Suite
Tests:
1. Pydantic schema validation & constraints
2. SQLite persistence & retrieval
3. Gemini Analyzer prompt construction & rubric weights alignment
4. Resume analysis execution (with & without target role)
5. Background analysis API pipeline & step-by-step progress tracking
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app import app
from schemas import ResumeAnalysisSchema, ATSCheck, CriterionScore
from database import init_db, save_analysis, get_analysis, list_recent_analyses
from analyzer import build_analysis_prompt, analyze_resume, generate_mock_analysis_for_dev
from config import SCORING_CRITERIA

client = TestClient(app)
test_resumes_dir = Path(__file__).resolve().parent / "test_resumes"


def test_schema_validation():
    mock_data = generate_mock_analysis_for_dev("Sample resume text", "Software Engineer")
    validated = ResumeAnalysisSchema.model_validate(mock_data)
    assert validated.overall_score in (78, 79)
    assert validated.ats.score in (85, 86)
    assert len(validated.criteria_scores) == 8
    assert validated.job_match is not None
    assert validated.job_match.percentage == 82
    print("[OK] Schema validation verified")


def test_database_crud():
    init_db()
    import uuid
    mock_data = generate_mock_analysis_for_dev("Sample resume text")
    test_id = f"test_analysis_{uuid.uuid4().hex[:8]}"

    saved_id = save_analysis(
        analysis_id=test_id,
        filename="test_alex.pdf",
        target_role="Frontend Engineer",
        job_description=None,
        analysis_data=mock_data
    )
    assert saved_id == test_id

    retrieved = get_analysis(test_id)
    assert retrieved is not None
    assert retrieved["filename"] == "test_alex.pdf"
    assert retrieved["overall_score"] in (78, 79)
    assert retrieved["analysis"]["ats"]["score"] in (85, 86)

    recent = list_recent_analyses(5)
    assert any(r["id"] == test_id for r in recent)
    print("[OK] SQLite database operations verified")


def test_prompt_rubric_alignment():
    prompt = build_analysis_prompt("Resume body", "DevOps Engineer", "Kubernetes experience needed")
    for criterion in SCORING_CRITERIA:
        assert criterion["name"] in prompt
        assert f"{criterion['weight']}%" in prompt
    assert "DevOps Engineer" in prompt
    print("[OK] Prompt rubric alignment verified")


def test_analyzer_role_condition():
    # 1. Without target role/JD -> job_match must be None
    res_no_role = analyze_resume("Full-Stack Developer with 5 years experience in Python and databases.")
    assert res_no_role.job_match is None, "job_match should be None when no role/JD provided"

    # 2. With target role -> job_match must be populated
    res_with_role = analyze_resume(
        "Full-Stack Developer with 5 years experience in Python and databases.",
        target_role="Senior Python Engineer"
    )
    assert res_with_role.job_match is not None
    assert res_with_role.job_match.percentage > 0
    print("[OK] Analyzer job_match condition verified")


def test_real_time_analysis_pipeline():
    pdf_path = test_resumes_dir / "resume_software_engineer.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        resp = client.post(
            "/api/analyze",
            data={"target_role": "Junior Software Engineer"},
            files={"file": (pdf_path.name, f, "application/pdf")}
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    job_id = data["job_id"]

    # Poll status until completed (max 10 seconds)
    completed = False
    for _ in range(20):
        status_resp = client.get(f"/api/analyze/status/{job_id}")
        assert status_resp.status_code == 200
        job_status = status_resp.json()
        assert job_status["step"] in (0, 1, 2, 3, 4)

        if job_status["status"] == "completed":
            completed = True
            assert job_status["analysis_id"] is not None
            assert f"/results/{job_status['analysis_id']}" in job_status["redirect_url"]
            break
        elif job_status["status"] == "failed":
            raise AssertionError(f"Job failed unexpectedly: {job_status.get('error')}")
        time.sleep(0.3)

    assert completed, "Analysis job did not complete within timeout"
    print("[OK] Real-time background analysis pipeline and polling verified")


if __name__ == "__main__":
    test_schema_validation()
    test_database_crud()
    test_prompt_rubric_alignment()
    test_analyzer_role_condition()
    test_real_time_analysis_pipeline()
    print("\nAll Phase 3 verification tests passed successfully!")
