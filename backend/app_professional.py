from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dotenv import load_dotenv
from marshmallow import ValidationError
import os
import logging

# Load environment variables
load_dotenv()

# Import schemas and services
from schemas import UserSchema, PatientSchema, DoctorSchema, AppointmentSchema, MedicalRecordSchema
from email_service import mail, send_appointment_confirmation

app = Flask(__name__)

# Professional Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///hospital.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback-jwt-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Email Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
mail.init_app(app)
CORS(app)

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)


# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize schemas
user_schema = UserSchema()
patient_schema = PatientSchema()
doctor_schema = DoctorSchema()
appointment_schema = AppointmentSchema()
medical_record_schema = MedicalRecordSchema()

# ============= MODELS =============
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        return self.locked_until and self.locked_until > datetime.utcnow()

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    medical_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    blood_type = db.Column(db.String(5))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def age(self):
        today = datetime.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    availability = db.Column(db.String(200))
    consultation_fee = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_number = db.Column(db.String(20), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    appointment_type = db.Column(db.String(50), default='consultation')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

    patient = db.relationship('Patient', backref='appointments')
    doctor = db.relationship('Doctor', backref='appointments')

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    diagnosis = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    prescription = db.Column(db.Text)
    doctor_notes = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('Patient', backref='medical_records')
    doctor = db.relationship('Doctor', backref='medical_records')
    appointment = db.relationship('Appointment', backref='medical_record')


# ============= UTILITY FUNCTIONS =============
def log_audit(action, table_name, record_id=None):
    """Log user actions for audit trail"""
    try:
        current_user_id = get_jwt_identity()
        audit = AuditLog(
            user_id=current_user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()
    except Exception as e:
        logger.error(f"Audit logging failed: {str(e)}")

def generate_patient_id():
    """Generate unique patient ID"""
    import random
    while True:
        patient_id = f"P{datetime.now().year}{random.randint(1000, 9999)}"
        if not Patient.query.filter_by(patient_id=patient_id).first():
            return patient_id

def generate_appointment_number():
    """Generate unique appointment number"""
    import random
    while True:
        apt_num = f"APT{datetime.now().strftime('%Y%m%d')}{random.randint(100, 999)}"
        if not Appointment.query.filter_by(appointment_number=apt_num).first():
            return apt_num

# ============= ERROR HANDLERS =============
@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({'error': 'Validation failed', 'messages': e.messages}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

# ============= AUTH ROUTES =============
@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=data.get('username')).first()
    
    if not user or user.is_locked():
        return jsonify({'message': 'Invalid credentials or account locked'}), 401
    
    if user.check_password(data.get('password')) and user.is_active:
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        token = create_access_token(
            identity=user.id, 
            additional_claims={'role': user.role}
        )
        
        log_audit('LOGIN', 'user', user.id)
        
        return jsonify({
            'access_token': token,
            'user': {
                'id': user.id, 
                'username': user.username, 
                'role': user.role,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }), 200
    else:
        # Increment failed attempts
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
        
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/auth/me')
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({
        'user': {
            'id': user.id, 
            'username': user.username, 
            'role': user.role,
            'email': user.email,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    })

# ============= ENHANCED PATIENT ROUTES =============
@app.route('/api/patients', methods=['GET', 'POST'])
@jwt_required()
def patients():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = Patient.query
        if search:
            query = query.filter(
                db.or_(
                    Patient.first_name.contains(search),
                    Patient.last_name.contains(search),
                    Patient.patient_id.contains(search),
                    Patient.phone.contains(search)
                )
            )
        
        patients = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'patients': [{
                'id': p.id,
                'patient_id': p.patient_id,
                'first_name': p.first_name,
                'last_name': p.last_name,
                'age': p.age,
                'gender': p.gender,
                'phone': p.phone,
                'email': p.email,
                'blood_type': p.blood_type,
                'created_at': p.created_at.isoformat()
            } for p in patients.items],
            'total': patients.total,
            'pages': patients.pages,
            'current_page': page
        })
    
    # POST - Create patient
    try:
        data = patient_schema.load(request.get_json())
        
        patient = Patient(
            patient_id=generate_patient_id(),
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=data['date_of_birth'],
            gender=data['gender'],
            phone=data.get('phone'),
            email=data.get('email'),
            address=data.get('address'),
            medical_history=data.get('medical_history')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        log_audit('CREATE', 'patient', patient.id)
        
        return jsonify({
            'message': 'Patient created successfully',
            'patient_id': patient.patient_id,
            'id': patient.id
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'messages': e.messages}), 400

# ============= ENHANCED APPOINTMENT ROUTES =============
@app.route('/api/appointments', methods=['GET', 'POST'])
@jwt_required()
def appointments():
    if request.method == 'GET':
        date_filter = request.args.get('date')
        status_filter = request.args.get('status')
        
        query = Appointment.query
        if date_filter:
            query = query.filter(db.func.date(Appointment.appointment_date) == date_filter)
        if status_filter:
            query = query.filter(Appointment.status == status_filter)
        
        appointments = query.order_by(Appointment.appointment_date.desc()).all()
        
        return jsonify([{
            'id': a.id,
            'appointment_number': a.appointment_number,
            'patient_id': a.patient_id,
            'patient_name': f"{a.patient.first_name} {a.patient.last_name}",
            'doctor_id': a.doctor_id,
            'doctor_name': f"Dr. {a.doctor.first_name} {a.doctor.last_name}",
            'appointment_date': a.appointment_date.isoformat(),
            'status': a.status,
            'appointment_type': a.appointment_type,
            'notes': a.notes
        } for a in appointments])
    
    # POST - Create appointment
    try:
        data = appointment_schema.load(request.get_json())
        
        appointment = Appointment(
            appointment_number=generate_appointment_number(),
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            appointment_date=data['appointment_date'],
            status=data.get('status', 'scheduled'),
            notes=data.get('notes')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # Send confirmation email
        patient = Patient.query.get(data['patient_id'])
        doctor = Doctor.query.get(data['doctor_id'])
        
        if patient.email:
            send_appointment_confirmation(
                patient.email,
                f"{patient.first_name} {patient.last_name}",
                f"{doctor.first_name} {doctor.last_name}",
                appointment.appointment_date.strftime('%Y-%m-%d %H:%M')
            )
        
        log_audit('CREATE', 'appointment', appointment.id)
        
        return jsonify({
            'message': 'Appointment created successfully',
            'appointment_number': appointment.appointment_number,
            'id': appointment.id
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'messages': e.messages}), 400

# ============= DASHBOARD WITH REAL DATA =============
@app.route('/api/dashboard/overview')
@jwt_required()
def dashboard_overview():
    today = datetime.now().date()
    
    return jsonify({
        'total_patients': Patient.query.count(),
        'active_doctors': Doctor.query.filter_by(is_active=True).count(),
        'todays_appointments': Appointment.query.filter(
            db.func.date(Appointment.appointment_date) == today
        ).count(),
        'pending_appointments': Appointment.query.filter_by(status='scheduled').count(),
        'completed_today': Appointment.query.filter(
            db.and_(
                db.func.date(Appointment.appointment_date) == today,
                Appointment.status == 'completed'
            )
        ).count()
    })

@app.route('/api/bills', methods=['GET', 'POST'])
@jwt_required()
def bills():
    if request.method == 'GET':
        return jsonify({'bills': [], 'message': 'Billing API ready - add Invoice model'})
    
    data = request.get_json()
    return jsonify({'message': 'Bill created', 'bill_id': 1}), 201

@app.route('/api/bills/<int:id>/payment', methods=['POST'])
@jwt_required()
def process_payment(id):
    data = request.get_json()
    return jsonify({'message': 'Payment processed'}), 200

@app.route('/api/dashboard/recent-activities')
@jwt_required()
def recent_activities():

    recent_appointments = Appointment.query.order_by(
        Appointment.created_at.desc()
    ).limit(5).all()
    
    recent_patients = Patient.query.order_by(
        Patient.created_at.desc()
    ).limit(5).all()
    
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
            'patient_id': p.patient_id,
            'created_at': p.created_at.isoformat()
        } for p in recent_patients]
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
        admin.set_password('Admin123!')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created: admin / Admin123!")
    else:
        print("ℹ️  Admin user already exists")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    print("\n🏥 Professional Hospital Management System")
    print("=" * 50)
    print("📍 Backend URL: http://localhost:5000")
    print("👤 Admin Login: admin / Admin123!")
    print("🔒 Security: Rate limiting, validation, audit logs")
    print("📧 Features: Email notifications, enhanced models")
    print("=" * 50 + "\n")
    
    app.run(debug=True, port=5000)