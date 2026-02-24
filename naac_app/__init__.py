import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Ensure instance/ and uploads/ exist
    os.makedirs(os.path.join(app.root_path, "..", "instance"), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    # Blueprints
    from naac_app.auth.routes import auth_bp
    from naac_app.documents.routes import docs_bp
    from naac_app.dashboard.routes import dash_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(dash_bp)

    # Create DB tables + seed admin
    with app.app_context():
        from naac_app.models import User
        db.create_all()
        User.ensure_default_admin()

    return app