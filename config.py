import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "app.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB

    ALLOWED_EXTENSIONS = {"pdf", "docx", "png", "jpg", "jpeg"}

    # OCR optional (for scanned images)
    ENABLE_OCR = True

    # NOTE: For OCR to work, you must install Tesseract in OS.
    # Windows: install tesseract and set path below if needed:
    TESSERACT_CMD = os.environ.get("TESSERACT_CMD", "")