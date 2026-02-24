from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from naac_app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="Staff")  # Admin / Staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def ensure_default_admin():
        # Creates admin/admin123 if no users exist
        if User.query.count() == 0:
            admin = User(username="admin", role="Admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    document_title = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(80), nullable=True)

    department = db.Column(db.String(120), nullable=True)
    academic_year = db.Column(db.String(20), nullable=True)

    filename = db.Column(db.String(255), nullable=False)
    original_path = db.Column(db.String(500), nullable=False)

    extracted_text = db.Column(db.Text, nullable=True)

    predicted_criterion = db.Column(db.String(10), nullable=True)  # C1..C7
    predicted_metric = db.Column(db.String(255), nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)

    validation_status = db.Column(db.String(20), nullable=True)  # VALID/PARTIAL/FAIL
    missing_items = db.Column(db.Text, nullable=True)            # comma-separated
    matched_keywords = db.Column(db.Text, nullable=True)         # comma-separated

    uploaded_by = db.Column(db.String(80), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def missing_list(self):
        if not self.missing_items:
            return []
        return [x.strip() for x in self.missing_items.split(",") if x.strip()]

    def matched_list(self):
        if not self.matched_keywords:
            return []
        return [x.strip() for x in self.matched_keywords.split(",") if x.strip()]