from fastapi import APIRouter, HTTPException
from backend.app.models.detection_models import DetectionRequest, DetectionResponse
from backend.app.services.detection_service import run_object_detection
from backend.app.services.detection_service import get_detections_by_video_id

router = APIRouter()

@router.post("/object-detection", response_model=DetectionResponse)
def detect_objects(request: DetectionRequest):
    return run_object_detection(request)

@router.get("/detections/{video_id}")
def get_detections(video_id: int):
    detections = get_detections_by_video_id(video_id)
    return {"detections": detections}