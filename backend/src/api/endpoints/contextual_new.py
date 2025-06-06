"""
API endpoints for Contextual Intelligence module.
Provides endpoints for real-time video analysis and event querying.
"""
from fastapi import APIRouter, Query, Form, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from datetime import datetime
from typing import List, Dict, Any, Optional
import cv2
import asyncio
import json
import os
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from src.database import db
from src.config.logging_config import get_logger

# Create router
router = APIRouter()
logger = get_logger(__name__)

# Thread pool for background processing
executor = ThreadPoolExecutor(max_workers=4)


@router.get("/")
async def contextual_root():
    """
    Root endpoint for contextual intelligence.
    """
    return {
        "message": "Contextual Intelligence module API",
        "status": "Active",
        "capabilities": [
            "Video contextual analysis",
            "Event detection and classification",
            "Natural language querying",
            "Real-time streaming analysis"
        ]
    }


@router.post("/query")
async def run_contextual_query(
    query: str = Query(..., description="Natural language query to process"),
    location: Optional[str] = Query(None, description="Filter by location"),
    start_time: Optional[str] = Query(None, description="Start time filter (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time filter (ISO format)")
):
    """Run a natural language query against video data."""
    try:
        # Import here to avoid circular imports
        from src.modules.context_intelligence.video_analyzer import QueryProcessor
        
        # Initialize query processor
        query_processor = QueryProcessor()
        
        # Process the natural language query
        processed_query = query_processor.process_query(query)
        
        # Search for relevant events in database
        collection = db["contextual_events"]
        
        # Build search filters
        filters = {}
        if location:
            filters["location"] = location
        if start_time:
            filters["timestamp"] = {"$gte": start_time}
        if end_time:
            if "timestamp" in filters:
                filters["timestamp"]["$lte"] = end_time
            else:
                filters["timestamp"] = {"$lte": end_time}
        
        # Execute query
        cursor = collection.find(filters).limit(50)
        events = await cursor.to_list(length=50)
        
        # Convert ObjectId to string
        for event in events:
            event["_id"] = str(event["_id"])
        
        return {
            "success": True,
            "query": query,
            "processed_query": processed_query,
            "results_count": len(events),
            "results": events
        }
        
    except Exception as e:
        logger.error(f"Error processing contextual query: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@router.post("/process-video")
async def process_contextual_video(
    location: str = Form(...),
    video: UploadFile = File(...)
):
    """
    Process a video file for contextual analysis and event detection.
    """
    try:
        # Validate file type
        if not video.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Unsupported video format"}
            )
        
        # Save uploaded video
        video_dir = "/tmp/contextual_videos"
        os.makedirs(video_dir, exist_ok=True)
        video_path = os.path.join(video_dir, f"{location}_{int(time.time())}_{video.filename}")
        
        with open(video_path, "wb") as buffer:
            content = await video.read()
            buffer.write(content)
        
        # Process video in background
        processing_id = f"contextual_{location}_{int(time.time())}"
        executor.submit(process_video_for_contextual, video_path, location, processing_id)
        
        return {
            "success": True,
            "processing_id": processing_id,
            "message": "Video processing started",
            "video_path": video_path,
            "location": location
        }
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


def process_video_for_contextual(video_path: str, location: str, processing_id: str):
    """Process video file for contextual analysis."""
    try:
        # Import here to avoid circular imports
        from src.modules.context_intelligence.video_analyzer import VideoAnalyzer, EventDetector, QueryProcessor
        
        # Initialize analyzers
        video_analyzer = VideoAnalyzer()
        event_detector = EventDetector()
        query_processor = QueryProcessor()
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"Could not open video file: {video_path}")
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        frame_count = 0
        processed_frames = 0
        all_analyses = []
        all_events = []
        
        logger.info(f"Processing video: {video_path}, Duration: {duration:.1f}s, FPS: {fps}")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process every 30th frame (approximately 1 FPS)
            if frame_count % 30 == 0:
                timestamp = frame_count / fps if fps > 0 else processed_frames
                
                # Analyze frame
                analysis = video_analyzer.analyze_frame(frame, timestamp)
                all_analyses.append(analysis)
                
                # Detect events
                events = event_detector.process_frame(analysis)
                all_events.extend(events)
                
                # Add to query processor
                query_processor.add_analysis(analysis, events)
                
                processed_frames += 1
                
                # Log progress every 10 frames
                if processed_frames % 10 == 0:
                    logger.info(f"Processed {processed_frames} frames, {len(all_events)} events detected")
            
            frame_count += 1
        
        cap.release()
        
        # Calculate summary statistics
        motion_frames = [a for a in all_analyses if a.get("motion_detected", False)]
        brightness_values = [a.get("brightness", 128) for a in all_analyses]
        total_objects = sum(len(a.get("objects_detected", [])) for a in all_analyses)
        event_types = list(set([e["type"] for e in all_events])) if all_events else []
        
        # Save results to database
        result_data = {
            "processing_id": processing_id,
            "location": location,
            "video_path": video_path,
            "duration": duration,
            "total_frames": total_frames,
            "processed_frames": processed_frames,
            "fps": fps,
            "analyses": all_analyses,
            "events": all_events,
            "summary": {
                "motion_frames": len(motion_frames),
                "average_brightness": float(np.mean(brightness_values)) if brightness_values else 0,
                "total_objects": total_objects,
                "event_types": event_types,
                "activity_score": len(all_events) + len(motion_frames)
            },
            "timestamp": datetime.utcnow(),
            "status": "completed"
        }
        
        # Store in database
        asyncio.run(store_contextual_results(result_data))
        
        logger.info(f"Contextual analysis completed: {processed_frames} frames, {len(all_events)} events")
        
    except Exception as e:
        logger.error(f"Error in contextual video processing: {str(e)}")
        # Store error in database
        error_data = {
            "processing_id": processing_id,
            "location": location,
            "video_path": video_path,
            "error": str(e),
            "timestamp": datetime.utcnow(),
            "status": "error"
        }
        asyncio.run(store_contextual_results(error_data))


