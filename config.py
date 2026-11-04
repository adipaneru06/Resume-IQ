"""
Configuration and scoring rubric definitions for Resumely AI.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# App / Server Settings
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# File Upload Settings
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 5))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Tesseract OCR path
TESSERACT_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

# Google Gemini API Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Database Path
DB_PATH = BASE_DIR / "resumely.db"

# ==========================================
# SCORING CRITERIA AND WEIGHTS (Single Source of Truth)
# ==========================================
# Sum of weights = 100%
SCORING_CRITERIA = [
    {
        "id": "ats_compatibility",
        "name": "ATS Compatibility",
        "tag": "Standard Format",
        "weight": 20,
        "description": "Formatting cleanliness, single-column parsing, UTF-8 font compatibility, and standard section headers."
    },
    {
        "id": "keyword_relevance",
        "name": "Keyword Relevance",
        "tag": "Role Alignment",
        "weight": 18,
        "description": "Match depth with target role title, industry job requirements, and hard technical skills."
    },
    {
        "id": "impact_achievements",
        "name": "Impact and Achievements",
        "tag": "Quantitative",
        "weight": 18,
        "description": "Measurable quantitative metrics (percentages, dollar amounts, scale) and decisive active verbs."
    },
    {
        "id": "skills_presentation",
        "name": "Skills Presentation",
        "tag": "Taxonomy",
        "weight": 12,
        "description": "Relevance, organized category groupings (Languages, Frameworks, Cloud), and stack clarity."
    },
    {
        "id": "experience_projects",
        "name": "Experience and Projects",
        "tag": "Depth",
        "weight": 12,
        "description": "Descriptive depth, problem-solving context, architectural ownership, and recency of tools."
    },
    {
        "id": "education_credentials",
        "name": "Education and Credentials",
        "tag": "Accreditation",
        "weight": 8,
        "description": "Degree accuracy, institution validation, graduation timeline consistency, and honors."
    },
    {
        "id": "language_quality",
        "name": "Language Quality",
        "tag": "Grammar",
        "weight": 6,
        "description": "Flawless grammar, executive tone, elimination of first-person pronouns, and cliché eradication."
    },
    {
        "id": "structure_length",
        "name": "Overall Structure and Length",
        "tag": "Economy",
        "weight": 6,
        "description": "Visual balance, uniform margin distribution, and disciplined 1-page economy for early to mid-level roles."
    }
]

# Total weight sanity assertion
TOTAL_WEIGHT = sum(c["weight"] for c in SCORING_CRITERIA)
assert TOTAL_WEIGHT == 100, f"Scoring criteria weights must total 100%, got {TOTAL_WEIGHT}%"

# ==========================================
# CREATOR PROFILE PLACEHOLDERS
# ==========================================
# Users can update their information here or directly in the templates
CREATOR_INFO = {
    "name": "Aditya Paneru",
    "role": "Computer Science Student & Software Builder",
    "avatar_url": "/static/images/profile.jpg",
    "tag": "Independent Builder",
    "bio": "I'm a B.Tech Data Science student passionate about technology, problem-solving, and building impactful projects. I enjoy exploring Data Science, AI/ML, software development, and emerging technologies while continuously improving my technical and creative skills. I love turning ideas into practical solutions, collaborating with others, and learning through hands-on experiences.",
    "technical_foundation": "Built with Python, Gemini AI, and OCR as a university capstone project to make high-quality resume critiques accessible to everyone without paywalled assessments.",
    "github_url": "https://github.com/adipaneru06",
    "linkedin_url": "https://www.linkedin.com/in/aditya-paneru-b976833a5/"
}

