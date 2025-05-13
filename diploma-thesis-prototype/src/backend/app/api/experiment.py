import os
import time
from typing import List
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from backend.app.services.ubnormal_experiment_service import (
    load_analyzed_filenames_with_objects_and_anomalies_from_annotations,
    evaluate_results as evaluate_results_ubnormal,
    get_activities_for_scene
)
from backend.app.services.experiment_service import run_full_analysis

router = APIRouter()

# Base directory = root of the project (assuming this script is in diploma-thesis-prototype/src/backend/app/api/)

BASE_DIR = Path(__file__).resolve().parents[4]


class UBnormalExperimentRequest(BaseModel):
    dataset_path: str = "experiments/UBnormal"
    model_path: str = "data/models/yolo11n.pt"
    num_segments: int = 8
    categories: List[str] = [
        "a person wearing a helmet and an orange vest is walking",
        "a person wearing a helmet and an orange vest is dancing",
        "a person wearing a helmet and an orange vest is standing in place",
        "a person wearing a helmet and an orange vest is jumping",
        "a person wearing a helmet and an orange vest is running",
        "a person wearing a helmet and an orange vest is fighting",
        "a person wearing a helmet and an orange vest have something in hand",
        "a person wearing a helmet and an orange vest is lying in the ground",
        "a person wearing a helmet and an orange vest is limping",
        "a person wearing a helmet and an orange vest fell to the ground",
        "a person wearing a helmet and an orange vest is sitting",
        "a person wearing a helmet and an orange vest is riding motocycle"
    ]
    threshold: int = 21
    skip_frames: bool = True
    num_of_skip_frames: int = 5
    confidence_threshold: float = 0.25
    top_k: int = 5
    batch_size: int = 32
    frame_sample_rate: int = 4
    processing_mode: str = "sequential"


@router.post("/experiments/ubnormal/run")
def run_experiment_pipeline(request: UBnormalExperimentRequest):
    start_time = time.time()

    dataset_path = str(BASE_DIR / request.dataset_path)
    model_path = str(BASE_DIR / request.model_path)
    
    scenes = load_analyzed_filenames_with_objects_and_anomalies_from_annotations(
        dataset_path
    )

    normal_video_analysis_results = []
    abnormal_video_analysis_results = []

    categories_for_scenes = get_activities_for_scene(scenes, request.categories)

    # counter = 0
    # scenes_to_process = 1

    for scene_name, scene_data in scenes.items():
        # if counter >= scenes_to_process:
            # break

        normals = scene_data["normal"]
        for normal_entry in normals:
            normal_full_analysis_response = run_full_analysis(
                video_path=normal_entry["path"],
                model_path=model_path,
                num_segments=request.num_segments,
                processing_mode=request.processing_mode,
                classes_to_detect=[0],
                name_of_analysis=f"{normal_entry['path']}_analysis",
                categories=categories_for_scenes[scene_name],
                threshold=request.threshold,
                skip_frames=request.skip_frames,
                num_of_skip_frames=request.num_of_skip_frames,
                confidence_threshold=request.confidence_threshold,
                top_k=request.top_k,
                batch_size=request.batch_size,
                frame_sample_rate=request.frame_sample_rate
            )
            normal_video_analysis_results.append(normal_full_analysis_response)

        abnormals = scene_data["abnormal"]
        for abnormal_entry in abnormals:
            abnormal_full_analysis_response = run_full_analysis(
                video_path=abnormal_entry["path"],
                model_path=model_path,
                num_segments=request.num_segments,
                processing_mode=request.processing_mode,
                classes_to_detect=[0],
                name_of_analysis=f"{abnormal_entry['path']}_analysis",
                categories=categories_for_scenes[scene_name],
                threshold=request.threshold,
                skip_frames=request.skip_frames,
                num_of_skip_frames=request.num_of_skip_frames,
                confidence_threshold=request.confidence_threshold,
                top_k=request.top_k,
                batch_size=request.batch_size,
                frame_sample_rate=request.frame_sample_rate
            )
            abnormal_video_analysis_results.append(abnormal_full_analysis_response)

        # counter += 1

    end_time = time.time()
    total_duration = round(end_time - start_time, 2)

    all_results = {
        "abnormal_results": abnormal_video_analysis_results,
        "normal_results": normal_video_analysis_results
    }

    tp, fp, fn, tn = evaluate_results_ubnormal(all_results, scenes, request.categories)

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