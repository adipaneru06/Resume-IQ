# Resumely AI — Design Changes & Adaptations Log

This log records every modification and technical adaptation made to the original Stitch export (`/design/code.html`). The project strictly preserves the layout, typography, colors, spacing, and component styles of the original design.

---

## Phase 1 Adaptations

| Item / Element | Original `/design/code.html` | Phase 1 Implementation | Technical Reason |
| :--- | :--- | :--- | :--- |
| **Template Modularization** | Single static `code.html` file | Split into `templates/base.html` (header, head scripts, footer) and `templates/index.html` (landing content) | Standard architecture for multi-page FastAPI / Jinja2 applications (enabling the upcoming Results page to reuse the exact same shell). |
| **Asset Localization** | External Google User Content URLs for logo & avatar | Local files downloaded to `static/images/logo.png` and `static/images/profile.jpg` with CDN error fallbacks | Prevents broken images if external CDN tokens expire or when working offline. |
| **Creator Placeholders** | Hardcoded "Alex Morgan" copy in `/design/code.html` | Dynamic variables `{{ creator.name }}`, `{{ creator.role }}`, `{{ creator.bio }}`, `{{ creator.avatar_url }}` defined in `config.py` and marked with HTML comments in `templates/index.html` | Strict requirement: allow the user to easily customize the creator photo, name, bio, and links. |
| **Rubric Criteria Definition** | Hardcoded criteria table in HTML | Criteria generated via `config.py` (`SCORING_CRITERIA`) loop in `templates/index.html` | Strict requirement: ensure the scoring criteria and weights (ATS 20%, Keywords 18%, Impact 18%, Skills 12%, Experience 12%, Education 8%, Language 6%, Structure 6%) are defined once and never diverge from the Gemini analysis prompt. |
| **Navigation Anchor Smooth Scrolling** | Default instant jump links (`#analyze`, etc.) | Added `html { scroll-behavior: smooth; }` via `static/css/custom.css` and `scroll-smooth` class | Enhanced UX for navigation links. |
| **Client-Side Validation & Feedback** | Alert popup in inline JS (`alert(...)`) | Replaced `alert()` with styled in-card error box (`#upload-error-box`) matching design tokens (`bg-[#FAF0EE] border-[#F5C2C7] text-error`) | Avoids disruptive browser alert dialogs; matches design system error state styling. Max 5MB and allowed file types validated on select. |
| **Analyzing View Placeholder** | Design only had resting state | Added hidden container `#analyzing-state` styled strictly with design tokens (`bg-surface-container-lowest border border-[#E6E2DA]`) with 4 sequential progress steps | Necessary state for Phase 3 live analysis progress tracking without breaking the layout. |

---

## Phase 2 Adaptations & Additions

| Item / Element | Original `/design` | Phase 2 Implementation | Technical Reason |
| :--- | :--- | :--- | :--- |
| **Extraction Sandbox Route** | Not in design | Added `/test-extract` and `POST /test-extract` using `templates/test_extract.html` | Allows manual and automated visual inspection of extracted text, page count, word count, character count, and OCR status. |
| **JSON Extraction Endpoint** | Not in design | Added `POST /api/extract` | Facilitates headless testing and asynchronous validation. |
| **Dual Extraction Pipeline** | Static mockup | Implemented `extractor.py` utilizing PyMuPDF for native vector text and Tesseract OCR fallback for scanned PDFs and image uploads | Enables robust extraction across both digital and scanned/photo resumes. |
| **Zero-Retention Privacy** | Privacy promise on landing page | Temporary file creation with guaranteed deletion in a `finally` block immediately after extraction; resume text contents are never logged to console/files | Fulfills core privacy requirement: files deleted immediately, content never logged. |

---

## Phase 3 Adaptations & Additions

