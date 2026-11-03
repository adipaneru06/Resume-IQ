"""
Generates 3+ sample test resumes for Resumely AI:
1. Strong Tech Resume (Digital PDF with quantified bullets & metrics)
2. Weak Marketing Resume (Digital PDF with passive voice, vague buzzwords, no numbers)
3. Scanned / Flattened Resume (Image-only PDF, zero text layer for OCR testing)
4. Image Resume Screenshot (PNG for direct image OCR)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pymupdf
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw

output_dir = Path(__file__).resolve().parent / "test_resumes"
output_dir.mkdir(parents=True, exist_ok=True)


def create_strong_tech_pdf():
    """Creates a high-quality digital PDF with searchable text."""
    pdf_path = output_dir / "resume_software_engineer.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "ALEX RIVERA")

    c.setFont("Helvetica", 9)
    c.drawString(50, 735, "San Francisco, CA | alex.rivera@email.com | (555) 019-2834 | github.com/alexrivera")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 705, "PROFESSIONAL SUMMARY")
    c.setFont("Helvetica", 10)
    c.drawString(50, 688, "Full-Stack Software Engineer with 3+ years of experience designing scalable microservices,")
    c.drawString(50, 674, "RESTful APIs, and responsive web applications. Experienced in Python, React, and AWS cloud.")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 645, "TECHNICAL SKILLS")
    c.setFont("Helvetica", 10)
    c.drawString(50, 628, "Languages: Python, JavaScript, TypeScript, Go, SQL, HTML5, CSS3")
    c.drawString(50, 614, "Frameworks: FastAPI, Django, Flask, React.js, Next.js, Node.js")
    c.drawString(50, 600, "Cloud & DevOps: Docker, Kubernetes, AWS (EC2, S3, RDS), GitHub Actions, CI/CD")
    c.drawString(50, 586, "Databases: PostgreSQL, Redis, MongoDB, SQLite")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 555, "PROFESSIONAL EXPERIENCE")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 538, "Apex Cloud Technologies — Junior Software Engineer (2022 - Present)")
    c.setFont("Helvetica", 10)
    c.drawString(60, 522, "• Architected and deployed 14 asynchronous API microservices handling 450K+ daily requests.")
    c.drawString(60, 508, "• Reduced database query latency by 38% through Redis caching and PostgreSQL index tuning.")
    c.drawString(60, 494, "• Collaborated with team of 8 engineers in Agile sprints, maintaining 94% test coverage.")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 470, "Vanguard Labs — Software Engineering Intern (Summer 2021)")
    c.setFont("Helvetica", 10)
    c.drawString(60, 454, "• Built automated ETL pipelines using Python and Pandas, reducing manual reports by 15 hours/week.")
    c.drawString(60, 440, "• Resolved 32 customer-reported frontend bugs across React dashboard components.")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 410, "FEATURED PROJECTS")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 394, "Distributed Task Scheduler (Go, Redis, Docker)")
    c.setFont("Helvetica", 10)
    c.drawString(60, 378, "• Implemented Raft consensus protocol supporting 10,000 tasks/second with zero data loss.")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 354, "AI Code Review Assistant (Python, FastAPI, Gemini API)")
    c.setFont("Helvetica", 10)
    c.drawString(60, 338, "• Developed GitHub bot that scans pull requests for security vulnerabilities with 88% accuracy.")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 308, "EDUCATION")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 292, "University of California, Berkeley — B.S. in Computer Science (2018 - 2022)")
    c.setFont("Helvetica", 10)
    c.drawString(50, 276, "GPA: 3.82 / 4.0 | Dean's Honors List | Coursework: Data Structures, Algorithms, Distributed Systems")

    c.save()
    print(f"[OK] Generated: {pdf_path.name}")


def create_weak_marketing_pdf():
    """Creates a weak resume lacking metrics, filled with passive voice and buzzwords."""
    pdf_path = output_dir / "resume_weak_marketing.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "TAYLOR REED")
    c.setFont("Helvetica", 9)
    c.drawString(50, 735, "Austin, TX | taylor.reed@email.com | (555) 948-2019")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 705, "PROFILE")
    c.setFont("Helvetica", 10)
    c.drawString(50, 688, "Results-oriented team player with a passion for excellence in fast-paced marketing environments.")
    c.drawString(50, 674, "Proven track record of thinking outside the box to drive brand synergy.")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 645, "SKILLS")
    c.setFont("Helvetica", 10)
    c.drawString(50, 628, "Marketing, Social Media, Communication, Microsoft Office, Problem Solving, Leadership")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 600, "WORK EXPERIENCE")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 583, "Marketing Coordinator — BrightWave Media (2022 - 2024)")
    c.setFont("Helvetica", 10)
    c.drawString(60, 567, "• Was responsible for helping with social media posts and scheduling content.")
    c.drawString(60, 553, "• Worked on email newsletters that were sent out to customers.")
    c.drawString(60, 539, "• Attended weekly team meetings and brainstormed creative campaign ideas.")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 515, "Marketing Assistant — Summit Agency (2021 - 2022)")
    c.setFont("Helvetica", 10)
    c.drawString(60, 499, "• Assisted senior staff members with various promotional marketing duties.")
    c.drawString(60, 485, "• Helped organize company promotional webinars and logged attendee information.")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 455, "EDUCATION")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 439, "Texas State University — B.A. in Communications (2017 - 2021)")

    c.save()
    print(f"[OK] Generated: {pdf_path.name}")


def create_image_resume():
    """Creates a high resolution PNG image resume."""
    img_path = output_dir / "resume_screenshot.png"
    width, height = 800, 1050
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    lines = [
        "JORDAN CHEN",
        "Data Analyst | New York, NY | jordan.chen@email.com",
        "--------------------------------------------------------------------------------",
        "PROFESSIONAL EXPERIENCE",
        "Senior Analytics Associate - Retail Insights Inc (2021 - Present)",
        "- Analyzed customer transaction data across 1.2M accounts using SQL and Python.",
        "- Built interactive Tableau dashboards for executive leadership, increasing sales visibility by 40%.",
        "- Developed automated churn prediction model achieving 82% precision score.",
        "",
        "Junior Data Analyst - Metropolitan Media (2019 - 2021)",
        "- Cleaned and transformed 500GB+ marketing campaign datasets using Python and pandas.",
        "- Automated weekly financial reports, saving team 8 hours of manual data entry every Monday.",
        "",
        "TECHNICAL SKILLS",
        "Languages: Python, SQL, R",
        "Tools: Tableau, Power BI, Excel, Snowflake, dbt, Git, Docker",
        "",
        "EDUCATION",
        "New York University - B.S. in Applied Statistics, 2019"
    ]

    y = 40
    for line in lines:
        draw.text((40, y), line, fill=(20, 20, 20))
        y += 24

    img.save(img_path)
    print(f"[OK] Generated: {img_path.name}")
    return img_path


def create_scanned_pdf(image_path: Path):
    """Creates an image-only PDF (no searchable text layer) to test OCR fallback."""
    pdf_path = output_dir / "resume_scanned_flattened.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)

    rect = pymupdf.Rect(0, 0, 612, 792)
    page.insert_image(rect, filename=str(image_path))

    doc.save(pdf_path)
    doc.close()
    print(f"[OK] Generated: {pdf_path.name}")


if __name__ == "__main__":
    create_strong_tech_pdf()
    create_weak_marketing_pdf()
    img_file = create_image_resume()
    create_scanned_pdf(img_file)
    print("All sample resumes generated successfully.")
