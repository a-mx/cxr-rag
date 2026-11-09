from src.app.extensions import db


class BoundingBox(db.Model):
    __tablename__ = "bounding_box"

    id = db.Column(db.Integer, primary_key=True)

    analysis_id = db.Column(
            db.Integer,
            db.ForeignKey("analyses.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )

    analysis = db.relationship("Analysis", back_populates="bounding_boxes")
    
    x0 = db.Column(db.Float, nullable=False)
    x1 = db.Column(db.Float, nullable=False)
    y0 = db.Column(db.Float, nullable=False)
    y1 = db.Column(db.Float, nullable=False)

    @property
    def to_list(self) -> list[float]:
        return [self.x0, self.y0, self.x1, self.y1]
    
    def __repr__(self) -> str:
        return (
            f"<Analysis id={self.id}"
            "x0={self.x0}"
            "x1={self.x1}"
            "y0={self.y0}"
            "y1={self.y1}>"
        )