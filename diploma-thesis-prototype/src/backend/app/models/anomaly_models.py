from pydantic import BaseModel
from typing import List

class AnomalyPreprocessRequest(BaseModel):
    video_id: int
    video_path: str
    output_path: str
    target_width: int = 200
    target_height: int = 200
    max_frames: int = 50

class AnomalyRecognitionRequest(BaseModel):
    video_id: int
    categories: List[str]