from pydantic import BaseModel

class VideoVisualizationRequest(BaseModel):
    video_id: int
