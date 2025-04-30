#!/bin/bash

# Script to install dependencies incrementally
echo "Installing WarehouseVision AI dependencies incrementally..."

# Make sure we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Error: Virtual environment not activated."
    echo "Please activate your virtual environment first with: source venv/bin/activate"
    exit 1
fi

# Function to install package with error handling
install_package() {
    package=$1
    echo "Installing $package..."
    pip install --timeout 300 $package
    if [ $? -ne 0 ]; then
        echo "Failed to install $package. Retrying with --no-cache-dir..."
        pip install --timeout 300 --no-cache-dir $package
        if [ $? -ne 0 ]; then
            echo "Warning: Failed to install $package. Continuing with other packages."
        else
            echo "Successfully installed $package on retry."
        fi
    else
        echo "Successfully installed $package."
    fi
    echo ""
}

# Step 1: Core web packages
echo "==== Installing core web packages ===="
install_package "fastapi>=0.100.0"
install_package "uvicorn>=0.22.0"
install_package "pydantic>=2.0.0"

# Step 2: Database packages
echo "==== Installing database packages ===="
install_package "sqlalchemy>=2.0.0"
install_package "alembic>=1.11.1"
install_package "python-dotenv>=1.0.0"
install_package "psycopg2-binary>=2.9.6"

# Step 3: Messaging and cache packages
echo "==== Installing messaging and cache packages ===="
install_package "redis>=4.6.0"
install_package "celery>=5.3.1"

# Step 4: Security packages
echo "==== Installing security packages ===="
install_package "python-jose>=3.3.0"
install_package "passlib>=1.7.4"
install_package "cryptography>=41.0.1"
install_package "pydantic-settings>=2.0.1"

# Step 5: Testing packages
echo "==== Installing testing packages ===="
install_package "pytest>=7.3.1"
install_package "pytest-cov>=4.1.0"
install_package "httpx>=0.24.1"

# Step 6: ELK stack integration
echo "==== Installing ELK stack integration ===="
install_package "elasticsearch>=8.8.0"
install_package "python-logstash>=0.4.8"

# Step 7: Computer vision packages (optional)
echo "==== Installing computer vision packages (may be skipped) ===="
echo "Note: These packages are large and may be installed later when needed."
echo "Attempting to install OpenCV (this may take some time)..."
pip install --timeout 600 opencv-python
if [ $? -ne 0 ]; then
    echo "Warning: OpenCV installation failed. You can try installing it later with:"
    echo "pip install --timeout 600 opencv-python"
else
    echo "Successfully installed OpenCV."
fi

echo ""
echo "Installation complete! Some packages may have been skipped due to compatibility issues."
echo "You can check your installation with: python scripts/check_setup.py"

# Inform about PyTorch
echo ""
echo "Note: PyTorch was not installed as it doesn't support Python 3.13 yet."
echo "If you need PyTorch, consider using Python 3.10 or 3.11 in a separate environment."
