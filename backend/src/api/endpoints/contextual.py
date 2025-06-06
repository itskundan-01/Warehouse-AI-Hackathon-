from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
import cv2
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor

# Initialize logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Shared executor for background processing
executor = ThreadPoolExecutor(max_workers=4)

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload video for contextual intelligence analysis."""
    try:
        logger.info(f"Contextual Intelligence - Received video upload: {file.filename}")
        
        # Validate file
        if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            raise HTTPException(status_code=400, detail="Unsupported video format")
        
        if file.size and file.size > 200 * 1024 * 1024:  # 200MB limit
            raise HTTPException(status_code=400, detail="File too large")
        
        # Read video content
        video_content = await file.read()
        
        # Generate processing ID
        processing_id = f"contextual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Start background processing
        asyncio.create_task(process_video_async(video_content, processing_id, file.filename))
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Video uploaded successfully for contextual analysis",
                "processing_id": processing_id,
                "filename": file.filename
            }
        )
        
    except Exception as e:
        logger.error(f"Contextual upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{processing_id}")
async def get_results(processing_id: str):
    """Get contextual analysis results."""
    try:
        # Mock results for demonstration
        mock_results = generate_mock_contextual_results(processing_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "processing_id": processing_id,
                "results": mock_results,
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Contextual results error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def natural_language_query(query_data: Dict[str, Any]):
    """Process natural language query about analyzed videos."""
    try:
        query = query_data.get("query", "")
        processing_ids = query_data.get("processing_ids", [])
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        logger.info(f"Processing NL query: {query}")
        
        # Mock query processing
        processed_query = {
            "intent": "information_retrieval",
            "entities": extract_entities_from_query(query),
            "query_type": classify_query_type(query)
        }
        
        # Mock results
        results = generate_query_results(query, processed_query)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "query": query,
                "processed_query": processed_query,
                "results": results,
                "results_count": len(results),
                "message": f"Found {len(results)} relevant results for your query."
            }
        )
        
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-video")
async def process_contextual_video(
    location: str = Form(...),
    video: UploadFile = File(...)
):
    """
    Process a video file to perform contextual intelligence analysis.
    Returns analysis results with events and natural language queryable content.
    """
    try:
        # Create directory for storing videos
        video_dir = "./data/videos/contextual"
        os.makedirs(video_dir, exist_ok=True)
        
        # Save uploaded video
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        video_filename = f"contextual_{location}_{timestamp}.mp4"
        video_path = f"{video_dir}/{video_filename}"
        
        with open(video_path, "wb") as video_file:
            video_file.write(await video.read())
        
        # Process video in background
        result = await asyncio.get_event_loop().run_in_executor(
            executor, process_video_for_contextual_analysis, video_path, location
        )
        
        return {
            "status": "success",
            "message": "Video processed successfully",
            "data": result,
            "video_file": video_filename
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process video: {str(e)}"
        )

async def process_video_async(video_content: bytes, processing_id: str, filename: str):
    """Process video asynchronously."""
    try:
        logger.info(f"Starting contextual analysis for {processing_id}")
        
        # Simulate processing time
        await asyncio.sleep(2)
        
        # In production, this would perform actual contextual analysis
        # For now, we'll use mock results
        
        logger.info(f"Completed contextual analysis for {processing_id}")
        
    except Exception as e:
        logger.error(f"Async processing error for {processing_id}: {str(e)}")

def generate_mock_contextual_results(processing_id: str) -> Dict[str, Any]:
    """Generate mock contextual analysis results."""
    import random
    
    # Generate realistic mock data
    events = []
    for i in range(random.randint(3, 8)):
        event_types = ["motion_detected", "object_entered", "unusual_activity", "lighting_change", "sound_anomaly"]
        severities = ["low", "medium", "high"]
        
        events.append({
            "id": f"event_{i+1}",
            "type": random.choice(event_types),
            "description": f"Contextual event detected at timestamp {random.randint(5, 120)}s",
            "timestamp": random.randint(5, 120),
            "confidence": random.uniform(0.7, 0.98),
            "severity": random.choice(severities),
            "location": f"Zone {random.choice(['A', 'B', 'C'])}"
        })
    
    return {
        "processing_id": processing_id,
        "status": "completed",
        "summary": {
            "total_events": len(events),
            "motion_frames": random.randint(50, 200),
            "total_objects": random.randint(5, 15),
            "activity_score": random.uniform(0.3, 0.9),
            "average_brightness": random.randint(80, 200),
            "event_types": list(set([event["type"] for event in events])),
            "analysis_duration": random.uniform(2.5, 8.3)
        },
        "events": events,
        "timeline": generate_timeline_data(events),
        "metadata": {
            "video_duration": random.uniform(30, 180),
            "fps": 30,
            "resolution": "1920x1080",
            "processed_frames": random.randint(900, 5400)
        },
        "location": f"Warehouse Section {random.choice(['North', 'South', 'East', 'West'])}",
        "timestamp": datetime.now().isoformat()
    }

def generate_timeline_data(events: List[Dict]) -> List[Dict]:
    """Generate timeline data from events."""
    timeline = []
    for event in events:
        timeline.append({
            "time": event["timestamp"],
            "event": event["type"],
            "description": event["description"],
            "severity": event["severity"]
        })
    
    return sorted(timeline, key=lambda x: x["time"])

def extract_entities_from_query(query: str) -> List[str]:
    """Extract entities from natural language query."""
    entities = []
    query_lower = query.lower()
    
    # Simple entity extraction
    if "people" in query_lower or "person" in query_lower:
        entities.append("person")
    if "motion" in query_lower or "movement" in query_lower:
        entities.append("motion")
    if "object" in query_lower or "item" in query_lower:
        entities.append("object")
    if "event" in query_lower or "activity" in query_lower:
        entities.append("event")
    if "time" in query_lower or "when" in query_lower:
        entities.append("temporal")
    
    return entities

def classify_query_type(query: str) -> str:
    """Classify the type of query."""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["how many", "count", "number"]):
        return "quantitative"
    elif any(word in query_lower for word in ["when", "what time", "timestamp"]):
        return "temporal"
    elif any(word in query_lower for word in ["what", "which", "describe"]):
        return "descriptive"
    elif any(word in query_lower for word in ["where", "location", "zone"]):
        return "spatial"
    else:
        return "general"

def generate_query_results(query: str, processed_query: Dict) -> List[Dict]:
    """Generate mock results for natural language query."""
    results = []
    
    # Generate relevant mock results based on query type
    if "people" in query.lower():
        results.extend([
            {"type": "detection", "description": "3 people detected between 15-45 seconds", "timestamp": 15},
            {"type": "detection", "description": "1 person detected at 78 seconds", "timestamp": 78}
        ])
    
    if "motion" in query.lower():
        results.extend([
            {"type": "motion", "description": "Significant motion detected in Zone A", "timestamp": 23},
            {"type": "motion", "description": "Motion detected near entrance", "timestamp": 67}
        ])
    
    if "event" in query.lower():
        results.extend([
            {"type": "event", "description": "Unusual activity detected", "timestamp": 45},
            {"type": "event", "description": "Object left unattended", "timestamp": 89}
        ])
    
    # Default results if no specific matches
    if not results:
        results = [
            {"type": "general", "description": "Analysis completed with 8 events detected", "timestamp": 0},
            {"type": "general", "description": "Motion detected in multiple zones", "timestamp": 30}
        ]
    
    return results

def process_video_for_contextual_analysis(video_path: str, location: str):
    """
    Process video file for contextual intelligence analysis.
    Detects events, behaviors, and generates queryable content.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    results = []
    frame_count = 0
    detected_events = {}
    
    # Event types to detect
    event_types = [
        "person_movement", "vehicle_entry", "object_placement", 
        "crowding", "unusual_activity", "security_breach"
    ]
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process every 30th frame (approximately 1 frame per second for 30fps video)
        if frame_count % 30 == 0:
            timestamp_seconds = frame_count / fps
            
            # Simulate contextual analysis
            events_detected = analyze_frame_for_events(frame, timestamp_seconds)
            
            for event in events_detected:
                event_id = f"{event['type']}_{frame_count}"
                
                result = {
                    "timestamp": timestamp_seconds,
                    "frame_number": frame_count,
                    "event_id": event_id,
                    "event_type": event["type"],
                    "confidence": event["confidence"],
                    "description": event["description"],
                    "location": location,
                    "severity": event.get("severity", "normal"),
                    "bbox": event.get("bbox", [0, 0, 0, 0]),
                    "context": event.get("context", "")
                }
                results.append(result)
                
                # Track event types
                if event["type"] not in detected_events:
                    detected_events[event["type"]] = []
                detected_events[event["type"]].append(result)
        
        frame_count += 1
    
    cap.release()
    
    # Generate summary with natural language queryable content
    summary = {
        "location": location,
        "video_file": video_path,
        "total_frames": total_frames,
        "fps": fps,
        "duration_seconds": total_frames / fps,
        "detected_events": detected_events,
        "all_events": results,
        "event_types": list(detected_events.keys()),
        "total_events": len(results),
        "timestamp": datetime.utcnow(),
        "processing_type": "contextual_analysis",
        "queryable_content": generate_queryable_content(results, location)
    }
    
    return summary

