from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class AnalysisConfigIn(BaseModel):
    name: str
    categories: List[str]
    settings: Dict[str, Any]

class AnalysisConfigOut(AnalysisConfigIn):
    id: int
    created_at: datetime

class UpdateAnalysisConfigRequest(BaseModel):
    name: str
    categories: List[str]
    settings: Dict[str, Any]

class LinkIn(BaseModel):
    video_id: int
    config_id: int