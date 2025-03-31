from backend.app.models.anomaly_models import AnomalyPreprocessRequest
from backend.app.core.helpers import create_folders
from backend.app.core.anomaly_recognition_preprocessor import main as preprocess_main

def run_anomaly_preprocessing(request: AnomalyPreprocessRequest):
    create_folders(request.output_path)
    preprocess_main(
        request.video_id,
        request.video_path,
        request.output_path,
        request.max_frames,
        request.target_width,
        request.target_height
    )
    return {"message": "Anomaly preprocessing completed."}
