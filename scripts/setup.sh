#!/bin/bash

# Cross-platform setup script for WarehouseVision AI
echo "Setting up WarehouseVision AI development environment..."

# Detect OS type
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="Linux"
    echo "Detected Linux OS: $(lsb_release -d 2>/dev/null | cut -f2- || cat /etc/*-release | grep PRETTY_NAME | cut -d= -f2- || echo 'Unknown')"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macOS"
    echo "Detected macOS: $(sw_vers -productVersion)"
else
    OS_TYPE="Unknown"
    echo "Warning: Unrecognized OS. Script may not work correctly."
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "Python version: $PYTHON_VERSION"
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "Warning: This project is recommended to use Python 3.10+."
    read -p "Continue with Python $PYTHON_VERSION? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [ "$OS_TYPE" == "Linux" ] || [ "$OS_TYPE" == "macOS" ]; then
    source venv/bin/activate
else
    # Windows fallback
    venv/Scripts/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
fi

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    echo "Please manually activate it with: source venv/bin/activate (Linux/macOS) or venv\\Scripts\\activate (Windows)"
    exit 1
fi

# Install required packages
echo "Installing core dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create basic directories
mkdir -p data/images data/videos models/yolo models/ocr models/facial logs

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Created .env file from example."
    else
        echo "Creating basic .env file..."
        cat > .env << EOF
# Environment configuration
ENVIRONMENT=development

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/warehousevision
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=warehousevision

# JWT
JWT_SECRET=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Model Registry
MODEL_REGISTRY=./models

# Logging
LOG_LEVEL=INFO
EOF
        echo "Created basic .env file."
    fi
else
    echo ".env file already exists."
fi

# Make scripts executable
chmod +x scripts/*.py scripts/*.sh 2>/dev/null || echo "Note: Could not make all scripts executable. This is OK."

echo ""
echo "Setup complete! You can now start working on the project."
echo ""
echo "Next steps:"
echo "1. Verify your setup with: python scripts/check_setup.py"
echo "2. Start the API with: python src/main.py"
echo ""
echo "Remember to keep the virtual environment activated:"
echo "  source venv/bin/activate  (Linux/macOS)"
echo "  venv\\Scripts\\activate     (Windows)"
