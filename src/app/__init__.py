from flask import Flask
from src.app.config import Config

from src.app.auth.routes import auth_bp
from src.app.main.routes import main_bp

from src.app.extensions import db, login_manager, csrf, model_registry

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    login_manager.init_app(app)
    csrf.init_app(app)
    db.init_app(app)

    model_registry.init_app(app)
    app.extensions["model_registry"] = model_registry

    from src.app import models
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()


    return app