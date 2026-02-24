import os
import re
from werkzeug.utils import secure_filename
from flask import current_app

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from PIL import Image

import pytesseract

def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]

def save_upload(file_storage) -> tuple[str, str]:
    """
    Returns (safe_filename, absolute_path)
    """
    filename = secure_filename(file_storage.filename)
    abs_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

    # avoid overwrite: add suffix
    if os.path.exists(abs_path):
        base, ext = os.path.splitext(filename)
        i = 1
        while True:
            new_name = f"{base}_{i}{ext}"
            new_path = os.path.join(current_app.config["UPLOAD_FOLDER"], new_name)
            if not os.path.exists(new_path):
                filename, abs_path = new_name, new_path
                break
            i += 1

    file_storage.save(abs_path)
    return filename, abs_path

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_text_from_pdf(path: str) -> str:
    text_parts = []
    with fitz.open(path) as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))
    return clean_text("\n".join(text_parts))

def extract_text_from_docx(path: str) -> str:
    doc = DocxDocument(path)
    paras = [p.text for p in doc.paragraphs if p.text.strip()]
    return clean_text("\n".join(paras))

def extract_text_from_image(path: str) -> str:
    if current_app.config.get("TESSERACT_CMD"):
        pytesseract.pytesseract.tesseract_cmd = current_app.config["TESSERACT_CMD"]
    img = Image.open(path)
    text = pytesseract.image_to_string(img)
    return clean_text(text)

def extract_text_by_extension(path: str) -> str:
    ext = path.rsplit(".", 1)[1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(path)
    if ext == "docx":
        return extract_text_from_docx(path)
    if ext in {"png", "jpg", "jpeg"}:
        if current_app.config.get("ENABLE_OCR", True):
            return extract_text_from_image(path)
        return ""
    return ""

def keyword_score(text_lower: str, keywords: list[str]) -> tuple[int, list[str]]:
    matched = []
    score = 0
    for kw in keywords:
        k = kw.lower()
        if k in text_lower:
            score += 1
            matched.append(kw)
    return score, matched