"""
video_service.py

This module provides high-level functions for handling video-related operations
in the anomaly detection pipeline.

Functions:
- run_video_visualization: triggers anomaly overlay rendering for a given video.
- save_uploaded_video: stores uploaded video files on disk.
- get_video_data: retrieves metadata for a video by ID from the database.
"""

from backend.app.core.video_visualizer import show_anomalies_in_video
from backend.app.models.video_models import VideoVisualizationRequest
from backend.app.core.database_manager import DatabaseManager

import os
import shutil
from fastapi import UploadFile

def run_video_visualization(request: VideoVisualizationRequest):
    # Generate a video with anomalies visualized based on detection results
    show_anomalies_in_video(request.video_id)
    output_path = f"data/output/{request.video_id}/final_output.mp4"
    return {
        "message": "Anomalies visualized.",
        "output_path": output_path
    }

VIDEO_STORAGE_PATH = "../data/input"

def save_uploaded_video(video: UploadFile) -> tuple[str, str]:
    """Save uploaded video to disk and return its path and filename."""
    # Ensure the upload directory exists
    if not os.path.exists(VIDEO_STORAGE_PATH):
        os.makedirs(VIDEO_STORAGE_PATH)

    video_path = os.path.join(VIDEO_STORAGE_PATH, video.filename)

    # Save the video file to the specified path
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    return video_path, video.filename

def get_video_data(video_id: int):
    # Connect to the database and fetch video metadata
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()

    return db.fetch_video_by_id(video_id)