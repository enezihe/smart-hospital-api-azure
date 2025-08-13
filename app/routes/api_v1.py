# app/routes/api_v1.py
from flask import Blueprint, request
from datetime import datetime
from uuid import uuid4
from marshmallow import ValidationError
from ..extensions import db
from ..config import Config
from ..models import Patient, Device, Vital, IdempotencyKey
from ..schemas import VitalInSchema, DeviceRegisterSchema

api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

def uid(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"

def error(code: str, http: int, message: str, details=None):
    payload = {"code": code, "message": message}
    if details is not None:
        payload["details"] = details
    return payload, http

def require_device_api_key():
    supplied = request.headers.get("X-API-Key")
    if not supplied:
        return False, error("missing_api_key", 401, "X-API-Key header required")
    if supplied == Config.DEVICE_MASTER_KEY:
        return True, None
    if Device.query.filter_by(api_key=supplied).first():
        return True, None
    return False, error("invalid_api_key", 401, "Invalid API key")

def parse_dt(s):
    if not s:
        return None
    try:
        s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except Exception:
        raise ValueError(f"Invalid datetime: {s}")

def record_idempotency(device_id, idem_key):
    if not idem_key:
        return True
    combined = f"{device_id}:{idem_key}"
    if IdempotencyKey.query.filter_by(key=combined).first():
        return False
    db.session.add(IdempotencyKey(device_id=device_id, key=combined))
    db.session.commit()
    return True

@api_v1_bp.post("/devices/register")
def register_device():
    ok, resp = require_device_api_key()
    if not ok:
        return resp
    try:
        body = DeviceRegisterSchema().load(request.get_json())
    except ValidationError as e:
        return error("validation_error", 400, "Invalid payload", e.messages)
    patient = Patient.query.get(body["patient_id"])
    if not patient:
        patient = Patient(id=body["patient_id"], name=f"Patient {body['patient_id']}")
        db.session.add(patient)
    existing = Device.query.get(body["device_id"])
    if existing:
        return {"device_id": existing.id, "api_key": existing.api_key, "status": "already_registered"}, 200
    api_key = uid("key")
    device = Device(id=body["device_id"], type=body["type"], patient_id=body["patient_id"], api_key=api_key)
    db.session.add(device)
    db.session.commit()
    return {"device_id": device.id, "api_key": api_key, "status": "registered"}, 201

@api_v1_bp.post("/patients/<patient_id>/vitals")
def post_vitals(patient_id):
    ok, resp = require_device_api_key()
    if not ok:
        return resp
    try:
        data = VitalInSchema().load(request.get_json())
    except ValidationError as e:
        return error("validation_error", 400, "Invalid payload", e.messages)
    idem = request.headers.get("Idempotency-Key") or (request.json or {}).get("idempotency_key")
    if not record_idempotency(data["device_id"], idem):
        return {"status": "duplicate_ignored"}, 200
    v = Vital(
        id=uid("v"),
        patient_id=patient_id,
        timestamp=data["timestamp"],
        heart_rate=data.get("heart_rate"),
        bp_systolic=(data.get("bp") or {}).get("systolic"),
        bp_diastolic=(data.get("bp") or {}).get("diastolic"),
        spo2=data.get("spo2"),
        temp=data.get("temp"),
        device_id=data["device_id"],
    )
    db.session.add(v)
    db.session.commit()
    return {"vital_id": v.id, "status": "stored"}, 201

@api_v1_bp.get("/patients/<patient_id>/latest")
def get_latest(patient_id):
    v = Vital.query.filter_by(patient_id=patient_id).order_by(Vital.timestamp.desc()).first()
    if not v:
        return error("not_found", 404, "No readings for patient")
    bp = None
    if v.bp_systolic is not None and v.bp_diastolic is not None:
        bp = {"systolic": v.bp_systolic, "diastolic": v.bp_diastolic}
    return {
        "timestamp": v.timestamp.isoformat() + "Z",
        "heart_rate": v.heart_rate,
        "bp": bp,
        "spo2": v.spo2,
        "temp": v.temp,
        "device_id": v.device_id
    }, 200

@api_v1_bp.get("/patients/<patient_id>/history")
def get_history(patient_id):
    try:
        dt_from = parse_dt(request.args.get("from")) if request.args.get("from") else None
        dt_to   = parse_dt(request.args.get("to")) if request.args.get("to") else None
        page = max(int(request.args.get("page", 1)), 1)
        size = min(max(int(request.args.get("page_size", 100)), 1), 500)
        q = Vital.query.filter_by(patient_id=patient_id)
        if dt_from: q = q.filter(Vital.timestamp >= dt_from)
        if dt_to:   q = q.filter(Vital.timestamp <= dt_to)
        total = q.count()
        q = q.order_by(Vital.timestamp.desc()).offset((page - 1) * size).limit(size)
        items = []
        for v in q.all():
            bp = None
            if v.bp_systolic is not None and v.bp_diastolic is not None:
                bp = {"systolic": v.bp_systolic, "diastolic": v.bp_diastolic}
            items.append({
                "timestamp": v.timestamp.isoformat() + "Z",
                "heart_rate": v.heart_rate,
                "bp": bp,
                "spo2": v.spo2,
                "temp": v.temp,
                "device_id": v.device_id
            })
        return {"results": items, "page": page, "page_size": size, "total": total}, 200
    except Exception as e:
        return error("bad_request", 400, "Invalid query parameters", str(e))
