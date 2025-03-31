from pydantic import BaseModel

class ResultInterpreterRequest(BaseModel):
    video_id: int
    threshold: int
    category_list_path: str