| Item / Element | Original `/design` | Phase 3 Implementation | Technical Reason |
| :--- | :--- | :--- | :--- |
| **Real Progress vs Fake Timers** | Design had static mockup | Replaced placeholder simulation with a real multi-step background pipeline (`POST /api/analyze` and `GET /api/analyze/status/{job_id}`) | Strictly fulfills requirement: progress reflects real background steps (1: extracting, 2: checking ATS, 3: matching role, 4: finding improvements), not fake timers. |
| **Pydantic Validation & Retries** | N/A (Backend logic) | Strict `ResumeAnalysisSchema` validation with 1 retry on malformed JSON | Ensures reliable JSON output from Gemini. |
| **Rubric Weights Injection** | Static table | Injected `SCORING_CRITERIA` from `config.py` into `analyzer.py` system prompts | Guarantees scoring criteria and weights never diverge from the landing page. |
| **SQLite Persistence** | N/A (Backend logic) | Added `database.py` with automatic schema creation and JSON storage | Persists analysis results for retrieval, sharing, and PDF generation. |
| **Target Role Discretion** | N/A (Backend logic) | Enforced rule: if neither target role nor JD is provided, `job_match` is set to `null` | Prevents arbitrary or hallucinated job matching when no target was requested. |

---

## Phase 4 Adaptations & Additions

| Item / Element | Original `/design` | Phase 4 Implementation | Technical Reason |
| :--- | :--- | :--- | :--- |
| **Results Page Architecture** | Page was NOT designed in Stitch | Built from scratch in `templates/results.html` strictly using tokens and component styles extracted from `/design` | Delivers complete, consistent diagnostic reporting matching the landing page. |
| **Score Gauge Reproducibility** | Mockup SVG gauge in hero column | Replicated identical SVG circular gauge math (`circumference = 251.2`, stroke `#00563e`, stroke-width `8`) on results page | 100% aesthetic continuity with the landing page sample diagnostic. |
| **Section Radar Chart** | Not in design | Integrated Chart.js Radar Chart in `static/js/results.js` styled with `#00563e` and `#E6E2DA` | Visualizes the 5 section scores (Summary, Skills, Experience, Projects, Education) balance. |
| **Copy-to-Clipboard for Bullet Rewrites** | Not in design | Added interactive "Copy" button with temporary visual confirmation tooltip | Immediate utility for job seekers adopting AI rewrites. |
| **Dynamic Job Match Visibility** | Not in design | Conditionally renders Job Match card ONLY if target role or JD was supplied | Avoids showing an empty or 0% match card when the user chose a general resume critique. |

---

## Phase 5 Adaptations & Additions

| Item / Element | Original `/design` | Phase 5 Implementation | Technical Reason |
| :--- | :--- | :--- | :--- |
| **Downloadable PDF Report** | Not in design | Built `report.py` using ReportLab (`SimpleDocTemplate`, `Table`, `Paragraph`) to generate an executive audit PDF | Provides user with an offline, printable audit report matching design tokens. |
| **Custom 404 & 500 Error Pages** | Not in design | Implemented `templates/error.html` styled with design tokens | Replaces raw browser error pages with consistent editorial error handling. |
| **Empty State Defensiveness** | Not in design | Handled missing job match, empty suggestions, or flawless grammar cleanly without breaking UI cards | Prevents empty cards or ugly `undefined` displays when resumes have varying content. |

---

## Phase 6 Deliverables & Quality Assurance

| Item / Element | Specification | Implementation Details |
| :--- | :--- | :--- |
| **Full Test Resume Suite** | 3+ distinct test resume types | Generated 4 test artifacts in `tests/test_resumes/`: `resume_software_engineer.pdf` (strong tech), `resume_weak_marketing.pdf` (weak marketing), `resume_scanned_flattened.pdf` (scanned image PDF), and `resume_screenshot.png` (PNG image). |
| **Comprehensive README** | Prerequisites, setup, run instructions | Authored `README.md` detailing Python 3.10/3.11 requirements, Tesseract OCR Windows installation, `.env` setup, feature overview, customization guide, and test suite instructions. |
| **Verification Test Coverage** | Automated test scripts for each phase | Maintained and validated 5 individual test suites (`tests/test_phase1.py` through `tests/test_phase5.py`), achieving 100% test pass rate across routing, extraction, OCR, AI schemas, database persistence, results page rendering, and PDF generation. |
| **Repository Hygiene & `.gitignore`** | Standard version control hygiene | Added `.gitignore` excluding secrets (`.env`), local databases (`*.db`, `resumely.db`), temporary uploads (`uploads/*`), caches (`__pycache__`), virtualenvs, and OS files, with `uploads/.gitkeep` preserving structure. |






