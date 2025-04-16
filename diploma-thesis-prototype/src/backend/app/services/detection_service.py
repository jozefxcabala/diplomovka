from typing import Dict, List
from backend.app.models.detection_models import DetectionRequest, DetectionResponse
from backend.app.core.object_detection_processor import main as object_detection_main
from backend.app.core.database_manager import DatabaseManager

def run_object_detection(request: DetectionRequest) -> DetectionResponse:
    video_id = object_detection_main(
        video_path=request.video_path,
        name_of_analysis=request.name_of_analysis,
        num_segments=request.num_segments,
        processing_mode=request.processing_mode,
        model_path=request.model_path,
        classes_to_detect=request.classes_to_detect
    )
    return DetectionResponse(
        video_id=video_id,
        message="Object detection completed successfully."
    )

def get_detections_by_video_id(video_id: int):
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    
    return db.fetch_detections_by_video_id(video_id)