def analyze_frame_for_events(frame, timestamp):
    """
    Analyze a single frame for contextual events.
    This is a mock implementation - in production would use actual AI models.
    """
    import random
    
    events = []
    
    # Simulate event detection with random events
    if random.random() < 0.3:  # 30% chance of detecting an event
        event_types = [
            {
                "type": "person_movement", 
                "description": "Person detected moving through warehouse area",
                "severity": "normal"
            },
            {
                "type": "vehicle_entry", 
                "description": "Vehicle detected entering warehouse premises",
                "severity": "normal"
            },
            {
                "type": "object_placement", 
                "description": "Objects being placed or moved in storage area",
                "severity": "normal"
            },
            {
                "type": "crowding", 
                "description": "Multiple people gathered in one area",
                "severity": "medium"
            },
            {
                "type": "unusual_activity", 
                "description": "Suspicious movement pattern detected",
                "severity": "high"
            }
        ]
        
        selected_event = random.choice(event_types)
        events.append({
            "type": selected_event["type"],
            "confidence": random.uniform(0.7, 0.95),
            "description": selected_event["description"],
            "severity": selected_event["severity"],
            "bbox": [
                random.randint(0, 100), 
                random.randint(0, 100), 
                random.randint(100, 200), 
                random.randint(100, 200)
            ],
            "context": f"Event occurred at timestamp {timestamp:.2f}s"
        })
    
    return events

def generate_queryable_content(events, location):
    """
    Generate natural language queryable content from detected events.
    """
    content = {
        "summary": f"Video analysis completed for {location}. {len(events)} events detected.",
        "events_by_type": {},
        "timeline": [],
        "searchable_descriptions": []
    }
    
    for event in events:
        event_type = event["event_type"]
        if event_type not in content["events_by_type"]:
            content["events_by_type"][event_type] = []
        
        content["events_by_type"][event_type].append({
            "timestamp": event["timestamp"],
            "description": event["description"],
            "confidence": event["confidence"]
        })
        
        content["timeline"].append(f"At {event['timestamp']:.1f}s: {event['description']}")
        content["searchable_descriptions"].append(event["description"])
    
    return content