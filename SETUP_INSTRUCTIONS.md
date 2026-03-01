# Quick Setup Instructions

## 1. Environment Setup

Copy the `.env` file and add your API keys:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your actual API keys:
- `ROBOFLOW_API_KEY`: Get from Roboflow dashboard
- `GEMINI_API_KEY`: Get from Google AI Studio

## 2. Install Dependencies

For gunny bag counting, you also need:
```bash
pip install inference-sdk  # Roboflow inference
```

For Gemini plate detection:
```bash
pip install google-generativeai
```

## 3. Usage

### Gunny Bag Counter
- **Requires**: Video files (.mp4, .avi, .mov, .mkv, .webm)
- **Uses**: `gunny_bag_line_counter_local.py` with Roboflow pipeline
- **Output**: IN/OUT counts, net count, processed frames

### License Plate Detection  
- **Supports**: Both images and videos
- **Uses**: `gemini.py` with Google Gemini AI
- **Fallback**: Original plate detector for images only
- **Output**: License plates, vehicle types, confidence scores

## 4. API Endpoints

- `POST /api/process/gunny_bag_counter` - Process video for bag counting
- `POST /api/process/license_plate` - Process image/video for license plates
- `GET /api/status` - Check system status

The system will automatically:
1. Use the correct processing file based on the component selected
2. Handle both images and videos appropriately
3. Provide meaningful error messages for unsupported formats
