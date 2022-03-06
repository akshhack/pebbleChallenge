from api.core import Mixin
from .base import db


# Note that we use sqlite for our tests, so you can't use Postgres Arrays
class Quote(Mixin, db.Model):
    """Quote Table."""

    __tablename__ = "quote"

    id = db.Column(db.Integer, unique=True, primary_key=True)
    quote = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    user = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )

    def __init__(self, quote, date):
        self.quote = quote
        self.date = date

    def __repr__(self):
        return f"<Quote {self.quote}>"
