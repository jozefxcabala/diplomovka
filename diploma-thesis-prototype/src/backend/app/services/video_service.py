from backend.app.core.video_visualizer import show_anomalies_in_video
from backend.app.models.video_models import VideoVisualizationRequest

def run_video_visualization(request: VideoVisualizationRequest):
    show_anomalies_in_video(request.video_id)
    output_path = f"data/output/{request.video_id}/final_output.mp4"
    return {
        "message": "Anomalies visualized.",
        "output_path": output_path
    }
