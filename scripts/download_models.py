#!/usr/bin/env python3
"""
Download facial recognition models for the Warehouse Vision AI system.

This script downloads pre-trained models for facial recognition
and places them in the appropriate directory structure.
"""

import os
import sys
import requests
import logging
import hashlib
from pathlib import Path
import argparse
import tqdm

# Import gdown for Google Drive downloads
try:
    import gdown
    GDOWN_AVAILABLE = True
except ImportError:
    GDOWN_AVAILABLE = False
    logging.warning("gdown package not found. Google Drive downloads may not work. Install with 'pip install gdown'")

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Model information with URLs and checksums
MODEL_INFO = {
    "arcface": {
        "url": "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip",
        "alternate_url": "https://onedrive.live.com/download?cid=3DDDA50086C1DCD8&resid=3DDDA50086C1DCD8%21196&authkey=ADgucMNgXChUQR0",
        "gdrive_url": "https://drive.google.com/uc?export=download&id=1Hc5zUfBATaVT2-Zsmk_Y0rYYVJ8CaX8H",
        "filename": "arcface_resnet100.onnx",
        "md5": None,  # This is a placeholder - should be replaced with actual MD5
        "size": 248151738,  # Approximate size in bytes
    },
    "insightface": {
        "url": "https://storage.googleapis.com/insightface-models/buffalo_l.onnx",
        "alternate_url": "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip",
        "gdrive_url": None,  # Add Google Drive URL if available
        "filename": "insightface.onnx",
        "md5": None,  # Add when actual checksum is known
        "size": 243895572,  # Approximate size in bytes
    },
    "facenet": {
        "url": "https://storage.googleapis.com/facenet-models/facenet.pb",
        "alternate_url": "https://github.com/davidsandberg/facenet/releases/download/v1.0.0/20180402-114759.zip",
        "gdrive_url": None,  # Add Google Drive URL if available
        "filename": "facenet.pb",
        "md5": None,  # Add when actual checksum is known
        "size": 87910968,  # Approximate size in bytes
    }
}

def get_project_root():
    """Get the absolute path to the project root directory."""
    # This script is in the 'scripts' directory, so we need to go up one level
    return Path(__file__).parent.parent.absolute()

def get_models_directory():
    """Get the absolute path to the models directory."""
    root_dir = get_project_root()
    models_dir = root_dir / "models" / "facial"
    return models_dir

def ensure_directory_exists(directory):
    """Ensure that the specified directory exists."""
    if not directory.exists():
        logger.info(f"Creating directory: {directory}")
        directory.mkdir(parents=True, exist_ok=True)

def download_file(url, destination_path, expected_size=None):
    """
    Download a file from a URL to the specified destination path.
    
    Args:
        url: URL of the file to download
        destination_path: Path where the file should be saved
        expected_size: Expected file size in bytes for progress bar
    
    Returns:
        True if download was successful, False otherwise
    """
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            
            # Get the file size from headers or use expected_size
            file_size = int(response.headers.get('content-length', 0)) or expected_size or 0
            
            logger.info(f"Downloading {url} to {destination_path} ({file_size / 1024 / 1024:.1f} MB)")
            
            # Use tqdm for progress bar
            with open(destination_path, 'wb') as f, tqdm.tqdm(
                desc="Downloading",
                total=file_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
            
            return True
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        if destination_path.exists():
            logger.info(f"Removing partial download: {destination_path}")
            destination_path.unlink()
        return False

def download_file_gdrive(gdrive_url, destination_path):
    """
    Download a file from Google Drive using gdown.
    
    Args:
        gdrive_url: Google Drive URL of the file to download
        destination_path: Path where the file should be saved
    
    Returns:
        True if download was successful, False otherwise
    """
    if not GDOWN_AVAILABLE:
        logger.error("gdown is not available. Cannot download from Google Drive.")
        return False
    
    try:
        logger.info(f"Downloading from Google Drive: {gdrive_url} to {destination_path}")
        gdown.download(gdrive_url, str(destination_path), quiet=False)
        return True
    except Exception as e:
        logger.error(f"Error downloading from Google Drive: {e}")
        return False

def verify_checksum(file_path, expected_md5):
    """
    Verify the MD5 checksum of a file.
    
    Args:
        file_path: Path to the file
        expected_md5: Expected MD5 checksum
    
    Returns:
        True if checksum matches, False otherwise
    """
    if not expected_md5:
        logger.warning("No checksum provided for verification, skipping check")
        return True
        
    logger.info(f"Verifying checksum for {file_path}")
    
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    
    calculated_md5 = md5_hash.hexdigest()
    
    if calculated_md5 == expected_md5:
        logger.info("Checksum verification passed")
        return True
    else:
        logger.error(f"Checksum verification failed. Expected: {expected_md5}, Got: {calculated_md5}")
        return False

def download_models(models=None, force=False):
    """
    Download the specified models.
    
    Args:
        models: List of model names to download, or None for all
        force: If True, download even if the file already exists
    """
    models_dir = get_models_directory()
    ensure_directory_exists(models_dir)
    
    # If no specific models are requested, download all
    if not models:
        models = list(MODEL_INFO.keys())
    
    for model_name in models:
        if model_name not in MODEL_INFO:
            logger.warning(f"Unknown model: {model_name}")
            continue
        
        model_data = MODEL_INFO[model_name]
        file_path = models_dir / model_data["filename"]
        
        # Skip if file already exists and force is False
        if file_path.exists() and not force:
            logger.info(f"Model {model_name} already exists at {file_path}. Use --force to redownload.")
            continue
        
        logger.info(f"Downloading {model_name} model...")
        success = download_file(model_data["url"], file_path, model_data["size"])
        
        # If primary URL fails and an alternate URL exists, try that
        if not success and "alternate_url" in model_data:
            logger.info(f"Primary download failed. Trying alternate URL for {model_name}...")
            success = download_file(model_data["alternate_url"], file_path, model_data["size"])
        
        # If alternate URL fails and a Google Drive URL exists, try that
        if not success and "gdrive_url" in model_data and model_data["gdrive_url"]:
            logger.info(f"Alternate download failed. Trying Google Drive URL for {model_name}...")
            success = download_file_gdrive(model_data["gdrive_url"], file_path)
        
        if success:
            if verify_checksum(file_path, model_data["md5"]):
                logger.info(f"Successfully downloaded {model_name} to {file_path}")
            else:
                logger.warning(f"Checksum verification failed for {model_name}. The file may be corrupted.")
                if not force:
                    logger.info("Removing potentially corrupted file")
                    file_path.unlink(missing_ok=True)
        else:
            logger.error(f"Failed to download {model_name}")

def main():
    parser = argparse.ArgumentParser(description="Download facial recognition models")
    parser.add_argument("--models", nargs="+", choices=list(MODEL_INFO.keys()), 
                        help="Specific models to download")
    parser.add_argument("--force", action="store_true", 
                        help="Force download even if models already exist")
    parser.add_argument("--list", action="store_true", 
                        help="List available models without downloading")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available models:")
        for model_name, info in MODEL_INFO.items():
            print(f"  - {model_name} ({info['filename']}, ~{info['size'] / 1024 / 1024:.1f} MB)")
        return
    
    logger.info("Starting model download process")
    download_models(args.models, args.force)
    logger.info("Model download process complete")

if __name__ == "__main__":
    main()