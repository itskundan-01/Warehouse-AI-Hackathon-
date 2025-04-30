#!/usr/bin/env python3
"""
Windows compatible setup script for WarehouseVision AI
"""
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(command, error_message=None):
    """Run a command and return success status"""
    try:
        subprocess.run(command, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        if error_message:
            print(error_message)
        return False

def main():
    print("Setting up WarehouseVision AI development environment...")
    
    # Check Python version
    python_version = platform.python_version()
    print(f"Python version: {python_version}")
    
    major, minor, _ = map(int, python_version.split('.'))
    if major < 3 or (major == 3 and minor < 10):
        print("Warning: This project is recommended to use Python 3.10+")
        response = input("Continue with Python {}? (y/n): ".format(python_version))
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(1)
    
    # Create virtual environment
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        if not run_command("python -m venv venv", 
                         "Error: Failed to create virtual environment."):
            sys.exit(1)
    else:
        print("Virtual environment already exists.")
    
    # Activate virtual environment and install dependencies
    print("Installing dependencies...")
    
    # Windows uses different activation
    activate_script = os.path.join("venv", "Scripts", "activate")
    pip_cmd = os.path.join("venv", "Scripts", "pip")
    
    # Install required packages
    if run_command(f"{pip_cmd} install --upgrade pip"):
        run_command(f"{pip_cmd} install -r requirements.txt")
    
    # Create necessary directories
    for directory in ["data/images", "data/videos", "models/yolo", "models/ocr", "models/facial", "logs"]:
        os.makedirs(directory, exist_ok=True)
    
    # Create .env file
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("Created .env file from example.")
        else:
            env_content = """# Environment configuration
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
"""
            with open(".env", "w") as f:
                f.write(env_content)
            print("Created basic .env file.")
    else:
        print(".env file already exists.")

    print("\nSetup complete! You can now start working on the project.")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    print("   venv\\Scripts\\activate")
    print("2. Verify your setup with:")
    print("   python scripts\\check_setup.py")
    print("3. Start the API with:")
    print("   python src\\main.py")

if __name__ == "__main__":
    main()
