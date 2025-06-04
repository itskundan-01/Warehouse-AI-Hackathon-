#!/usr/bin/env python3
"""
Script to check the WarehouseVision AI setup
Cross-platform compatible (Linux/macOS)
"""
import sys
import os
import importlib
import platform
import subprocess
import shutil

def check_module_availability(module_name):
    """Check if a Python module is available"""
    # Add Docker check capability
    if module_name == "docker":
        docker_path = shutil.which("docker")
        if docker_path:
            try:
                version_output = subprocess.check_output(["docker", "--version"], 
                                                        stderr=subprocess.STDOUT,
                                                        universal_newlines=True)
                print(f"✅ {module_name} is installed ({version_output.strip()})")
                return True
            except (subprocess.SubprocessError, OSError):
                print(f"❌ {module_name} is installed but not running properly")
                return False
        else:
            print(f"❌ {module_name} is not installed")
            return False
    
    # Add Docker Compose check capability
    if module_name == "docker-compose":
        compose_path = shutil.which("docker-compose")
        if compose_path:
            try:
                version_output = subprocess.check_output(["docker-compose", "--version"], 
                                                       stderr=subprocess.STDOUT,
                                                       universal_newlines=True)
                print(f"✅ {module_name} is installed ({version_output.strip()})")
                return True
            except (subprocess.SubprocessError, OSError):
                print(f"❌ {module_name} is installed but not running properly")
                return False
        else:
            # Try Docker Compose V2 (part of docker CLI)
            try:
                version_output = subprocess.check_output(["docker", "compose", "version"], 
                                                       stderr=subprocess.STDOUT,
                                                       universal_newlines=True)
                print(f"✅ Docker Compose V2 is installed ({version_output.strip()})")
                return True
            except (subprocess.SubprocessError, OSError):
                print(f"❌ {module_name} is not installed")
                return False
    
    # Standard module checking
    try:
        # Special case for opencv-python which is imported as cv2
        if module_name == "opencv-python":
            module = importlib.import_module("cv2")
        else:
            module = importlib.import_module(module_name)
        
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {module_name} is installed (version: {version})")
        return True
    except ImportError:
        print(f"❌ {module_name} is not installed")
        return False
    except Exception as e:
        print(f"⚠️ {module_name} had an error: {str(e)}")
        return False

def check_opencv_version():
    """Check OpenCV version and provide more detailed information"""
    try:
        import cv2
        print(f"✅ OpenCV is installed (version: {cv2.__version__})")
        
        # Check if OpenCV was built with optimizations
        features = []
        if hasattr(cv2, 'getBuildInformation'):
            build_info = cv2.getBuildInformation()
            if 'NEON:' in build_info and 'YES' in build_info.split('NEON:')[1].split('\n')[0]:
                features.append("NEON")
            if 'AVX:' in build_info and 'YES' in build_info.split('AVX:')[1].split('\n')[0]:
                features.append("AVX")
            if 'OpenCL:' in build_info and 'YES' in build_info.split('OpenCL:')[1].split('\n')[0]:
                features.append("OpenCL")
            
            if features:
                print(f"   - Built with optimizations: {', '.join(features)}")
            else:
                print("   - No hardware optimizations detected")
        
        return True
    except ImportError:
        print("❌ OpenCV is not installed")
        return False

def check_virtual_env():
    """Check if running in a virtual environment"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def main():
    print("\n===== CHECKING WAREHOUSEVISION AI SETUP =====\n")
    
    # Print Python information
    print(f"Python version: {platform.python_version()}")
    print(f"Python implementation: {platform.python_implementation()}")
    print(f"System: {platform.system()} {platform.release()}")
    
    # Check virtual environment
    if check_virtual_env():
        print(f"Virtual environment: ✅ Active ({sys.prefix})")
    else:
        print("Virtual environment: ❌ Not active")
        print("Warning: It's recommended to run in a virtual environment.")
    print()

    # Check core modules
    print("Checking core dependencies:")
    core_modules = [
        "fastapi", "uvicorn", "pydantic", 
        "python-dotenv", "redis", "celery"
    ]
    
    for module in core_modules:
        check_module_availability(module)
    
    # Try to import project modules
    print("\nChecking project modules:")
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from src.core.utils import get_logger
        logger = get_logger("setup_check")
        logger.info("Logger initialized successfully!")
        print("✅ Project modules are working correctly")
    except Exception as e:
        print(f"❌ Error importing project modules: {str(e)}")
    
    # Check ML libraries (optional)
    print("\nChecking ML libraries (some may be missing - that's OK for now):")
    ml_modules = ["opencv-python"]
    
    for module in ml_modules:
        check_module_availability(module)
    
    # Check OpenCV version
    print("\nChecking OpenCV version:")
    check_opencv_version()
    
    # Check Docker if available (optional)
    print("\nChecking Docker (optional):")
    check_module_availability("docker")
    check_module_availability("docker-compose")
    
    print("\n===== SETUP CHECK COMPLETE =====\n")

if __name__ == "__main__":
    main()
