from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from src.app.model_registry import ModelRegistry

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
model_registry = ModelRegistry()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "You need to be logged in to see this page."
login_manager.login_message_category = "warning"
login_manager.session_protection = "strong"

