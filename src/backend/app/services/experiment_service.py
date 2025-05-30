"""
experiment_service.py

Orchestrates the full video analysis pipeline consisting of multiple stages:
- Object detection
- Anomaly preprocessing
- Anomaly recognition
- Result interpretation
- Result aggregation from the database

Function:
- run_full_analysis: runs all steps in sequence using the provided parameters and returns the results.
"""

from backend.app.services.detection_service import run_object_detection
from backend.app.models.detection_models import DetectionRequest

from backend.app.services.anomaly_service import run_anomaly_preprocessing, run_anomaly_recognition
from backend.app.models.anomaly_models import AnomalyPreprocessRequest, AnomalyRecognitionRequest

from backend.app.services.result_interpreter_service import run_result_interpreter
from backend.app.models.result_models import ResultInterpreterRequest

from backend.app.core.database_manager import DatabaseManager

def run_full_analysis(video_path, model_path, num_segments, processing_mode, classes_to_detect, name_of_analysis, categories, threshold, skip_frames, num_of_skip_frames, confidence_threshold, top_k, batch_size, frame_sample_rate):
  # Step 1: Run object detection on the input video
  # 1 Object Detection (video_path, name_of_analysis, settings)
  detect_res = run_object_detection(DetectionRequest(
        video_path=video_path,
        model_path=model_path,
        num_segments=num_segments,
        processing_mode='parallel',
        classes_to_detect=classes_to_detect,
        name_of_analysis=name_of_analysis,
        skip_frames=skip_frames,
        num_of_skip_frames=num_of_skip_frames,
        confidence_threshold=confidence_threshold
    ))
  
  video_id = detect_res.video_id

  # Step 2: Run anomaly preprocessing to extract features
  # 2 Anomaly Preprocessing (video_path, video_id, output_path)
  output_path = f"../data/output/{video_id}/anomaly_recognition_preprocessor"
  preproc_res = run_anomaly_preprocessing(AnomalyPreprocessRequest(
    video_id=video_id,
    video_path=video_path,
    output_path=output_path,
    processing_mode=processing_mode,
  ))

  # Step 3: Perform anomaly recognition using the specified categories
  # 3 Anomaly Recognition (video_id, categories)
  recog_res = run_anomaly_recognition(AnomalyRecognitionRequest(
    video_id=video_id,
    categories=categories,
    batch_size=batch_size,
    frame_sample_rate=frame_sample_rate,
    processing_mode=processing_mode,
  ))

  # Step 4: Interpret recognized anomalies using the specified threshold
  # 4 Result Interpreter (video_id, threshold, categories)
  res_int_res = run_result_interpreter(ResultInterpreterRequest(
    video_id=video_id,
    threshold=threshold,
    categories=categories,
    top_k=top_k
  ))

  # Step 5: Fetch detected anomalies from the database
  # 5 Load Results
  db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
  db.connect()
  anomalies = db.fetch_all_anomalies_by_video_id(video_id) 

  result_dict = {
        "path": video_path,
        "objects": {}
    }

  # Format the database results into the expected JSON structure
  for idx, anomaly in enumerate(anomalies):
      object_id = str(idx + 1)  # Generate a simple ID like '1', '2', ...
      result_dict["objects"][object_id] = {
          "name": "person",
          "anomalies": [{
             "start": anomaly["start_frame"], 
             "end": anomaly["end_frame"],
             "type_of_anomaly": [a["label"] for a in anomaly["anomalies"][:top_k]]
          }],
  }

  return {
    "video_id": detect_res.video_id,
    "result": result_dict
  }