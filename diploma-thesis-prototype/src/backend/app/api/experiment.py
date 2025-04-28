import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.app.services.ubnormal_experiment_service import (
    load_analyzed_filenames_with_objects_and_anomalies_from_annotations,
    evaluate_results as evaluate_results_ubnormal
)
from backend.app.services.experiment_service import run_full_analysis

import time

router = APIRouter()

@router.post("/experiments/ubnormal/run")
def run_experiment_pipeline():
    start_time = time.time()

    scenes = load_analyzed_filenames_with_objects_and_anomalies_from_annotations(
        "/Users/caby/Downloads/UBnormal"
    )

    categories = [
        "a person wearing a helmet and an orange vest is walking",
        "a person wearing a helmet and an orange vest is standing in place",
        "a person wearing a helmet and an orange vest is lying on the ground",
        "a person wearing a helmet and an orange vest fell to the ground"
    ]

    threshold = 21

    normal_video_analysis_results = []
    abnormal_video_analysis_results = []

    for scene_name, scene_data in scenes.items():
        normals = scene_data["normal"]
        for normal_entry in normals:
            normal_full_analysis_response = run_full_analysis(
                video_path=normal_entry["path"],
                model_path="/Users/caby/diplomovka/diploma-thesis-prototype/data/models/yolo11n.pt",
                num_segments=8,
                processing_mode="parallel",
                classes_to_detect=[0],
                name_of_analysis=f"{normal_entry['path']}_analysis",
                categories=categories,
                threshold=threshold
            )
            normal_video_analysis_results.append(normal_full_analysis_response)

        abnormals = scene_data["abnormal"]
        for abnormal_entry in abnormals:
            abnormal_full_analysis_response = run_full_analysis(
                video_path=abnormal_entry["path"],
                model_path="/Users/caby/diplomovka/diploma-thesis-prototype/data/models/yolo11n.pt",
                num_segments=8,
                processing_mode="parallel",
                classes_to_detect=[0],
                name_of_analysis=f"{abnormal_entry['path']}_analysis",
                categories=categories,
                threshold=threshold
            )
            abnormal_video_analysis_results.append(abnormal_full_analysis_response)
          
        break

    end_time = time.time()
    total_duration = round(end_time - start_time, 2)

    all_results = {
        "abnormal_results": abnormal_video_analysis_results,
        "normal_results": normal_video_analysis_results
    }

    tp, fp, fn, tn = evaluate_results_ubnormal(all_results, scenes, categories)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        # **all_results,
        "total_videos_analyzed": len(normal_video_analysis_results) + len(abnormal_video_analysis_results),
        "total_duration_seconds": total_duration,
        "statistics": {
          "true_positives": tp,
          "false_positives": fp,
          "false_negatives": fn,
          "true_negatives": tn,
          "precision": precision,
          "recall": recall,
          "f1_score": f1_score
        }
    }