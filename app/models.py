# app/models.py
from datetime import datetime
from .extensions import db

class Patient(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    dob = db.Column(db.String)
    assigned_doctor_id = db.Column(db.String)

class Device(db.Model):
    id = db.Column(db.String, primary_key=True)
    type = db.Column(db.String, nullable=False)
    patient_id = db.Column(db.String, db.ForeignKey("patient.id"))
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String, default="active")
    api_key = db.Column(db.String, nullable=False)

class Vital(db.Model):
    id = db.Column(db.String, primary_key=True)
    patient_id = db.Column(db.String, db.ForeignKey("patient.id"), index=True)
    timestamp = db.Column(db.DateTime, index=True)
    heart_rate = db.Column(db.Integer)
    bp_systolic = db.Column(db.Integer)
    bp_diastolic = db.Column(db.Integer)
    spo2 = db.Column(db.Integer)
    temp = db.Column(db.Float)
    device_id = db.Column(db.String, db.ForeignKey("device.id"))

class Alert(db.Model):
    id = db.Column(db.String, primary_key=True)
    patient_id = db.Column(db.String, index=True)
    type = db.Column(db.String)
    value = db.Column(db.Float)
    threshold = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String, default="NEW")

class IdempotencyKey(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String, index=True, nullable=False)
    key = db.Column(db.String, unique=True, index=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

