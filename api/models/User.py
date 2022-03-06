from api.core import Mixin
from .base import db

from datetime import datetime


class User(Mixin, db.Model):
    """User Table."""

    __tablename__ = "user"

    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    dob = db.Column(db.DateTime, nullable=False)
    zip = db.Column(db.Integer, nullable=False)
    quotes = db.relationship("Quote", backref="quotes")

    def __init__(self, name: str, dob: str, zip: int):
        self.name = name
        self.dob = dob
        self.zip = zip

    def __repr__(self):
        return f"<Person {self.name}>"
