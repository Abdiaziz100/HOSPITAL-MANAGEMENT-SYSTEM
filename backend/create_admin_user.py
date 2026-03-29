#!/usr/bin/env python3

from app import app, db, User

def create_admin():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@hospital.com',
            role='admin'
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")

if __name__ == '__main__':
    create_admin()