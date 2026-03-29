from marshmallow import Schema, fields, validate, ValidationError
import re

def validate_phone(phone):
    if phone and not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', phone):
        raise ValidationError('Invalid phone number format')

def validate_password(password):
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one number')

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate_password)
    role = fields.Str(required=True, validate=validate.OneOf(['admin', 'doctor', 'nurse', 'receptionist']))

class PatientSchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    date_of_birth = fields.Date(required=True)
    gender = fields.Str(required=True, validate=validate.OneOf(['Male', 'Female', 'Other']))
    phone = fields.Str(validate=validate_phone, allow_none=True)
    email = fields.Email(allow_none=True)
    address = fields.Str(allow_none=True)
    medical_history = fields.Str(allow_none=True)

class DoctorSchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    specialty = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    phone = fields.Str(validate=validate_phone, allow_none=True)
    email = fields.Email(allow_none=True)
    availability = fields.Str(allow_none=True)

class AppointmentSchema(Schema):
    patient_id = fields.Int(required=True)
    doctor_id = fields.Int(required=True)
    appointment_date = fields.DateTime(required=True)
    status = fields.Str(validate=validate.OneOf(['scheduled', 'completed', 'cancelled']), missing='scheduled')
    notes = fields.Str(allow_none=True)

class MedicalRecordSchema(Schema):
    patient_id = fields.Int(required=True)
    doctor_id = fields.Int(required=True)
    diagnosis = fields.Str(allow_none=True)
    prescription = fields.Str(allow_none=True)
    doctor_notes = fields.Str(allow_none=True)