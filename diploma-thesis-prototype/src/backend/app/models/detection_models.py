from pydantic import BaseModel
from typing import List

class DetectionRequest(BaseModel):
    video_path: str
    model_path: str
    num_segments: int = 8
    processing_mode: str = "parallel"
    classes_to_detect: List[int] = [0]
    name_of_analysis: str
    skip_frames: bool = True
    num_of_skip_frames: int = 5
    confidence_threshold: float = 0.25

class DetectionResponse(BaseModel):
    video_id: int
    message: str
