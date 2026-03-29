from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from urllib.parse import quote_plus

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hospital-secret-key-change-in-prod'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 280
}
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'hospital-management-system-jwt-secret-key-32-chars')

# Database config
if os.environ.get('DATABASE_URL'):
    # PostgreSQL on Render/Heroku
    db_url = os.environ['DATABASE_URL'].replace("postgres://", "postgresql://")
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    # Local SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/abdiaziz-mahat/HOSPITAL-MANAGEMENT-SYSTEM/backend/instance/hospital.db'

db = SQLAlchemy(app)
jwt = JWTManager(app)

# CORS for Vercel domains
cors_origins = os.environ.get('CORS_ORIGINS', '*').split(',')
CORS(app, origins=cors_origins)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    medical_history = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def age(self):
        today = datetime.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    availability = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('Patient', backref='appointments')
    doctor = db.relationship('Doctor', backref='appointments')

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    doctor_notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('Patient', backref='medical_records')
    doctor = db.relationship('Doctor', backref='medical_records')

class Billing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(20), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    total_amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    due_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('Patient', backref='bills')
    appointment = db.relationship('Appointment', backref='bill')

# Auth Routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')) and user.is_active:
        token = create_access_token(identity=user.id, additional_claims={'role': user.role})
        return jsonify({
            'access_token': token,
            'user': {'id': user.id, 'username': user.username, 'role': user.role}
        }), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/auth/me')
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({'user': {'id': user.id, 'username': user.username, 'role': user.role}})

# Dashboard Routes
@app.route('/api/dashboard/overview')
@jwt_required()
def dashboard_overview():
    from datetime import date
    today = date.today()
    todays_appointments = Appointment.query.filter(
        db.func.date(Appointment.appointment_date) == today
    ).count()
    
    return jsonify({
        'total_patients': Patient.query.count(),
        'available_doctors': Doctor.query.filter_by(is_active=True).count(),
        'todays_appointments': todays_appointments,
        'completed_today': Appointment.query.filter(
            db.func.date(Appointment.appointment_date) == today,
            Appointment.status == 'completed'
        ).count()
    })

@app.route('/api/dashboard/recent-activities')
@jwt_required()
def recent_activities():
    # Get recent appointments (last 5)
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all()
    # Get recent patients (last 5)
    recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
    
    return jsonify({
        'recent_appointments': [{
            'id': a.id,
            'patient_name': f"{a.patient.first_name} {a.patient.last_name}",
            'doctor_name': f"Dr. {a.doctor.first_name} {a.doctor.last_name}",
            'date': a.appointment_date.isoformat(),
            'status': a.status
        } for a in recent_appointments],
        'recent_patients': [{
            'id': p.id,
            'name': f"{p.first_name} {p.last_name}",
            'patient_id': f"P{p.id:04d}",
            'created_at': p.created_at.isoformat()
        } for p in recent_patients]
    })

# Patient Routes
@app.route('/api/patients', methods=['GET', 'POST'])
@jwt_required()
def patients():
    if request.method == 'GET':
        patients = Patient.query.all()
        today = datetime.today()
        return jsonify([{
            'id': p.id, 'first_name': p.first_name, 'last_name': p.last_name,
            'age': today.year - p.date_of_birth.year - ((today.month, today.day) < (p.date_of_birth.month, p.date_of_birth.day)),
            'gender': p.gender, 'phone': p.phone, 'email': p.email,
            'medical_history': p.medical_history
        } for p in patients])
    
    data = request.get_json()
    patient = Patient(
        first_name=data['first_name'],
        last_name=data['last_name'],
        date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
        gender=data['gender'],
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address'),
        medical_history=data.get('medical_history')
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify({'message': 'Patient created', 'id': patient.id}), 201

@app.route('/api/patients/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def patient_detail(id):
    patient = Patient.query.get_or_404(id)
    if request.method == 'DELETE':
        db.session.delete(patient)
        db.session.commit()
        return jsonify({'message': 'Patient deleted'})
    
    data = request.get_json()
    patient.first_name = data.get('first_name', patient.first_name)
    patient.last_name = data.get('last_name', patient.last_name)
    patient.gender = data.get('gender', patient.gender)
    patient.phone = data.get('phone', patient.phone)
    patient.email = data.get('email', patient.email)
    patient.address = data.get('address', patient.address)
    patient.medical_history = data.get('medical_history', patient.medical_history)
    if data.get('date_of_birth'):
        patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify({'message': 'Patient updated'})

# Doctor Routes
@app.route('/api/doctors', methods=['GET', 'POST'])
@jwt_required()
def doctors():
    if request.method == 'GET':
        doctors = Doctor.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': d.id, 'first_name': d.first_name, 'last_name': d.last_name,
            'specialty': d.specialty, 'phone': d.phone, 'email': d.email,
            'availability': d.availability, 'is_active': d.is_active
        } for d in doctors])
    
    data = request.get_json()
    doctor = Doctor(
        first_name=data['first_name'],
        last_name=data['last_name'],
        specialty=data['specialty'],
        phone=data.get('phone'),
        email=data.get('email'),
        availability=data.get('availability')
    )
    db.session.add(doctor)
    db.session.commit()
    return jsonify({'message': 'Doctor created', 'id': doctor.id}), 201

