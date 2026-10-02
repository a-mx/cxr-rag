from flask import Flask
from src.app.config import Config
from flask_sqlalchemy import SQLAlchemy

from src.app.auth.routes import auth_bp
from src.app.main.routes import main_bp

from src.app.extensions import db, login_manager, csrf

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    login_manager.init_app(app)
    csrf.init_app(app)
    db.init_app(app)

    from src.app import models
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()


    return app