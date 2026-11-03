"""
Phase 1 Verification Test
Verifies route rendering, template rendering, and asset accessibility.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app import app
from config import SCORING_CRITERIA, CREATOR_INFO

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["criteria_count"] == len(SCORING_CRITERIA)
    print("[OK] Health check passed")


def test_landing_page_render():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    # Verify key sections exist
    assert 'id="analyze"' in html
    assert 'id="what-you-get"' in html
    assert 'id="how-it-works"' in html
    assert 'id="criteria"' in html
    assert 'id="suggestions"' in html
    assert 'id="about"' in html

    # Verify design copy and tokens
    assert "Find out how your resume performs before a recruiter does." in html
    assert "Editorial ATS Intelligence" in html
    assert "Transparent Architecture" in html
    assert "What you&#39;ll get" in html or "What you'll get" in html

    # Verify all 8 criteria exist with correct weights
    for criterion in SCORING_CRITERIA:
        assert criterion["name"] in html
        assert f'{criterion["weight"]}%' in html

    # Verify creator placeholders
    assert CREATOR_INFO["name"] in html
    assert "Computer Science Student" in html
    assert CREATOR_INFO["avatar_url"] in html

    print("[OK] Landing page template rendered with 100% fidelity")


def test_static_assets():
    resp_logo = client.get("/static/images/logo.png")
    assert resp_logo.status_code == 200
    assert len(resp_logo.content) > 0

    resp_profile = client.get("/static/images/profile.jpg")
    assert resp_profile.status_code == 200
    assert len(resp_profile.content) > 0

    resp_css = client.get("/static/css/custom.css")
    assert resp_css.status_code == 200

    resp_js = client.get("/static/js/upload.js")
    assert resp_js.status_code == 200

    print("[OK] Static assets served successfully")


if __name__ == "__main__":
    test_health_check()
    test_landing_page_render()
    test_static_assets()
    print("\nAll Phase 1 tests passed successfully!")
