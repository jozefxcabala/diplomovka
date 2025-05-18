from pydantic import BaseModel
from typing import List

class ResultInterpreterRequest(BaseModel):
    video_id: int
    threshold: int
    categories: List[str]
    top_k: int = 5
