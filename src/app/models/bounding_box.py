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

    label = db.Column(db.String(128), nullable=False)
    #[y0, x0, y1, x1]

    y0 = db.Column(db.Float, nullable=False)
    x0 = db.Column(db.Float, nullable=False)
    y1 = db.Column(db.Float, nullable=False)
    x1 = db.Column(db.Float, nullable=False)

    @property
    def to_list(self) -> list[float]:
        return [self.y0, self.x0, self.y1, self.x1]
    
    def __repr__(self):
        return (
            f"<BoundingBox id={self.id} "
            f"analysis_id={self.analysis_id} "
            f"y0={self.y0} x0={self.x0} "
            f"y1={self.y1} x1={self.x1}>"
        )