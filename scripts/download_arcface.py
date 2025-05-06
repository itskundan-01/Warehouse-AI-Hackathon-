#!/usr/bin/env python3
"""
Script to download the ArcFace model for facial recognition.
"""
import os
import sys
import requests
import gdown
from pathlib import Path
import shutil
import tempfile
import hashlib
import zipfile

def download_file(url, output_path):
    """Download a file from a URL with progress indication."""
    try:
        print(f"Downloading from {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        downloaded = 0
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    percent = downloaded / total_size * 100 if total_size > 0 else 0
                    print(f"\rDownloaded: {downloaded} / {total_size} bytes ({percent:.2f}%)", end="")
        print()
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def main():
    # Define paths
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    models_dir = project_root / "models" / "facial"
    arcface_model_path = models_dir / "arcface_resnet100.onnx"
    
    # Create models directory if it doesn't exist
    os.makedirs(models_dir, exist_ok=True)
    
    # Remove existing corrupted model file if it exists
    if os.path.exists(arcface_model_path):
        print(f"Removing existing model file: {arcface_model_path}")
        os.remove(arcface_model_path)
    
    # Define model sources - URLs to try in order
    sources = [
        # InsightFace source 1
        "https://insightface.ai/media/datasets/arcface_resnet100.onnx",
        # InsightFace source 2 (zip file containing model) 
        "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip",
        # Alternate source (IntelliFactory mirror)
        "https://storage.intellifactory.com/models/arcface_resnet100.onnx"
    ]
    
    # Try each source in order
    for idx, source in enumerate(sources):
        print(f"Attempt {idx+1}/{len(sources)}: {source}")
        
        # Create a temporary directory for processing downloads
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / os.path.basename(source)
            
            # Download the file
            success = download_file(source, temp_file)
            if not success:
                continue
                
            # If it's a zip file, extract it
            if source.endswith(".zip"):
                try:
                    print(f"Extracting zip file: {temp_file}")
                    with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                        
                    # Look for the model file in the extracted contents
                    model_candidates = list(Path(temp_dir).rglob("*.onnx"))
                    if model_candidates:
                        # Use the first model file found
                        extracted_model = model_candidates[0]
                        print(f"Found model in zip: {extracted_model}")
                        shutil.copy(extracted_model, arcface_model_path)
                    else:
                        print("No ONNX model found in the zip file")
                        continue
                except Exception as e:
                    print(f"Error extracting zip file: {e}")
                    continue
            else:
                # Direct model file
                shutil.copy(temp_file, arcface_model_path)
            
            # Verify the file exists and has a reasonable size
            if os.path.exists(arcface_model_path) and os.path.getsize(arcface_model_path) > 10000000:
                print(f"Successfully downloaded ArcFace model to {arcface_model_path}")
                print(f"Model file size: {os.path.getsize(arcface_model_path) / (1024*1024):.2f} MB")
                return 0
    
    # If we get here, all sources failed
    print("All download attempts failed.")
    print("\nPlease try manually downloading the ArcFace model from:")
    print("1. https://github.com/deepinsight/insightface/tree/master/model_zoo")
    print("2. https://insightface.ai/models")
    print("\nPlace the downloaded file at: " + str(arcface_model_path))
    return 1

if __name__ == "__main__":
    sys.exit(main())