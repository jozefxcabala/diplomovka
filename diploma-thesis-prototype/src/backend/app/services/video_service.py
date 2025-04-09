from backend.app.core.video_visualizer import show_anomalies_in_video
from backend.app.models.video_models import VideoVisualizationRequest
from backend.app.core.database_manager import DatabaseManager

import os
import shutil
from fastapi import UploadFile

def run_video_visualization(request: VideoVisualizationRequest):
    show_anomalies_in_video(request.video_id)
    output_path = f"data/output/{request.video_id}/final_output.mp4"
    return {
        "message": "Anomalies visualized.",
        "output_path": output_path
    }

VIDEO_STORAGE_PATH = "../data/input"

def save_uploaded_video(video: UploadFile) -> tuple[str, str]:
    """Save uploaded video to disk and return its path and filename."""
    if not os.path.exists(VIDEO_STORAGE_PATH):
        os.makedirs(VIDEO_STORAGE_PATH)

    video_path = os.path.join(VIDEO_STORAGE_PATH, video.filename)

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    return video_path, video.filename

def get_video_data(video_id: int):
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()

    return db.fetch_video_by_id(video_id)