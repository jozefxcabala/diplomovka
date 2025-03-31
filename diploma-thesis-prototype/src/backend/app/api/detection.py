from fastapi import APIRouter
from backend.app.models.detection_models import DetectionRequest, DetectionResponse
from backend.app.services.detection_service import run_object_detection

router = APIRouter()

@router.post("/object-detection", response_model=DetectionResponse)
def detect_objects(request: DetectionRequest):
    return run_object_detection(request)
