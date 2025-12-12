#!/bin/bash

# Setup script for Tutorly Platform Backend

echo "🚀 Tutorly Platform - Backend Setup"
echo "===================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the server:"
echo "     python3 app/main.py"
echo "     or"
echo "     uvicorn app.main:app --reload"
echo ""
echo "  3. Access the API:"
echo "     http://localhost:8000/api/docs"
echo ""
