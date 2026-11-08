from datetime import datetime, timezone
from src.app.extensions import db

class ReportRevision(db.Model):
    __tablename__ = "report_revisions"

    id = db.Column(db.Integer, primary_key=True)

    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    author_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    revision_number = db.Column(db.Integer, nullable=False)

    content = db.Column(db.Text, nullable=False)

    source = db.Column(
        db.String(20),
        nullable=False,
        default="manual",
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    analysis = db.relationship(
        "Analysis",
        back_populates="revisions",
    )

    author = db.relationship(
        "User",
        backref="report_revisions",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "analysis_id",
            "revision_number",
            name="uq_report_revision_number",
        ),
    )

    def __repr__(self):
        return (
            f"<ReportRevision analysis_id={self.analysis_id} "
            f"version={self.revision_number}>"
        )