from flask import Flask, request, jsonify, send_file
from datetime import datetime, timedelta
import uuid
import io
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ============= BILLING ROUTES =============
@app.route('/api/bills', methods=['GET', 'POST'])
@jwt_required()
def bills():
    if request.method == 'GET':
        status_filter = request.args.get('status')
        patient_id = request.args.get('patient_id')
        
        query = Bill.query
        if status_filter:
            query = query.filter(Bill.status == status_filter)
        if patient_id:
            query = query.filter(Bill.patient_id == patient_id)
        
        bills = query.order_by(Bill.created_at.desc()).all()
        
        return jsonify([{
            'id': b.id,
            'bill_number': b.bill_number,
            'patient_name': f"{b.patient.first_name} {b.patient.last_name}",
            'total_amount': b.total_amount,
            'paid_amount': b.paid_amount,
            'balance': b.total_amount - b.paid_amount,
            'status': b.status,
            'due_date': b.due_date.isoformat(),
            'created_at': b.created_at.isoformat()
        } for b in bills])
    
    # Create new bill
    data = request.get_json()
    bill = Bill(
        bill_number=f"BILL{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}",
        patient_id=data['patient_id'],
        appointment_id=data.get('appointment_id'),
        total_amount=data['total_amount'],
        patient_amount=data['patient_amount'],
        due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    )
    
    db.session.add(bill)
    db.session.commit()
    
    # Add bill items
    for item_data in data.get('items', []):
        item = BillItem(
            bill_id=bill.id,
            service_code=item_data['service_code'],
            description=item_data['description'],
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            total_price=item_data['quantity'] * item_data['unit_price']
        )
        db.session.add(item)
    
    db.session.commit()
    return jsonify({'message': 'Bill created', 'bill_number': bill.bill_number}), 201

@app.route('/api/bills/<int:id>/payment', methods=['POST'])
@jwt_required()
def process_payment(id):
    bill = Bill.query.get_or_404(id)
    data = request.get_json()
    
    payment = Payment(
        payment_id=f"PAY{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}",
        bill_id=bill.id,
        amount=data['amount'],
        payment_method=data['payment_method'],
        reference_number=data.get('reference_number'),
        notes=data.get('notes')
    )
    
    db.session.add(payment)
    
    # Update bill paid amount
    bill.paid_amount += data['amount']
    if bill.paid_amount >= bill.total_amount:
        bill.status = 'paid'
    
    db.session.commit()
    return jsonify({'message': 'Payment processed', 'payment_id': payment.payment_id}), 201

# ============= LAB RESULTS ROUTES =============
@app.route('/api/lab-tests', methods=['GET', 'POST'])
@jwt_required()
def lab_tests():
    if request.method == 'GET':
        tests = LabTest.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': t.id,
            'test_code': t.test_code,
            'test_name': t.test_name,
            'category': t.category,
            'normal_range': t.normal_range,
            'unit': t.unit,
            'price': t.price
        } for t in tests])
    
    data = request.get_json()
    test = LabTest(
        test_code=data['test_code'],
        test_name=data['test_name'],
        category=data['category'],
        normal_range=data.get('normal_range'),
        unit=data.get('unit'),
        price=data['price']
    )
    db.session.add(test)
    db.session.commit()
    return jsonify({'message': 'Lab test created'}), 201

@app.route('/api/lab-results', methods=['GET', 'POST'])
@jwt_required()
def lab_results():
    if request.method == 'GET':
        patient_id = request.args.get('patient_id')
        status = request.args.get('status')
        
        query = LabResult.query
        if patient_id:
            query = query.filter(LabResult.patient_id == patient_id)
        if status:
            query = query.filter(LabResult.status == status)
        
        results = query.order_by(LabResult.test_date.desc()).all()
        
        return jsonify([{
            'id': r.id,
            'result_id': r.result_id,
            'patient_name': f"{r.patient.first_name} {r.patient.last_name}",
            'test_name': r.test.test_name,
            'result_value': r.result_value,
            'normal_range': r.test.normal_range,
            'status': r.status,
            'test_date': r.test_date.isoformat(),
            'result_date': r.result_date.isoformat() if r.result_date else None
        } for r in results])
    
    data = request.get_json()
    result = LabResult(
        result_id=f"LAB{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}",
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        test_id=data['test_id'],
        test_date=datetime.strptime(data['test_date'], '%Y-%m-%dT%H:%M')
    )
    db.session.add(result)
    db.session.commit()
    return jsonify({'message': 'Lab result created', 'result_id': result.result_id}), 201

