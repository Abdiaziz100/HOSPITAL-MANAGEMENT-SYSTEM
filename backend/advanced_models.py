from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Additional Professional Models for Billing & Insurance
class Insurance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    provider_name = db.Column(db.String(100), nullable=False)
    policy_number = db.Column(db.String(50), nullable=False)
    group_number = db.Column(db.String(50))
    coverage_type = db.Column(db.String(50))
    effective_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    copay_amount = db.Column(db.Float, default=0.0)
    deductible = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('Patient', backref='insurance_policies')

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(20), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    total_amount = db.Column(db.Float, nullable=False)
    insurance_amount = db.Column(db.Float, default=0.0)
    patient_amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue, cancelled
    due_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('Patient', backref='bills')
    appointment = db.relationship('Appointment', backref='bill')

class BillItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    service_code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    bill = db.relationship('Bill', backref='items')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.String(20), unique=True, nullable=False)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, card, insurance, check
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    reference_number = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    bill = db.relationship('Bill', backref='payments')

class LabTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_code = db.Column(db.String(20), unique=True, nullable=False)
    test_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    normal_range = db.Column(db.String(100))
    unit = db.Column(db.String(20))
    price = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class LabResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.String(20), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('lab_test.id'), nullable=False)
    result_value = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, completed, reviewed
    test_date = db.Column(db.DateTime, nullable=False)
    result_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    patient = db.relationship('Patient', backref='lab_results')
    doctor = db.relationship('Doctor', backref='lab_results')
    test = db.relationship('LabTest', backref='results')

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.String(20), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('Patient', backref='prescriptions')
    doctor = db.relationship('Doctor', backref='prescriptions')
    appointment = db.relationship('Appointment', backref='prescriptions')

class PrescriptionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescription.id'), nullable=False)
    medication_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    instructions = db.Column(db.Text)
    quantity = db.Column(db.Integer)
    
    prescription = db.relationship('Prescription', backref='medications')

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(20), unique=True, nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    current_stock = db.Column(db.Integer, default=0)
    minimum_stock = db.Column(db.Integer, default=10)
    unit_price = db.Column(db.Float, nullable=False)
    supplier = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_name = db.Column(db.String(100), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)
    generated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parameters = db.Column(db.JSON)
    file_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='reports')