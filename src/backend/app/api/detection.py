"""
detection.py

This API router handles object detection functionality.

Endpoints:
- POST /object-detection: runs the object detection pipeline with provided parameters.
- GET /detections/{video_id}: retrieves detections for a given video ID.
"""
from fastapi import APIRouter, HTTPException
from backend.app.models.detection_models import DetectionRequest, DetectionResponse
from backend.app.services.detection_service import run_object_detection
from backend.app.services.detection_service import get_detections_by_video_id
from pathlib import Path

# Base directory = root of the project (assuming this script is in diploma-thesis-prototype/src/backend/app/api/)

BASE_DIR = Path(__file__).resolve().parents[4]

router = APIRouter()

@router.post("/object-detection", response_model=DetectionResponse)
def detect_objects(request: DetectionRequest):
    absolute_model_path = str(BASE_DIR / request.model_path)
    updated_request = request.model_copy(update={"model_path": absolute_model_path})
    return run_object_detection(updated_request)

@router.get("/detections/{video_id}")
def get_detections(video_id: int):
    detections = get_detections_by_video_id(video_id)
    return {"detections": detections}