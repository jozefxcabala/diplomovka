from fastapi import APIRouter
from backend.app.models.video_models import VideoVisualizationRequest
from backend.app.services.video_service import run_video_visualization, save_uploaded_video

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

router = APIRouter()

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