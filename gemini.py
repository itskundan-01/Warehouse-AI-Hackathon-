import google.generativeai as genai
import cv2
import os
from PIL import Image
import numpy as np
import tempfile
import time
import sys
sys.path.append("..")  # or the correct relative path to your project root
from gemini import gemini_ocr_plate_image

def configure_gemini(api_key: str):
    """Configure Gemini API key."""
    genai.configure(api_key=api_key)

def gemini_ocr_plate_image(plate_img, prompt="Read the vehicle license plate number only. Return only the text.", model_name="gemini-1.5-flash"):
    """
    Takes a cropped license plate image (numpy array), sends it to Gemini API, and returns the detected text.
    model_name: Use 'gemini-1.5-flash' or 'gemini-2.0-flash' if supported.
    """
    # Convert numpy array to PIL Image
    if isinstance(plate_img, np.ndarray):
        plate_img = cv2.cvtColor(plate_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(plate_img)
    else:
        pil_img = plate_img
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([
            prompt,
            pil_img
        ])
        text = response.text.strip()
        return text
    except Exception as e:
        print(f"Gemini OCR error: {e}")
        return None

def gemini_vehicle_image_analysis(image_path, api_key, model_name="gemini-2.0-flash"):
    """
    Analyze a single image or multi-vehicle image for vehicle type and number plate using Gemini.
    Returns a list of dicts: [{vehicle_type, license_plate, status}]
    """
    configure_gemini(api_key)
    img = cv2.imread(image_path)
    if img is None:
        return {"error": f"Could not read image: {image_path}"}
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    prompt = (
        "You are a vehicle recognition expert. In this image, detect all vehicles. "
        "For each vehicle, provide: (1) the type (car, truck, etc.), (2) the license plate number if visible, "
        "(3) if the number plate is not detected, say 'not detected', and (4) if the number plate is too blurry or not visible, say 'not clear'. "
        "Index the vehicles if there are multiple. Return a JSON list with keys: index, vehicle_type, license_plate, status."
    )
    model = genai.GenerativeModel(model_name)
    response = model.generate_content([prompt, pil_img])
    print(response.text)  # Ensure output is printed for CLI use
    return response.text

def gemini_vehicle_video_analysis(video_path, api_key, model_name="gemini-2.0-flash", max_frames=10):
    """
    Analyze a video for vehicles and number plates using Gemini. Samples up to max_frames evenly spaced frames for efficiency.
    Returns a summary of all unique vehicles detected with their type and license plate.
    """
    configure_gemini(api_key)
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        print("Could not read video or video is empty.")
        return []
    frame_indices = np.linspace(0, total_frames - 1, min(max_frames, total_frames), dtype=int)
    seen_plates = set()
    vehicle_results = []
    prompt = (
        "You are a vehicle recognition expert. In this frame, detect all vehicles. "
        "For each vehicle, provide: (1) the type (car, truck, etc.), (2) the license plate number if visible, "
        "(3) if the number plate is not detected, say 'not detected', and (4) if the number plate is too blurry or not visible, say 'not clear'. "
        "Index the vehicles if there are multiple. Return a JSON list with keys: index, vehicle_type, license_plate, status."
    )
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, pil_img], request_options={"timeout": 300})
        try:
            import json
            frame_vehicles = json.loads(response.text)
            for v in frame_vehicles:
                plate = v.get("license_plate", "").strip().lower()
                if plate and plate not in seen_plates and plate not in ["not detected", "not clear"]:
                    seen_plates.add(plate)
                    vehicle_results.append(v)
                elif plate in ["not detected", "not clear"]:
                    vehicle_results.append(v)
        except Exception:
            vehicle_results.append({"frame": int(idx), "raw_response": response.text})
    cap.release()
    print(vehicle_results)
    return vehicle_results

if __name__ == "__main__":
    # Example usage: python gemini.py /path/to/plate.jpg
    import sys
    if len(sys.argv) < 4:
        print("Usage: python gemini.py <API_KEY> <image|video> <file_path> [model_name]")
        sys.exit(1)
    api_key = sys.argv[1]
    mode = sys.argv[2]
    file_path = sys.argv[3]
    model_name = sys.argv[4] if len(sys.argv) > 4 else "gemini-2.0-flash"
    if mode == "image":
        result = gemini_vehicle_image_analysis(file_path, api_key, model_name)
    elif mode == "video":
        result = gemini_vehicle_video_analysis(file_path, api_key, model_name)
    else:
        print("Mode must be 'image' or 'video'.")