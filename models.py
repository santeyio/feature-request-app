import uuid

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Feature(db.Model):

    __tablename__ = 'feature'

    id = db.Column(db.String, primary_key=True, default=str(uuid.uuid4()))
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    client = db.Column(db.String, nullable=False)
    client_priority = db.Column(db.Integer, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    product_area = db.Column(db.String, nullable=False)
