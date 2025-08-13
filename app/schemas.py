# app/schemas.py
from marshmallow import Schema, fields, validate

class BPField(Schema):
    systolic = fields.Integer(required=True, validate=validate.Range(min=0, max=300))
    diastolic = fields.Integer(required=True, validate=validate.Range(min=0, max=200))

class VitalInSchema(Schema):
    timestamp = fields.DateTime(required=True)
    heart_rate = fields.Integer(allow_none=True)
    bp = fields.Nested(BPField, required=False)
    spo2 = fields.Integer(allow_none=True)
    temp = fields.Float(allow_none=True)
    device_id = fields.String(required=True)

class DeviceRegisterSchema(Schema):
    device_id = fields.String(required=True)
    type = fields.String(required=True, validate=validate.OneOf(["hr","bp","spo2","temp","multi"]))
    patient_id = fields.String(required=True)
