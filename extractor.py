"""
Resumely AI — Resume Text Extraction Pipeline
Supports PyMuPDF direct text extraction and Tesseract OCR for scanned PDFs & images.
Files are cleaned up immediately following extraction for strict user privacy.
"""

import io
import os
import uuid
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import pymupdf  # Modern PyMuPDF API
import pytesseract
from PIL import Image

from config import TESSERACT_PATH, UPLOAD_DIR, MAX_FILE_SIZE_BYTES

# Setup logging (Note: Resume text content is NEVER logged)
logger = logging.getLogger("resumely.extractor")
logging.basicConfig(level=logging.INFO)

# Configure Tesseract binary path
if TESSERACT_PATH and os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    TESSERACT_AVAILABLE = True
else:
    TESSERACT_AVAILABLE = False
    logger.warning(
        f"Tesseract OCR executable not found at '{TESSERACT_PATH}'. "
        "Scanned documents and image uploads will be limited."
    )


class ExtractionError(Exception):
    """Raised when text extraction fails due to invalid/corrupted files."""
    pass


class EmptyExtractionError(ExtractionError):
    """Raised when extraction completes but yields no readable text."""
    pass


@dataclass
class ExtractionResult:
    filename: str
    method: str
    page_count: int
    char_count: int
    word_count: int
    text: str
    is_ocr: bool

    def to_dict(self) -> dict:
        return {
            "filename": self.filename,
            "method": self.method,
            "page_count": self.page_count,
            "char_count": self.char_count,
            "word_count": self.word_count,
            "text": self.text,
            "is_ocr": self.is_ocr
        }


def clean_extracted_text(raw_text: str) -> str:
    """Cleans up raw text, normalizing line breaks and excess whitespace."""
    if not raw_text:
        return ""
    lines = [line.strip() for line in raw_text.splitlines()]
    # Remove excessive blank lines
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        if not line:
            if not prev_blank:
                cleaned_lines.append("")
                prev_blank = True
        else:
            cleaned_lines.append(line)
            prev_blank = False
    return "\n".join(cleaned_lines).strip()


def extract_from_pdf(file_path: Path, filename: str) -> ExtractionResult:
    """
    Extracts text from a PDF file using PyMuPDF.
    If the text layer is empty or sparse (< 50 characters total),
    automatically renders pages to images and runs Tesseract OCR.
    """
    try:
        doc = pymupdf.open(file_path)
    except Exception as e:
        raise ExtractionError(f"Failed to parse PDF document: {e}")

    page_count = len(doc)
    if page_count == 0:
        doc.close()
        raise EmptyExtractionError("The uploaded PDF has 0 pages.")

    # 1. Attempt direct text extraction
    text_chunks = []
    for page_idx in range(page_count):
        page = doc[page_idx]
        text_chunks.append(page.get_text("text").strip())

    combined_text = "\n\n".join(chunk for chunk in text_chunks if chunk)
    cleaned_direct = clean_extracted_text(combined_text)

    # Threshold for scanned document: less than 50 characters total or under 15 chars/page
    is_scanned = len(cleaned_direct) < 50 or (len(cleaned_direct) / page_count < 15)

    if not is_scanned:
        doc.close()
        words = len(cleaned_direct.split())
        return ExtractionResult(
            filename=filename,
            method="PyMuPDF (Direct Text)",
            page_count=page_count,
            char_count=len(cleaned_direct),
            word_count=words,
            text=cleaned_direct,
            is_ocr=False
        )

    # 2. Direct text was insufficient; fall back to PyMuPDF rendering + Tesseract OCR
    if not TESSERACT_AVAILABLE:
        doc.close()
        if cleaned_direct:
            words = len(cleaned_direct.split())
            return ExtractionResult(
                filename=filename,
                method="PyMuPDF (Direct Text - OCR Unavailable)",
                page_count=page_count,
                char_count=len(cleaned_direct),
                word_count=words,
                text=cleaned_direct,
                is_ocr=False
            )
        raise ExtractionError(
            "The PDF appears to be a scanned image, but Tesseract OCR is not configured on the server."
        )

    logger.info(f"Falling back to Tesseract OCR for scanned PDF ({page_count} pages)")
    ocr_chunks = []
    try:
        for page_idx in range(page_count):
            page = doc[page_idx]
            # Render page to 200 DPI pixmap for optimal OCR quality vs speed
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            page_ocr_text = pytesseract.image_to_string(img)
            if page_ocr_text.strip():
                ocr_chunks.append(page_ocr_text.strip())
    except Exception as e:
        doc.close()
        raise ExtractionError(f"Tesseract OCR failed during PDF page processing: {e}")
    finally:
        doc.close()

    cleaned_ocr = clean_extracted_text("\n\n".join(ocr_chunks))
    if not cleaned_ocr:
        raise EmptyExtractionError("OCR could not recognize any legible text from the scanned PDF.")

    words = len(cleaned_ocr.split())
    return ExtractionResult(
        filename=filename,
        method="PyMuPDF + Tesseract OCR (Scanned PDF)",
        page_count=page_count,
        char_count=len(cleaned_ocr),
        word_count=words,
        text=cleaned_ocr,
        is_ocr=True
    )


def extract_from_image(file_path: Path, filename: str) -> ExtractionResult:
    """
    Extracts text from an image (PNG, JPG, JPEG) using Tesseract OCR.
    """
    if not TESSERACT_AVAILABLE:
        raise ExtractionError(
            "Tesseract OCR is not configured on the server to process image files."
        )

    try:
        with Image.open(file_path) as img:
            # Convert to RGB if needed (handles RGBA, Palette mode, etc.)
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            raw_text = pytesseract.image_to_string(img)
    except Exception as e:
        raise ExtractionError(f"Failed to process image file: {e}")

    cleaned = clean_extracted_text(raw_text)
    if not cleaned:
        raise EmptyExtractionError("No legible text could be recognized in the uploaded image.")

    words = len(cleaned.split())
    return ExtractionResult(
        filename=filename,
        method="Tesseract OCR (Image)",
        page_count=1,
        char_count=len(cleaned),
        word_count=words,
        text=cleaned,
        is_ocr=True
    )


def process_resume_upload(
    file_bytes: bytes,
    original_filename: str
) -> ExtractionResult:
    """
    Saves the upload temporarily, runs extraction, and immediately purges
    the temporary file from disk. Enforces privacy and clean resource cleanup.
    """
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ExtractionError("File size exceeds the 5MB maximum limit.")

    ext = Path(original_filename).suffix.lower()
    if ext not in (".pdf", ".png", ".jpg", ".jpeg"):
        raise ExtractionError(f"Unsupported file format '{ext}'. Allowed: .pdf, .png, .jpg, .jpeg")

    temp_id = f"{uuid.uuid4().hex}_{Path(original_filename).name}"
    temp_path = UPLOAD_DIR / temp_id

    try:
        # Save temporary file
        temp_path.write_bytes(file_bytes)

        if ext == ".pdf":
            result = extract_from_pdf(temp_path, original_filename)
        else:
            result = extract_from_image(temp_path, original_filename)

        logger.info(
            f"Successfully extracted {result.char_count} chars ({result.word_count} words) "
            f"from '{original_filename}' via {result.method}"
        )
        return result

    finally:
        # Enforce immediate privacy cleanup: delete uploaded file
        if temp_path.exists():
            try:
                temp_path.unlink()
                logger.info(f"Temporary file {temp_id} purged from disk.")
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_path}: {e}")

