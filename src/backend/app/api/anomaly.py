"""
anomaly.py

This API router provides endpoints for running anomaly preprocessing and recognition.

Endpoints:
- POST /anomaly/preprocess: runs preprocessing on video frames to prepare for recognition.
- POST /anomaly/recognition: performs anomaly recognition using extracted features.
"""
from fastapi import APIRouter
from backend.app.models.anomaly_models import AnomalyPreprocessRequest, AnomalyRecognitionRequest
from backend.app.services.anomaly_service import run_anomaly_preprocessing, run_anomaly_recognition

router = APIRouter()

@router.post("/anomaly/preprocess")
def preprocess_anomaly(request: AnomalyPreprocessRequest):
    return run_anomaly_preprocessing(request)

@router.post("/anomaly/recognition")
def anomaly_recognition(request: AnomalyRecognitionRequest):
    return run_anomaly_recognition(request)
