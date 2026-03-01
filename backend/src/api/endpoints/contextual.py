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
from ultralytics import YOLO

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
            "success": True,
            "status": "success",
            "message": "Video processed successfully",
            "processing_id": result.get("processing_id", f"contextual_{location}_{timestamp}"),
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
    """Extract keywords/entities from natural language query."""
    keywords = []
    for word in ['motion', 'object', 'enter', 'anomaly', 'detected']:
        if word in query.lower():
            keywords.append(word)
    return keywords

def classify_query_type(query: str) -> str:
    """Classify query type based on keywords."""
    q = query.lower()
    if q.startswith('show') or 'list' in q:
        return 'list_events'
    return 'information_retrieval'

def generate_query_results(query: str, processed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate results for a natural language query by filtering event logs."""
    results = []
    pids = processed_query.get('entities') or []  # using entities as identifiers
    # If no specific IDs, scan all JSON logs
    files = os.listdir('data/contextual')
    for fname in files:
        if fname.endswith('.json'):
            with open(f'data/contextual/{fname}') as f:
                data = json.load(f)
            for ev in data.get('events', []):
                if not processed_query['entities']:
                    results.append(ev)
                else:
                    # filter by event type keywords
                    if any(k in ev.get('type', '').lower() or k in ev.get('description','').lower() for k in processed_query['entities']):
                        results.append(ev)
    return results

def process_video_for_contextual_analysis(video_path: str, location: str):
    """
    Process video for contextual intelligence: detect motion and objects, log events to JSON.
    """
    from datetime import datetime
    processing_id = f"contextual_{location}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frame_skip = int(fps)
    fgbg = cv2.createBackgroundSubtractorMOG2()
    model = YOLO('yolov8n.pt')
    events = []
    frame_idx = 0
    event_counter = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_skip == 0:
            timestamp = frame_idx / fps
            # motion detection
            mask = fgbg.apply(frame)
            motion_pixels = np.sum(mask > 244)
            if motion_pixels > frame.shape[0] * frame.shape[1] * 0.01:
                event_counter += 1
                events.append({
                    'id': f'event_{event_counter}',
                    'type': 'motion_detected',
                    'description': f'Motion detected at {timestamp:.2f}s',
                    'timestamp': timestamp,
                    'confidence': None,
                    'severity': 'medium',
                    'location': location
                })
            # object detection
            results = model(frame)
            for res in results:
                for box in res.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    label = model.names[cls]
                    if conf > 0.5:
                        event_counter += 1
                        events.append({
                            'id': f'event_{event_counter}',
                            'type': 'object_detected',
                            'description': f"{label} detected at {timestamp:.2f}s",
                            'timestamp': timestamp,
                            'confidence': conf,
                            'severity': 'high' if conf > 0.7 else 'low',
                            'location': location,
                            'object': label
                        })
        frame_idx += 1
    cap.release()
    # save events
    os.makedirs('data/contextual', exist_ok=True)
    filepath = f'data/contextual/{processing_id}.json'
    with open(filepath, 'w') as f:
        json.dump({'processing_id': processing_id, 'status': 'completed', 'events': events}, f, default=str)
    return {'processing_id': processing_id, 'status': 'completed', 'events': events}


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