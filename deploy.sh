#!/bin/bash

echo "🏥 Hospital Management System - Complete Deployment"

# Install backend dependencies
echo "📦 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Setting up frontend..."
cd ../frontend
npm install

echo "✅ Setup complete!"

# Start both servers
echo "🚀 Starting servers..."

# Start backend in background
cd ../backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "🎉 Hospital Management System is running!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:5000"
echo "Login: admin / admin123"

# Keep script running
wait