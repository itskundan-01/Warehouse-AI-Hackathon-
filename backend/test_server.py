#!/usr/bin/env python3
"""
Simple test server for plate detection functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
from plate_detector import PlateDetector
import tempfile
import aiofiles

app = FastAPI(title="Plate Detection Test API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global detector instance
detector = None

@app.on_event("startup")
async def startup_event():
    """Initialize the plate detector on startup"""
    global detector
    try:
        detector = PlateDetector()
        print("PlateDetector initialized successfully")
    except Exception as e:
        print(f"Failed to initialize PlateDetector: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "detector_ready": detector is not None
    }

@app.post("/detect")
async def detect_plates(file: UploadFile = File(...)):
    """
    Detect plates in uploaded image or video
    """
    if not detector:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Detector not initialized"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process the file
        result = detector.process_file(temp_file_path)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return {
            "success": True,
            "filename": file.filename,
            "result": result
        }
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detection failed: {str(e)}"
        )

@app.get("/statistics")
async def get_statistics():
    """Get basic statistics"""
    return {
        "detector_ready": detector is not None,
        "status": "Test API - statistics not implemented"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
