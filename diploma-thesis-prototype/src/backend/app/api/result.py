from fastapi import APIRouter
from backend.app.models.result_models import ResultInterpreterRequest
from backend.app.services.result_interpreter_service import run_result_interpreter

router = APIRouter()

@router.post("/result-interpreter")
def result_interpreter(request: ResultInterpreterRequest):
    return run_result_interpreter(request)
