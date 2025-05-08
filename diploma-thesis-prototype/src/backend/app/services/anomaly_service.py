from backend.app.models.anomaly_models import AnomalyPreprocessRequest, AnomalyRecognitionRequest
from backend.app.core.helpers import create_folders
from backend.app.core.anomaly_recognition_preprocessor import main as preprocess_main
from backend.app.core.anomaly_recognition import main as recognition_main

def run_anomaly_preprocessing(request: AnomalyPreprocessRequest):
    create_folders(request.output_path)
    preprocess_main(
        request.video_id,
        request.video_path,
        request.output_path,
        request.max_frames,
        request.target_width,
        request.target_height,
        request.processing_mode
    )
    return {"message": "Anomaly preprocessing completed."}

def run_anomaly_recognition(request: AnomalyRecognitionRequest):
    recognition_main(
        video_id=request.video_id,
        categories_json=request.categories,
        batch_size=request.batch_size,
        frame_sample_rate=request.frame_sample_rate,
        processing_mode=request.processing_mode
    )
    return {"message": "Anomaly recognition completed."}
