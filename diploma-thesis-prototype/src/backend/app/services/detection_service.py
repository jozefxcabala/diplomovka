from app.models.detection_models import DetectionRequest, DetectionResponse
from app.core.object_detection_processor import main as object_detection_main

def run_object_detection(request: DetectionRequest) -> DetectionResponse:
    video_id = object_detection_main(
        video_path=request.video_path,
        num_segments=request.num_segments,
        processing_mode=request.processing_mode,
        model_path=request.model_path,
        classes_to_detect=request.classes_to_detect,
    )
    return DetectionResponse(
        video_id=video_id,
        message="Object detection completed successfully."
    )
