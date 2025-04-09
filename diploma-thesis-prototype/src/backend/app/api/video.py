from fastapi import APIRouter, HTTPException
from backend.app.models.video_models import VideoVisualizationRequest
from backend.app.services.video_service import run_video_visualization, save_uploaded_video, get_video_data

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/video/{video_id}")
async def fetch_video_data(video_id: int):
    try:
        video_data = get_video_data(video_id)
        if not video_data:
            raise HTTPException(status_code=404, detail="Video not found")
        return video_data
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/video/visualization")
def video_visualization(request: VideoVisualizationRequest):
    return run_video_visualization(request)

@router.post("/video/upload")
async def upload_video(video: UploadFile = File(...)):
    try:
        video_path, video_filename = save_uploaded_video(video)
        return JSONResponse(status_code=200, content={
            "video_path": video_path,
            "video_filename": video_filename
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})