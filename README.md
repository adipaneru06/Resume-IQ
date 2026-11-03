# Resumely AI — Editorial ATS Resume Analyzer

> **College Project & Independent Capstone**  
> An AI-powered resume analyzer web application built with **FastAPI**, **PyMuPDF**, **Tesseract OCR**, **Google Gemini**, **ReportLab**, and **Chart.js**.  
> Faithfully styled with an editorial design system inspired by physical print publishing and rigorous hiring desk standards.

---

## 1. System Requirements & Prerequisites

- **Python**: Version `3.10` or `3.11` (Tested on Python `3.11.1`).
- **Operating System**: Windows (tested on Windows 10/11), macOS, or Linux.
- **Tesseract OCR**:
  - **Windows**: Install the official 64-bit binary from [UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki).
  - Default installation directory: `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - (If installed to a custom directory, update `TESSERACT_PATH` in your `.env` file).

---

## 2. Quickstart Installation & Setup

### Step 1: Install Dependencies
Open PowerShell or your command prompt in the project root (`d:\resume`) and install the required packages:

```powershell
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env` (a pre-configured `.env` is already created):

```powershell
cp .env.example .env
```

Open `.env` in any text editor and fill in your settings:

```ini
# Google Gemini API Key (Get a free key from https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Tesseract OCR Executable Path
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# Server Settings
HOST=127.0.0.1
PORT=8000
DEBUG=True
MAX_FILE_SIZE_MB=5
```

> **Note for Local Testing**: If `GEMINI_API_KEY` is not provided or left blank, the application automatically activates a realistic, rubric-aligned fallback analysis engine. This allows offline testing, classroom grading, and UI inspection with zero setup friction!

---

## 3. Running the Application

Start the local server using Python:

```powershell
python app.py
```

Or run via Uvicorn with auto-reload:

```powershell
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Then visit:
- **Landing Desk & Analyzer**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Extraction Test Sandbox**: [http://127.0.0.1:8000/test-extract](http://127.0.0.1:8000/test-extract)
- **API Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 4. Key Features & Workflow

1. **Pixel-Faithful Landing Desk**:
   - Reuses the Stitch export layout, typography (*Newsreader* serif + *Inter* sans-serif), colors, hairline borders (`#E6E2DA`), and warm canvas tone (`#FAF8F4`).
   - Drag-and-drop file upload supporting PDF, PNG, JPG up to 5MB.
   - Optional target job role input and collapsible job description textarea.
   - Smooth-scrolling anchor navigation to all sections (`What You Get`, `How it works`, `Criteria`, `About`).

2. **Dual-Extraction Pipeline with Zero Data Retention**:
   - **PyMuPDF**: Rapid direct UTF-8 text extraction from digital PDFs.
   - **Tesseract OCR Fallback**: If a PDF is a flat image or scanned document (< 50 characters of selectable text), pages are automatically rendered to 200 DPI pixmaps and OCR-parsed.
   - **Image OCR**: Direct text recognition for PNG and JPG screenshots.
   - **Privacy First**: Uploaded documents are deleted immediately after text extraction. Resume contents are never stored in plain text or logged to the console.

3. **Real-Time Backend Progress Tracking**:
   - Live sequential feedback (Extracting text &rarr; Auditing ATS format &rarr; Matching role keywords &rarr; Finding improvements).
   - Driven by actual background pipeline events via polling (`/api/analyze/status/{job_id}`), avoiding artificial timer delays.

4. **Comprehensive Diagnostic Results Page**:
   - **Executive Assessment**: Editorial AI verdict summarizing profile positioning.
   - **Overall Score Gauge**: Circular SVG gauge with qualitative tier rating.
   - **ATS Compatibility**: Detailed pass/fail checks across contact anchors, layouts, and header standards.
   - **Job Match**: Role alignment percentage with matched vs missing keyword chips (automatically hidden when no target role is requested).
   - **Section Benchmarks**: Interactive Chart.js radar chart visualizing structural balance across *Summary*, *Skills*, *Experience*, *Projects*, and *Education*.
   - **Rubric Performance**: Scores against the 8 transparent criteria defined in `config.py`.
   - **Strengths & Weaknesses**: Clear asset highlights and prioritized gap flags.
   - **Prioritized Suggestions**: High, Medium, and Low impact cards with exact problem statements and actionable fixes.
   - **Before / After Bullet Rewrites**: Real resume bullet transformations with a 1-click **Copy** button.
   - **Language Quality**: Identifies passive voice, corporate buzzwords, grammar issues, and overly verbose sentences.

5. **Exportable PDF Audit Report**:
   - Built with **ReportLab**, styled with matching editorial design tokens.
   - Downloadable in one click from the results page (`/report/{id}/download`).

---

## 5. Customizing the Creator Profile

The landing page includes an "About the creator" section with clearly marked placeholders:
- **Photo**: Replace `static/images/profile.jpg` with your own portrait.
- **Name, Bio, and Social Links**: Update `CREATOR_INFO` in `config.py` or edit the placeholders in `templates/index.html`:
  - `name`: Your full name
  - `role`: e.g., *"Computer Science Student"*
  - `bio`: Your personal description
  - `github_url`: Your GitHub link
  - `linkedin_url`: Your LinkedIn profile

---

## 6. Pre-Generated Test Resumes

Sample test resumes are provided in `tests/test_resumes/`:

| Filename | Type | Description |
| :--- | :--- | :--- |
| `resume_software_engineer.pdf` | Digital PDF | Strong technical resume with quantified metrics, tech stack, and clear dates. |
| `resume_weak_marketing.pdf` | Digital PDF | Weak resume lacking numbers, filled with passive voice ("Was responsible for") and buzzwords. |
| `resume_scanned_flattened.pdf` | Scanned PDF | Flattened image-only PDF with zero text layer (triggers automatic OCR fallback). |
| `resume_screenshot.png` | Image (PNG) | Screenshot format for testing direct image OCR parsing. |

To regenerate or add new test files:
```powershell
python tests/generate_test_resumes.py
```

---

## 7. Running the Automated Test Suite

Each phase of the project includes a dedicated automated test suite:

```powershell
# Phase 1: Landing page template fidelity & static assets
python tests/test_phase1.py

# Phase 2: PyMuPDF extraction, Tesseract OCR fallback, and privacy cleanup
python tests/test_phase2.py

# Phase 3: Pydantic schemas, SQLite persistence, and real-time analysis pipeline
python tests/test_phase3.py

# Phase 4: Results page rendering, radar chart data, and role condition
python tests/test_phase4.py

# Phase 5: ReportLab PDF report generation, error states, and download route
python tests/test_phase5.py
```

Or run all tests in sequence:
```powershell
python tests/test_phase1.py; python tests/test_phase2.py; python tests/test_phase3.py; python tests/test_phase4.py; python tests/test_phase5.py
```

---

## 8. Project Structure

```
d:\resume\
├── app.py                     # FastAPI application, routing, error handlers, and async workers
├── config.py                  # Environment config, single-source-of-truth scoring criteria & weights
├── extractor.py               # PyMuPDF direct text parser + Tesseract OCR fallback pipeline
├── analyzer.py                # Gemini client (google-genai), prompt constants, rate-limit retry logic
├── schemas.py                 # Pydantic models for JSON validation
├── database.py                # SQLite schema and analysis persistence
├── report.py                  # ReportLab PDF report builder matching design tokens
├── design/                    # Original Stitch export (intact)
│   ├── code.html
│   ├── DESIGN.md
│   └── screen.png
├── templates/
│   ├── base.html              # Core HTML shell (header, Tailwind config, fonts, footer)
│   ├── index.html             # Pixel-faithful landing desk
│   ├── results.html           # Comprehensive results report page
│   ├── test_extract.html      # Extraction test sandbox
│   └── error.html             # Custom 404 & 500 editorial error templates
├── static/
│   ├── css/
│   │   └── custom.css         # Smooth scrolling and focus ring styles
│   ├── js/
│   │   ├── upload.js          # File validation, drag-and-drop, and real-time progress polling
│   │   └── results.js         # Radar chart rendering and copy-to-clipboard helpers
│   └── images/
│       ├── logo.png           # Local localized logo
│       └── profile.jpg        # Creator avatar placeholder
├── uploads/                   # Temporary directory (files deleted immediately after extraction)
├── tests/
│   ├── test_resumes/          # 4 sample resumes (strong tech, weak marketing, scanned PDF, image PNG)
│   ├── generate_test_resumes.py
│   ├── test_phase1.py
│   ├── test_phase2.py
│   ├── test_phase3.py
│   ├── test_phase4.py
│   └── test_phase5.py
├── .env.example               # Environment variables template
├── .env                       # Local environment file
├── requirements.txt           # Python package dependencies
├── README.md                  # Comprehensive documentation and run guide
└── CHANGES.md                 # Full changelog of design adaptations
```

