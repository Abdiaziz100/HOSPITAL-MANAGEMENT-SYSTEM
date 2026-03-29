#!/bin/bash

echo "🧪 Testing Hospital Management System..."

# Test backend
echo "Testing backend API..."
cd backend
source venv/bin/activate

# Test if server starts
timeout 3 python app.py &
sleep 2

# Test API endpoints
curl -s http://localhost:5000/api/auth/login > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend API is working"
else
    echo "❌ Backend API failed"
fi

# Kill background process
pkill -f "python app.py"

# Test frontend
echo "Testing frontend build..."
cd ../frontend
npm run build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Frontend builds successfully"
else
    echo "❌ Frontend build failed"
fi

echo "🎉 Testing complete!"