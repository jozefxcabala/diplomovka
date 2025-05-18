"""
result_interpreter_service.py

This module provides service-level functions for handling the result interpretation
stage of the video analysis pipeline.

Functions:
- run_result_interpreter: runs the result interpretation using configured parameters.
- get_results_from_xclip_preprocessing: retrieves processed videos from the database.
- delete_video_analysis: deletes a video and its analysis from the database.
"""

from backend.app.core.result_interpreter import main as result_interpreter_main
from backend.app.models.result_models import ResultInterpreterRequest
from backend.app.core.database_manager import DatabaseManager

# Trigger the result interpretation stage with given parameters
def run_result_interpreter(request: ResultInterpreterRequest):
    result_interpreter_main(
        request.video_id,
        request.threshold,
        request.categories,
        request.top_k
    )
    return {"message": "Result interpretation completed."}

def get_results_from_xclip_preprocessing():
    # Connect to the database
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    # Retrieve all processed video entries
    return db.fetch_videos()

def delete_video_analysis(video_id: int) -> dict:
    # Connect to the database
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    # Attempt to delete video entry by ID
    success = db.delete_video_by_id(video_id)
    if not success:
        raise ValueError(f"Video with ID {video_id} not found.")
    return {"message": f"Video {video_id} deleted."}