# ============= PRESCRIPTION ROUTES =============
@app.route('/api/prescriptions', methods=['GET', 'POST'])
@jwt_required()
def prescriptions():
    if request.method == 'GET':
        patient_id = request.args.get('patient_id')
        status = request.args.get('status')
        
        query = Prescription.query
        if patient_id:
            query = query.filter(Prescription.patient_id == patient_id)
        if status:
            query = query.filter(Prescription.status == status)
        
        prescriptions = query.order_by(Prescription.created_at.desc()).all()
        
        return jsonify([{
            'id': p.id,
            'prescription_id': p.prescription_id,
            'patient_name': f"{p.patient.first_name} {p.patient.last_name}",
            'doctor_name': f"Dr. {p.doctor.first_name} {p.doctor.last_name}",
            'status': p.status,
            'created_at': p.created_at.isoformat(),
            'medications': [{
                'medication_name': m.medication_name,
                'dosage': m.dosage,
                'frequency': m.frequency,
                'duration': m.duration
            } for m in p.medications]
        } for p in prescriptions])
    
    data = request.get_json()
    prescription = Prescription(
        prescription_id=f"RX{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}",
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        appointment_id=data.get('appointment_id')
    )
    db.session.add(prescription)
    db.session.commit()
    
    # Add medications
    for med_data in data.get('medications', []):
        medication = PrescriptionItem(
            prescription_id=prescription.id,
            medication_name=med_data['medication_name'],
            dosage=med_data['dosage'],
            frequency=med_data['frequency'],
            duration=med_data['duration'],
            instructions=med_data.get('instructions'),
            quantity=med_data.get('quantity')
        )
        db.session.add(medication)
    
    db.session.commit()
    return jsonify({'message': 'Prescription created', 'prescription_id': prescription.prescription_id}), 201

# ============= INVENTORY ROUTES =============
@app.route('/api/inventory', methods=['GET', 'POST'])
@jwt_required()
def inventory():
    if request.method == 'GET':
        low_stock = request.args.get('low_stock') == 'true'
        
        query = Inventory.query
        if low_stock:
            query = query.filter(Inventory.current_stock <= Inventory.minimum_stock)
        
        items = query.all()
        
        return jsonify([{
            'id': i.id,
            'item_code': i.item_code,
            'item_name': i.item_name,
            'category': i.category,
            'current_stock': i.current_stock,
            'minimum_stock': i.minimum_stock,
            'unit_price': i.unit_price,
            'supplier': i.supplier,
            'expiry_date': i.expiry_date.isoformat() if i.expiry_date else None,
            'status': 'Low Stock' if i.current_stock <= i.minimum_stock else 'In Stock'
        } for i in items])
    
    data = request.get_json()
    item = Inventory(
        item_code=data['item_code'],
        item_name=data['item_name'],
        category=data['category'],
        current_stock=data['current_stock'],
        minimum_stock=data.get('minimum_stock', 10),
        unit_price=data['unit_price'],
        supplier=data.get('supplier'),
        expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data.get('expiry_date') else None
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Inventory item created'}), 201

# ============= REPORTING ROUTES =============
@app.route('/api/reports/generate', methods=['POST'])
@jwt_required()
def generate_report():
    data = request.get_json()
    report_type = data['report_type']
    
    if report_type == 'patient_summary':
        return generate_patient_summary_report(data)
    elif report_type == 'financial_summary':
        return generate_financial_report(data)
    elif report_type == 'appointment_summary':
        return generate_appointment_report(data)
    else:
        return jsonify({'error': 'Invalid report type'}), 400

def generate_patient_summary_report(data):
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
    
    patients = Patient.query.filter(
        Patient.created_at.between(start_date, end_date)
    ).all()
    
    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Patient ID', 'Name', 'Age', 'Gender', 'Phone', 'Email', 'Registration Date'])
    
    for patient in patients:
        writer.writerow([
            patient.id,
            f"{patient.first_name} {patient.last_name}",
            patient.age,
            patient.gender,
            patient.phone,
            patient.email,
            patient.created_at.strftime('%Y-%m-%d')
        ])
    
    output.seek(0)
    return jsonify({
        'report_data': output.getvalue(),
        'total_patients': len(patients),
        'report_type': 'patient_summary'
    })

def generate_financial_report(data):
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
    
    bills = Bill.query.filter(
        Bill.created_at.between(start_date, end_date)
    ).all()
    
    total_revenue = sum(bill.total_amount for bill in bills)
    total_collected = sum(bill.paid_amount for bill in bills)
    outstanding = total_revenue - total_collected
    
    return jsonify({
        'total_revenue': total_revenue,
        'total_collected': total_collected,
        'outstanding_amount': outstanding,
        'total_bills': len(bills),
        'paid_bills': len([b for b in bills if b.status == 'paid']),
        'pending_bills': len([b for b in bills if b.status == 'pending'])
    })

# ============= ANALYTICS ROUTES =============
@app.route('/api/analytics/dashboard')
@jwt_required()
def analytics_dashboard():
    today = datetime.now().date()
    this_month = datetime.now().replace(day=1).date()
    
    # Revenue analytics
    monthly_revenue = db.session.query(db.func.sum(Bill.total_amount)).filter(
        Bill.created_at >= this_month
    ).scalar() or 0
    
    # Patient analytics
    new_patients_this_month = Patient.query.filter(
        Patient.created_at >= this_month
    ).count()
    
    # Appointment analytics
    completed_appointments = Appointment.query.filter(
        Appointment.status == 'completed',
        db.func.date(Appointment.appointment_date) == today
    ).count()
    
    # Lab results pending
    pending_lab_results = LabResult.query.filter_by(status='pending').count()
    
    # Low stock items
    low_stock_items = Inventory.query.filter(
        Inventory.current_stock <= Inventory.minimum_stock
    ).count()
    
    return jsonify({
        'monthly_revenue': monthly_revenue,
        'new_patients_this_month': new_patients_this_month,
        'completed_appointments_today': completed_appointments,
        'pending_lab_results': pending_lab_results,
        'low_stock_alerts': low_stock_items,
        'revenue_trend': 'up',  # This would be calculated based on previous month
        'patient_satisfaction': 4.5  # This would come from a feedback system
    })