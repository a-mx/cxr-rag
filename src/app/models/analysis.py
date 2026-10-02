from datetime import datetime, timezone

from src.app.extensions import db


class Analysis(db.Model):
    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_filename = db.Column(db.String(255), nullable=False)
    user_prompt = db.Column(db.Text, nullable=True)

    generated_report = db.Column(db.Text, nullable=False)

    top_k = db.Column(db.Integer, nullable=False, default=5)
    retrieval_strategy = db.Column(
        db.String(50),
        nullable=False,
        default="image_only",
    )

    chexbert_f1 = db.Column(db.Float, nullable=True)
    radgraph_f1 = db.Column(db.Float, nullable=True)
    rouge_l = db.Column(db.Float, nullable=True)

    inference_time_ms = db.Column(db.Integer, nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)

    retrieved_cases = db.Column(db.JSON, nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    @property
    def short_report(self) -> str:
        if not self.generated_report:
            return ""
        text = self.generated_report.strip().replace("\n", " ")
        return text[:150] + "..." if len(text) > 150 else text

    @property
    def case_count(self) -> int:
        return len(self.retrieved_cases) if self.retrieved_cases else 0

    @property
    def has_metrics(self) -> bool:
        return any([
            self.chexbert_f1 is not None,
            self.radgraph_f1 is not None,
            self.rouge_l is not None,
        ])

    def __repr__(self) -> str:
        return (
            f"<Analysis id={self.id} user_id={self.user_id} "
            f"strategy={self.retrieval_strategy}>"
        )