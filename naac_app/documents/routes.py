from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory, abort
from sqlalchemy import or_

from naac_app.auth.routes import login_required
from naac_app import db
from naac_app.models import Document
from naac_app.utils import allowed_file, save_upload, extract_text_by_extension, keyword_score
from naac_app.naac_rules import NAAC_MAPPING

docs_bp = Blueprint("docs", __name__, url_prefix="/documents")

def classify_and_validate(text: str):
    """
    Rule-based classification + validation:
    - Score each criterion/metric based on required+optional keyword matches.
    - Choose best metric overall.
    - Confidence = normalized score.
    - Validation based on required keyword coverage.
    """
    text_lower = (text or "").lower()
    best = {"criterion": None, "metric": None, "score": -1, "matched": [], "required_total": 0, "required_matched": 0}

    for criterion, metrics in NAAC_MAPPING.items():
        for metric_name, rules in metrics.items():
            req = rules.get("required", [])
            opt = rules.get("optional", [])

            req_score, req_matched = keyword_score(text_lower, req)
            opt_score, opt_matched = keyword_score(text_lower, opt)

            # Weight required keywords higher
            score = (req_score * 3) + opt_score
            matched = req_matched + opt_matched

            if score > best["score"]:
                best = {
                    "criterion": criterion,
                    "metric": metric_name,
                    "score": score,
                    "matched": matched,
                    "required_total": len(req),
                    "required_matched": req_score,
                }

    # If no text or very low match
    if not text or best["score"] <= 0:
        return (None, None, 0.0, "FAIL", ["No relevant NAAC keywords found"], [])

    # Confidence heuristic
    max_possible = (best["required_total"] * 3) + 5  # rough normalization
    confidence = min(1.0, best["score"] / max_possible) if max_possible > 0 else 0.2

    # Validation based on required coverage
    req_total = best["required_total"]
    req_matched = best["required_matched"]
    missing = []

    # Find missing required items
    req_list = NAAC_MAPPING[best["criterion"]][best["metric"]].get("required", [])
    for kw in req_list:
        if kw.lower() not in text_lower:
            missing.append(kw)

    if req_total == 0:
        status = "PARTIAL"
    else:
        ratio = req_matched / req_total
        if ratio >= 0.8:
            status = "VALID"
        elif ratio >= 0.4:
            status = "PARTIAL"
        else:
            status = "FAIL"

    return (best["criterion"], best["metric"], float(confidence), status, missing, best["matched"])

@docs_bp.route("/", methods=["GET"])
@login_required
def list_documents():
    q = (request.args.get("q") or "").strip()
    year = (request.args.get("year") or "").strip()
    dept = (request.args.get("dept") or "").strip()
    criterion = (request.args.get("criterion") or "").strip()
    metric = (request.args.get("metric") or "").strip()
    status = (request.args.get("status") or "").strip()

    query = Document.query

    if year:
        query = query.filter(Document.academic_year == year)
    if dept:
        query = query.filter(Document.department == dept)
    if criterion:
        query = query.filter(Document.predicted_criterion == criterion)
    if metric:
        query = query.filter(Document.predicted_metric == metric)
    if status:
        query = query.filter(Document.validation_status == status)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Document.document_title.ilike(like),
                Document.department.ilike(like),
                Document.academic_year.ilike(like),
                Document.extracted_text.ilike(like),
                Document.predicted_metric.ilike(like),
            )
        )

    docs = query.order_by(Document.uploaded_at.desc()).all()

    # For filter dropdowns
    years = [r[0] for r in db.session.query(Document.academic_year).distinct().all() if r[0]]
    depts = [r[0] for r in db.session.query(Document.department).distinct().all() if r[0]]

    return render_template(
        "documents.html",
        docs=docs,
        q=q, year=year, dept=dept, criterion=criterion, metric=metric, status=status,
        years=sorted(set(years)),
        depts=sorted(set(depts)),
        criteria=list(NAAC_MAPPING.keys()),
        statuses=["VALID", "PARTIAL", "FAIL"]
    )

@docs_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            flash("Please choose a file.", "warning")
            return redirect(url_for("docs.upload"))

        if not allowed_file(file.filename):
            flash("File type not allowed. Use PDF/DOCX/PNG/JPG.", "danger")
            return redirect(url_for("docs.upload"))

        document_title = (request.form.get("document_title") or "").strip()
        document_type = (request.form.get("document_type") or "").strip()
        department = (request.form.get("department") or "").strip()
        academic_year = (request.form.get("academic_year") or "").strip()

        if not document_title:
            flash("Document title is required.", "warning")
            return redirect(url_for("docs.upload"))

        filename, abs_path = save_upload(file)

        extracted_text = extract_text_by_extension(abs_path)
        criterion, metric, conf, vstatus, missing, matched = classify_and_validate(extracted_text)

        doc = Document(
            document_title=document_title,
            document_type=document_type,
            department=department,
            academic_year=academic_year,
            filename=filename,
            original_path=abs_path,
            extracted_text=extracted_text,

            predicted_criterion=criterion,
            predicted_metric=metric,
            confidence_score=conf,

            validation_status=vstatus,
            missing_items=", ".join(missing) if missing else "",
            matched_keywords=", ".join(matched) if matched else "",

            uploaded_by=session.get("username", "")
        )

        db.session.add(doc)
        db.session.commit()

        flash("Document uploaded and processed successfully.", "success")
        return redirect(url_for("docs.document_detail", doc_id=doc.id))

    return render_template("upload.html", criteria=list(NAAC_MAPPING.keys()))

@docs_bp.route("/<int:doc_id>", methods=["GET"])
@login_required
def document_detail(doc_id: int):
    doc = Document.query.get_or_404(doc_id)
    return render_template("document_detail.html", doc=doc)

@docs_bp.route("/download/<int:doc_id>", methods=["GET"])
@login_required
def download(doc_id: int):
    doc = Document.query.get_or_404(doc_id)
    directory = doc.original_path.rsplit("/", 1)[0].rsplit("\\", 1)[0]
    return send_from_directory(directory, doc.filename, as_attachment=True)

@docs_bp.route("/delete/<int:doc_id>", methods=["POST"])
@login_required
def delete(doc_id: int):
    # Admin only
    if session.get("role") != "Admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("docs.document_detail", doc_id=doc_id))

    doc = Document.query.get_or_404(doc_id)
    db.session.delete(doc)
    db.session.commit()
    flash("Document deleted.", "info")
    return redirect(url_for("docs.list_documents"))