async def store_contextual_results(result_data: dict):
    """Store contextual analysis results in database."""
    try:
        collection = db["contextual_analysis"]
        await collection.insert_one(result_data)
        logger.info(f"Stored contextual results for processing_id: {result_data.get('processing_id')}")
    except Exception as e:
        logger.error(f"Error storing contextual results: {str(e)}")


@router.get("/results/{processing_id}")
async def get_contextual_results(processing_id: str):
    """Get contextual analysis results by processing ID."""
    try:
        collection = db["contextual_analysis"]
        result = await collection.find_one({"processing_id": processing_id})
        
        if not result:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Results not found"}
            )
        
        # Convert ObjectId to string
        result["_id"] = str(result["_id"])
        
        return {
            "success": True,
            "results": result
        }
        
    except Exception as e:
        logger.error(f"Error retrieving contextual results: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@router.get("/stream-analysis")
async def stream_contextual_analysis():
    """Stream real-time contextual analysis data."""
    def generate_analysis_data():
        """Generate mock real-time contextual analysis data."""
        import random
        
        while True:
            # Generate mock analysis data
            timestamp = time.time()
            
            # Mock motion detection
            motion_detected = random.choice([True, False])
            motion_areas = []
            if motion_detected:
                num_areas = random.randint(1, 3)
                for _ in range(num_areas):
                    motion_areas.append({
                        "x": random.randint(0, 640),
                        "y": random.randint(0, 480),
                        "width": random.randint(50, 200),
                        "height": random.randint(50, 200),
                        "area": random.randint(2500, 40000)
                    })
            
            # Mock object detection
            objects_detected = []
            num_objects = random.randint(0, 3)
            object_types = ["person", "vehicle", "package", "equipment", "large_object"]
            for _ in range(num_objects):
                objects_detected.append({
                    "type": random.choice(object_types),
                    "bbox": {
                        "x": random.randint(0, 640),
                        "y": random.randint(0, 480),
                        "width": random.randint(50, 200),
                        "height": random.randint(50, 200)
                    },
                    "area": random.randint(2500, 40000),
                    "confidence": round(random.uniform(0.5, 1.0), 2)
                })
            
            # Mock events
            events = []
            if random.random() < 0.3:  # 30% chance of event
                event_types = ["sudden_motion", "person_detected", "lighting_anomaly", "object_left_behind"]
                events.append({
                    "type": random.choice(event_types),
                    "timestamp": timestamp,
                    "description": f"Event detected at {datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')}",
                    "severity": random.choice(["low", "medium", "high"]),
                    "confidence": round(random.uniform(0.6, 1.0), 2)
                })
            
            analysis_data = {
                "timestamp": timestamp,
                "location": "Warehouse-A",
                "motion_detected": motion_detected,
                "motion_areas": motion_areas,
                "brightness": random.randint(50, 200),
                "activity_level": random.randint(0, 10),
                "objects_detected": objects_detected,
                "events": events,
                "scene_description": f"{'High' if motion_detected else 'Low'} activity scene with {len(objects_detected)} objects detected",
                "analysis_time": round(random.uniform(0.1, 0.5), 3)
            }
            
            yield f"data: {json.dumps(analysis_data)}\n\n"
            time.sleep(2)  # Update every 2 seconds
    
    return StreamingResponse(
        generate_analysis_data(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.get("/analytics")
async def get_contextual_analytics():
    """Get analytics and statistics from contextual analysis."""
    try:
        collection = db["contextual_analysis"]
        
        # Get total processed videos
        total_videos = await collection.count_documents({"status": "completed"})
        
        # Get recent results
        recent_results = await collection.find(
            {"status": "completed"}, 
            sort=[("timestamp", -1)]
        ).limit(10).to_list(length=10)
        
        # Calculate aggregate statistics
        total_events = 0
        total_objects = 0
        event_types = {}
        
        for result in recent_results:
            result["_id"] = str(result["_id"])
            if "summary" in result:
                total_events += len(result.get("events", []))
                total_objects += result["summary"].get("total_objects", 0)
                
                for event_type in result["summary"].get("event_types", []):
                    event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            "success": True,
            "analytics": {
                "total_videos_processed": total_videos,
                "total_events_detected": total_events,
                "total_objects_detected": total_objects,
                "event_type_distribution": event_types,
                "recent_analyses": recent_results
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting contextual analytics: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
