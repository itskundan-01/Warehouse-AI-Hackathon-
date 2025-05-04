#!/usr/bin/env python3
"""
Script to download and set up the ArcFace model for facial recognition.
For use with the Warehouse AI Hackathon facial recognition system.
"""

import os
import sys
import requests
import shutil
import gdown
from pathlib import Path
from tqdm import tqdm

# Define model paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
MODEL_DIR = PROJECT_ROOT / "models" / "facial"
ARCFACE_MODEL_PATH = MODEL_DIR / "arcface_resnet100.onnx"

# Updated URLs for ArcFace model with current working links
# Primary source - InsightFace official model from InsightFace repo
PRIMARY_URL = "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"

# Secondary source - Direct InsightFace resnet100 model
SECONDARY_URL = "https://onedrive.live.com/download?cid=3DDDA50086C1DCD8&resid=3DDDA50086C1DCD8%21196&authkey=ADgucMNgXChUQR0"

# Third source - Intel Open Zoo Mirror
THIRD_URL = "https://drive.google.com/uc?export=download&id=1Hc5zUfBATaVT2-Zsmk_Y0rYYVJ8CaX8H"

def download_with_progress(url, destination_path):
    """Download a file with progress reporting."""
    try:
        print(f"Downloading from {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file size for progress bar
        total_size = int(response.headers.get('content-length', 0))
        
        with open(destination_path, 'wb') as f, tqdm(
            desc="Downloading",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))
                    
        print(f"Download complete! Saved to {destination_path}")
        return True
    except Exception as e:
        print(f"Error during download: {e}")
        # Remove partial download if it exists
        if os.path.exists(destination_path):
            os.remove(destination_path)
        return False

def download_with_gdown(url, destination_path):
    """Download a file using gdown (better for Google Drive links)."""
    try:
        print(f"Downloading from Google Drive: {url}")
        gdown.download(url, str(destination_path), quiet=False)
        print(f"Download complete! Saved to {destination_path}")
        return True
    except Exception as e:
        print(f"Error during download with gdown: {e}")
        # Remove partial download if it exists
        if os.path.exists(destination_path):
            os.remove(destination_path)
        return False

def main():
    """Main function to download and set up the ArcFace model."""
    # Create the model directory if it doesn't exist
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Check if the model already exists
    if os.path.exists(ARCFACE_MODEL_PATH):
        print(f"ArcFace model already exists at {ARCFACE_MODEL_PATH}")
        user_input = input("Do you want to re-download it? (y/n): ")
        if user_input.lower() != 'y':
            print("Using existing model file.")
            return
    
    # Try downloading from primary URL
    print("Attempting to download ArcFace model...")
    if download_with_progress(PRIMARY_URL, ARCFACE_MODEL_PATH):
        if os.path.exists(ARCFACE_MODEL_PATH) and os.path.getsize(ARCFACE_MODEL_PATH) > 1000000:  # At least 1MB
            print(f"ArcFace model successfully downloaded and installed at: {ARCFACE_MODEL_PATH}")
            print("Your facial recognition system is now configured to use ArcFace!")
            return
        else:
            print("Downloaded file seems invalid or too small.")
    
    # Try secondary URL if primary fails
    print("\nTrying secondary download source...")
    if download_with_progress(SECONDARY_URL, ARCFACE_MODEL_PATH):
        if os.path.exists(ARCFACE_MODEL_PATH) and os.path.getsize(ARCFACE_MODEL_PATH) > 1000000:
            print(f"ArcFace model successfully downloaded and installed at: {ARCFACE_MODEL_PATH}")
            print("Your facial recognition system is now configured to use ArcFace!")
            return
        else:
            print("Downloaded file seems invalid or too small.")
    
    # Try third URL (Google Drive) if secondary fails
    print("\nTrying third download source (Google Drive)...")
    if download_with_gdown(THIRD_URL, ARCFACE_MODEL_PATH):
        if os.path.exists(ARCFACE_MODEL_PATH) and os.path.getsize(ARCFACE_MODEL_PATH) > 1000000:
            print(f"ArcFace model successfully downloaded and installed at: {ARCFACE_MODEL_PATH}")
            print("Your facial recognition system is now configured to use ArcFace!")
            return
        else:
            print("Downloaded file seems invalid or too small.")
    
    # If all automated download attempts fail, provide manual instructions
    print("\n" + "="*80)
    print("DOWNLOAD FAILED: All automatic download attempts failed")
    print("Please try one of the following manual options:")
    print("\n1. Use your web browser to download the ArcFace model from one of these URLs:")
    print(f"   - {PRIMARY_URL}")
    print(f"   - {SECONDARY_URL}")
    print(f"   - https://drive.google.com/file/d/1Hc5zUfBATaVT2-Zsmk_Y0rYYVJ8CaX8H/view?usp=sharing")
    print(f"\n2. Save the downloaded file to: {ARCFACE_MODEL_PATH}")
    print("\n3. Alternatively, use the main model downloader script:")
    print(f"   python {SCRIPT_DIR}/download_models.py --models arcface --force")
    print("="*80)

if __name__ == "__main__":
    main()