from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hospital-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# ============= MODELS =============
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('Patient', backref='medical_records')
    doctor = db.relationship('Doctor', backref='medical_records')

# ============= AUTH ROUTES =============
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

# ============= DASHBOARD ROUTES =============
@app.route('/api/dashboard/overview')
@jwt_required()
def dashboard_overview():
    return jsonify({
        'total_patients': Patient.query.count(),
        'available_doctors': Doctor.query.filter_by(is_active=True).count(),
        'todays_appointments': Appointment.query.count()
    })

@app.route('/api/dashboard/appointments-chart')
@jwt_required()
def appointments_chart():
    # Simple mock data for chart - in real app, query last 7 days
    return jsonify([
        {'date': '2024-01-01', 'count': 5},
        {'date': '2024-01-02', 'count': 8},
        {'date': '2024-01-03', 'count': 3},
        {'date': '2024-01-04', 'count': 12},
        {'date': '2024-01-05', 'count': 7},
        {'date': '2024-01-06', 'count': 9},
        {'date': '2024-01-07', 'count': 6}
    ])

@app.route('/api/dashboard/patient-registrations')
@jwt_required()
def patient_registrations():
    # Simple mock data for chart - in real app, query last 7 days
    return jsonify([
        {'date': '2024-01-01', 'count': 2},
        {'date': '2024-01-02', 'count': 4},
        {'date': '2024-01-03', 'count': 1},
        {'date': '2024-01-04', 'count': 6},
        {'date': '2024-01-05', 'count': 3},
        {'date': '2024-01-06', 'count': 5},
        {'date': '2024-01-07', 'count': 2}
    ])

# ============= PATIENT ROUTES =============
@app.route('/api/patients', methods=['GET', 'POST'])
@jwt_required()
def patients():
    if request.method == 'GET':
        patients = Patient.query.all()
        return jsonify([{
            'id': p.id, 'first_name': p.first_name, 'last_name': p.last_name,
            'age': p.age, 'gender': p.gender, 'phone': p.phone, 'email': p.email,
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
    patient.medical_history = data.get('medical_history', patient.medical_history)
    db.session.commit()
    return jsonify({'message': 'Patient updated'})

# ============= DOCTOR ROUTES =============
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

# ============= APPOINTMENT ROUTES =============
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
    
    data = request.get_json()
    appointment = Appointment(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        appointment_date=datetime.strptime(data['appointment_date'], '%Y-%m-%dT%H:%M'),
        notes=data.get('notes')
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment booked', 'id': appointment.id}), 201

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

# ============= MEDICAL RECORDS ROUTES =============
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
            'created_at': r.created_at.isoformat()
        } for r in records])
    
    data = request.get_json()
    record = MedicalRecord(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        diagnosis=data.get('diagnosis'),
        prescription=data.get('prescription'),
        doctor_notes=data.get('doctor_notes')
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
    db.session.commit()
    return jsonify({'message': 'Medical record updated'})

# ============= USER MANAGEMENT ROUTES =============
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
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted'})
    
    data = request.get_json()
    user.is_active = data.get('is_active', user.is_active)
    user.role = data.get('role', user.role)
    if 'password' in data:
        user.set_password(data['password'])
    db.session.commit()
    return jsonify({'message': 'User updated'})

@app.route('/api/auth/me')
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({
        'user': {'id': user.id, 'username': user.username, 'role': user.role}
    })

# ============= INITIALIZATION =============
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
        print("Admin user created: username=admin, password=admin123")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
    app.run(debug=True, port=5000)
        records = MedicalRecord.query.all()
        return jsonify([{
            'id': r.id,
            'patient_name': f"{r.patient.first_name} {r.patient.last_name}",
            'doctor_name': f"Dr. {r.doctor.first_name} {r.doctor.last_name}",
            'diagnosis': r.diagnosis,
            'prescription': r.prescription,
            'doctor_notes': r.doctor_notes,
            'created_at': r.created_at.isoformat()
        } for r in records])
    
    data = request.get_json()
    record = MedicalRecord(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        diagnosis=data.get('diagnosis'),
        prescription=data.get('prescription'),
        doctor_notes=data.get('doctor_notes')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'message': 'Medical record created', 'id': record.id}), 201

# ============= CREATE ADMIN AND RUN =============
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@hospital.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created: admin / admin123")
        else:
            print("ℹ️  Admin user already exists: admin / admin123")
    
    print("\n🚀 Hospital Management System Backend")
    print("=" * 40)
    print("📍 URL: http://localhost:5000")
    print("👤 Default Admin Login:")
    print("   Username: admin")
    print("   Password: admin123")
    print("=" * 40 + "\n")
    
    app.run(debug=True, port=5000)

