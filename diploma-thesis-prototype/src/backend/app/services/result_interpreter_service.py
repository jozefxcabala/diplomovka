from backend.app.core.result_interpreter import main as result_interpreter_main
from backend.app.models.result_models import ResultInterpreterRequest
from backend.app.core.database_manager import DatabaseManager

def run_result_interpreter(request: ResultInterpreterRequest):
    result_interpreter_main(
        request.video_id,
        request.threshold,
        request.categories,
        request.top_k
    )
    return {"message": "Result interpretation completed."}

def get_results_from_xclip_preprocessing():
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    return db.fetch_videos()

def delete_video_analysis(video_id: int) -> dict:
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    success = db.delete_video_by_id(video_id)
    if not success:
        raise ValueError(f"Video with ID {video_id} not found.")
    return {"message": f"Video {video_id} deleted."}