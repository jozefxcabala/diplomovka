from fastapi import APIRouter
from backend.app.models.video_models import VideoVisualizationRequest
from backend.app.services.video_service import run_video_visualization

router = APIRouter()

@router.post("/video-visualization")
def video_visualization(request: VideoVisualizationRequest):
    return run_video_visualization(request)
