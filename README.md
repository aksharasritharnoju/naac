# NAAC AI Document Manager (Flask)

## Features

- Login (Admin/Staff)
- Upload PDF/DOCX/Images
- Extract text (PDF/DOCX + optional OCR for images)
- NAAC Classification (rule-based keyword scoring)
- NAAC Validation (VALID/PARTIAL/FAIL + missing items)
- Evidence search/filter + download
- Dashboard + readiness per criterion

## Setup

```bash
cd naac_ai_app
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/mac:
source venv/bin/activate

pip install -r requirements.txt
python app.py
```
