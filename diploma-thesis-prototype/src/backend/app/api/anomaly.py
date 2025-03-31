from fastapi import APIRouter
from backend.app.models.anomaly_models import AnomalyPreprocessRequest
from backend.app.services.anomaly_service import run_anomaly_preprocessing

router = APIRouter()

@router.post("/anomaly-preprocess")
def preprocess_anomaly(request: AnomalyPreprocessRequest):
    return run_anomaly_preprocessing(request)
