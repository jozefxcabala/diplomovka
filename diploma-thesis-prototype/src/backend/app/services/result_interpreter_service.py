from backend.app.core.result_interpreter import main as result_interpreter_main
from backend.app.models.result_models import ResultInterpreterRequest

def run_result_interpreter(request: ResultInterpreterRequest):
    result_interpreter_main(
        request.video_id,
        request.threshold,
        request.categories
    )
    return {"message": "Result interpretation completed."}