@app.route('/api/doctors/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def doctor_detail(id):
    doctor = Doctor.query.get_or_404(id)
    if request.method == 'DELETE':
        doctor.is_active = False
        db.session.commit()
        return jsonify({'message': 'Doctor deactivated'})
    
    data = request.get_json()
    doctor.first_name = data.get('first_name', doctor.first_name)
    doctor.last_name = data.get('last_name', doctor.last_name)
    doctor.specialty = data.get('specialty', doctor.specialty)
    doctor.phone = data.get('phone', doctor.phone)
    doctor.email = data.get('email', doctor.email)
    doctor.availability = data.get('availability', doctor.availability)
    db.session.commit()
    return jsonify({'message': 'Doctor updated'})

# Appointment Routes
@app.route('/api/appointments', methods=['GET', 'POST'])
@jwt_required()
def appointments():
    if request.method == 'GET':
        appointments = Appointment.query.all()
        return jsonify([{
            'id': a.id,
            'patient_id': a.patient_id,
            'patient_name': f"{a.patient.first_name} {a.patient.last_name}",
            'doctor_id': a.doctor_id,
            'doctor_name': f"Dr. {a.doctor.first_name} {a.doctor.last_name}",
            'appointment_date': a.appointment_date.isoformat(),
            'status': a.status,
            'notes': a.notes
        } for a in appointments])
    
    try:
        data = request.get_json()
        appointment = Appointment(
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            appointment_date=datetime.strptime(data['appointment_date'], '%Y-%m-%dT%H:%M:%S'),
            status=data.get('status', 'scheduled'),
            notes=data.get('notes')
        )
        db.session.add(appointment)
        db.session.commit()
        return jsonify({'message': 'Appointment booked', 'id': appointment.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 400

@app.route('/api/appointments/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def appointment_detail(id):
    appointment = Appointment.query.get_or_404(id)
    if request.method == 'DELETE':
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({'message': 'Appointment deleted'})
    
    data = request.get_json()
    appointment.status = data.get('status', appointment.status)
    appointment.notes = data.get('notes', appointment.notes)
    db.session.commit()
    return jsonify({'message': 'Appointment updated'})

# Medical Records Routes
@app.route('/api/medical-records', methods=['GET', 'POST'])
@jwt_required()
def medical_records():
    if request.method == 'GET':
        records = MedicalRecord.query.all()
        return jsonify([{
            'id': r.id,
            'patient_id': r.patient_id,
            'patient_name': f"{r.patient.first_name} {r.patient.last_name}",
            'doctor_id': r.doctor_id,
            'doctor_name': f"Dr. {r.doctor.first_name} {r.doctor.last_name}",
            'diagnosis': r.diagnosis,
            'prescription': r.prescription,
            'doctor_notes': r.doctor_notes,
            'status': r.status,
            'created_at': r.created_at.isoformat()
        } for r in records])
    
    data = request.get_json()
    record = MedicalRecord(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        diagnosis=data.get('diagnosis'),
        prescription=data.get('prescription'),
        doctor_notes=data.get('doctor_notes'),
        status=data.get('status', 'active')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'message': 'Medical record created', 'id': record.id}), 201

@app.route('/api/medical-records/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def medical_record_detail(id):
    record = MedicalRecord.query.get_or_404(id)
    if request.method == 'DELETE':
        db.session.delete(record)
        db.session.commit()
        return jsonify({'message': 'Medical record deleted'})
    
    data = request.get_json()
    record.diagnosis = data.get('diagnosis', record.diagnosis)
    record.prescription = data.get('prescription', record.prescription)
    record.doctor_notes = data.get('doctor_notes', record.doctor_notes)
    record.status = data.get('status', record.status)
    db.session.commit()
    return jsonify({'message': 'Medical record updated'})

@app.route('/api/bills', methods=['GET', 'POST'])
@jwt_required()
def bills():
    if request.method == 'GET':
        bills_list = Billing.query.all()
        return jsonify([{
            'id': b.id,
            'bill_number': b.bill_number,
            'patient_name': f"{b.patient.first_name} {b.patient.last_name}",
            'patient_id': b.patient_id,
            'total_amount': float(b.total_amount),
            'paid_amount': float(b.paid_amount),
            'balance': float(b.balance),
            'status': b.status,
            'due_date': b.due_date.isoformat() if b.due_date else None,
            'created_at': b.created_at.isoformat()
        } for b in bills_list])
    
    data = request.get_json()
    # Generate bill number
    last_bill = Billing.query.order_by(Billing.id.desc()).first()
    next_id = (last_bill.id if last_bill else 0) + 1
    bill_number = f"BILL{next_id:03d}"
    
    bill = Billing(
        bill_number=bill_number,
        patient_id=data['patient_id'],
        appointment_id=data.get('appointment_id'),
        total_amount=float(data['total_amount']),
        paid_amount=0.0,
        balance=float(data['total_amount']),
        status=data.get('status', 'pending'),
        due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
        notes=data.get('notes')
    )
    db.session.add(bill)
    db.session.commit()
    return jsonify({'message': 'Bill created', 'id': bill.id, 'bill_number': bill_number}), 201

@app.route('/api/bills/<int:id>/payment', methods=['POST'])
@jwt_required()
def process_payment(id):
    bill = Billing.query.get_or_404(id)
    data = request.get_json()
    amount = float(data['amount'])
    bill.paid_amount += amount
    bill.balance -= amount
    if bill.balance <= 0:
        bill.status = 'paid'
    db.session.commit()
    return jsonify({
        'message': f'Payment of ${amount} processed for bill {id}',
        'bill': {
            'id': bill.id,
            'paid_amount': float(bill.paid_amount),
            'balance': float(bill.balance),
            'status': bill.status
        }
    }), 200

@app.route('/api/bills/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def bill_detail(id):
    bill = Billing.query.get_or_404(id)
    if request.method == 'DELETE':
        db.session.delete(bill)
        db.session.commit()
        return jsonify({'message': 'Bill deleted'})
    
    data = request.get_json()
    bill.total_amount = float(data.get('total_amount', bill.total_amount))
    bill.paid_amount = float(data.get('paid_amount', bill.paid_amount))
    bill.balance = float(data.get('balance', bill.balance))
    bill.status = data.get('status', bill.status)
    if data.get('due_date'):
        bill.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    bill.notes = data.get('notes', bill.notes)
    db.session.commit()
    return jsonify({'message': 'Bill updated'})

# User Management Routes (Admin only)
@app.route('/api/users', methods=['GET', 'POST'])
@jwt_required()
def users():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if current_user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    if request.method == 'GET':
        users = User.query.all()
        return jsonify([{
            'id': u.id, 'username': u.username, 'email': u.email,
            'role': u.role, 'is_active': u.is_active,
            'created_at': u.created_at.isoformat()
        } for u in users])
    
    data = request.get_json()
    user = User(
        username=data['username'],
        email=data['email'],
        role=data['role']
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created', 'id': user.id}), 201

@app.route('/api/users/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def user_detail(id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if current_user.role != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    
    user = User.query.get_or_404(id)
    if request.method == 'DELETE':
        user.is_active = False
        db.session.commit()
        return jsonify({'message': 'User deactivated'})
    
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.role = data.get('role', user.role)
    if data.get('password'):
        user.set_password(data['password'])
    db.session.commit()
    return jsonify({'message': 'User updated'})

def create_admin_user():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@hospital.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created: admin/admin123')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
        
        # Create sample data if none exists
        if Patient.query.count() == 0:
            # Sample patients
            patients = [
                Patient(first_name='John', last_name='Doe', date_of_birth=datetime(1990, 1, 1).date(), 
                       gender='Male', phone='123-456-7890', email='john@example.com'),
                Patient(first_name='Jane', last_name='Smith', date_of_birth=datetime(1985, 5, 15).date(), 
                       gender='Female', phone='098-765-4321', email='jane@example.com')
            ]
            for p in patients:
                db.session.add(p)
            
            # Sample doctors
            doctors = [
                Doctor(first_name='Sarah', last_name='Johnson', specialty='Cardiology', 
                      phone='555-0101', email='dr.johnson@hospital.com', availability='Mon-Fri 9AM-5PM'),
                Doctor(first_name='Michael', last_name='Brown', specialty='Pediatrics', 
                      phone='555-0102', email='dr.brown@hospital.com', availability='Mon-Wed 8AM-4PM')
            ]
            for d in doctors:
                db.session.add(d)
            
            # Sample appointments
            appointments = [
                Appointment(patient_id=1, doctor_id=1, appointment_date=datetime.now(), status='completed'),
                Appointment(patient_id=2, doctor_id=2, appointment_date=datetime.now(), status='scheduled')
            ]
            for a in appointments:
                db.session.add(a)
            
            # Sample bills
            bills = [
                Billing(
                    bill_number='BILL001',
                    patient_id=1,
                    appointment_id=1,
                    total_amount=250.00,
                    balance=150.00,
                    paid_amount=100.00,
                    status='pending',
                    due_date=datetime(2026, 3, 20).date()
                ),
                Billing(
                    bill_number='BILL002',
                    patient_id=2,
                    appointment_id=2,
                    total_amount=180.00,
                    balance=180.00,
                    status='pending',
                    due_date=datetime(2026, 3, 25).date()
                )
            ]
            for b in bills:
                db.session.add(b)
            
            db.session.commit()
            print("Sample data created (patients, doctors, appointments, bills)")
    
    print("🏥 Hospital Management System Ready!")
    print("Login: admin / admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)

SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
