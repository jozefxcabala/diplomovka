"""
result.py

This API router exposes endpoints related to the result interpretation phase of the analysis pipeline.

Endpoints:
- POST /result-interpreter: triggers the result interpretation process for a given video.
- GET /results/xclip-preprocessing: fetches metadata of analyzed videos from the database.
- DELETE /results/xclip-preprocessing/{video_id}: deletes all data related to the specified video.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from backend.app.core.database_manager import DatabaseManager
from backend.app.models.result_models import ResultInterpreterRequest
from backend.app.services.result_interpreter_service import run_result_interpreter, get_results_from_xclip_preprocessing, delete_video_analysis

router = APIRouter()

@router.post("/result-interpreter")
def result_interpreter(request: ResultInterpreterRequest):
    return run_result_interpreter(request)

@router.get("/results/xclip-preprocessing")
def xclip_preprocessing():
    try:
        db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    
        db_manager.connect()
        db_manager.create_tables()
        results = get_results_from_xclip_preprocessing()
        return results
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
@router.delete("/results/xclip-preprocessing/{video_id}")
def delete_xclip_result(video_id: int):
    try:
        return delete_video_analysis(video_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})