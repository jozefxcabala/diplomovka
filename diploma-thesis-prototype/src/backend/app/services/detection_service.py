"""
detection_service.py

Provides service-layer logic for handling object detection operations.

Functions:
- run_object_detection: runs the object detection pipeline and returns the resulting video ID.
- get_detections_by_video_id: fetches detection records for a given video ID from the database.
"""
from typing import Dict, List
from backend.app.models.detection_models import DetectionRequest, DetectionResponse
from backend.app.core.object_detection_processor import main as object_detection_main
from backend.app.core.database_manager import DatabaseManager

def run_object_detection(request: DetectionRequest) -> DetectionResponse:
    # Execute the object detection process and obtain video ID
    video_id = object_detection_main(
        video_path=request.video_path,
        name_of_analysis=request.name_of_analysis,
        num_segments=request.num_segments,
        processing_mode=request.processing_mode,
        model_path=request.model_path,
        classes_to_detect=request.classes_to_detect,
        skip_frames=request.skip_frames,
        num_of_skip_frames=request.num_of_skip_frames,
        confidence_threshold=request.confidence_threshold
    )
    # Return the response with the detected video ID and message
    return DetectionResponse(
        video_id=video_id,
        message="Object detection completed successfully."
    )

def get_detections_by_video_id(video_id: int):
    # Connect to the database and fetch detections for the given video
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    
    return db.fetch_detections_by_video_id(video_id)