from flask_mail import Mail, Message
from flask import current_app
import logging

mail = Mail()

def send_email(to, subject, template, **kwargs):
    """Send email notification"""
    try:
        msg = Message(
            subject=f"[Hospital Management] {subject}",
            recipients=[to],
            html=template,
            sender=current_app.config['MAIL_USERNAME']
        )
        mail.send(msg)
        logging.info(f"Email sent to {to}: {subject}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email to {to}: {str(e)}")
        return False

def send_appointment_confirmation(patient_email, patient_name, doctor_name, appointment_date):
    """Send appointment confirmation email"""
    template = f"""
    <h2>Appointment Confirmation</h2>
    <p>Dear {patient_name},</p>
    <p>Your appointment has been confirmed with the following details:</p>
    <ul>
        <li><strong>Doctor:</strong> Dr. {doctor_name}</li>
        <li><strong>Date & Time:</strong> {appointment_date}</li>
    </ul>
    <p>Please arrive 15 minutes early for your appointment.</p>
    <p>Best regards,<br>Hospital Management Team</p>
    """
    return send_email(patient_email, "Appointment Confirmation", template)

def send_appointment_reminder(patient_email, patient_name, doctor_name, appointment_date):
    """Send appointment reminder email"""
    template = f"""
    <h2>Appointment Reminder</h2>
    <p>Dear {patient_name},</p>
    <p>This is a reminder for your upcoming appointment:</p>
    <ul>
        <li><strong>Doctor:</strong> Dr. {doctor_name}</li>
        <li><strong>Date & Time:</strong> {appointment_date}</li>
    </ul>
    <p>Please arrive 15 minutes early.</p>
    <p>Best regards,<br>Hospital Management Team</p>
    """
    return send_email(patient_email, "Appointment Reminder", template)