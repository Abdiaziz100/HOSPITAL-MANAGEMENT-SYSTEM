okay #!/bin/bash

echo "🏥 Setting up Hospital Management System..."

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "✅ Backend setup complete!"

# Frontend setup
echo "📦 Setting up frontend..."
cd ../frontend

# Install dependencies
npm install

echo "✅ Frontend setup complete!"

cd ..

echo "🎉 Setup complete! To start the application:"
python app_professional.py
echo "2. Start frontend: cd frontend && npm start"
echo "3. Open http://localhost:3000 in your browser"
Login with admin/Admin123!
