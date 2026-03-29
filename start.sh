#!/bin/bash

echo "🏥 Starting Hospital Management System..."

# Function to kill background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup EXIT

# Start backend
echo "🚀 Starting backend server..."
cd backend
source venv/bin/activate
python app_professional.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🚀 Starting frontend server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "✅ Both servers started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:5000"
👤 Login: admin / Admin123!
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
wait