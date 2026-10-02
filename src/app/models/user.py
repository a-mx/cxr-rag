from datetime import datetime, timezone

from flask_login import UserMixin
from flask import current_app
from src.app.extensions import db, login_manager
from passlib.hash import argon2

def _get_hasher():

    return argon2.using(
            time_cost=current_app.config.get("ARGON2_TIME_COST"),
            rounds=current_app.config.get("ARGON2_ROUNDS"),
            memory_cost=current_app.config.get("ARGON2_MEMORY_COST"),
            parallelism=current_app.config.get("ARGON2_PARALLELISM"),
            hash_len=current_app.config.get("ARGON2_HASH_LEN"),
            salt_len=current_app.config.get("ARGON2_SALT_LEN"),
        )


class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = db.Column(db.String(256), nullable=False)

    role = db.Column(
        db.String(20),
        default="user",
        nullable=False,
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    last_login = db.Column(db.DateTime, nullable=True)

    analyses = db.relationship(
        "Analysis",
        backref="author",
        lazy="dynamic",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    audit_logs = db.relationship(
        "AuditLog",
        backref="user",
        lazy="dynamic",
        passive_deletes=True,
    )


    def set_password(self, password: str) -> None:
        self.password_hash = _get_hasher().hash(password)

    @staticmethod
    def check_password(stored_hash: str, password: str) -> bool:
        try:
            _get_hasher().verify(password, stored_hash)
            return True
        except Exception as e:
            print(e)
            return False
    
    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def analysis_count(self) -> int:
        return self.analyses.count()

    def __repr__(self) -> str:
        return f"<User {self.username} role={self.role}>"

@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))