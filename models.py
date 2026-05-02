from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Todo(db.Model):
    SNo          = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(200), nullable=False)
    desc         = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    priority     = db.Column(db.String(20), default='Medium')
    status       = db.Column(db.String(20), default='Pending')
    due_date     = db.Column(db.Date, nullable=True)