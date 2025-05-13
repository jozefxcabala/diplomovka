from collections import defaultdict
import io
import json
import re
import sys
import os
import contextlib

import datetime
import time
import sys

import torch
import numpy as np
from typing import Dict, List

import argparse

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src"))
sys.path.append(ROOT_DIR)
DATASET_PATH = "../../UBnormal"

import psycopg2
from backend.app.core.database_manager import DatabaseManager

DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'dbname': 'diploma_thesis_prototype_db',
    'user': 'postgres',
    'password': 'postgres',
}

# Argument parser
parser = argparse.ArgumentParser(description="Evaluate anomaly detection results.")
parser.add_argument('--threshold', type=int, default=23, help='Threshold when anomaly is detected (default: 23)')
parser.add_argument('--confidence_threshold', type=float, default=0.1, help='Minimum confidence for detection to be considered (default: 0.1)')
parser.add_argument('--top_k', type=int, default=3, help='Number of top logits to consider (default: 3)')
args = parser.parse_args()

# Použitie argumentov
THRESHOLD = args.threshold
CONFIDENCE_THRESHOLD = args.confidence_threshold
TOP_K = args.top_k

CATEGORIES = [
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

def format_duration(seconds):
    """Vráti formátovaný string z počtu sekúnd: X hodín Y minút Z sekúnd"""
    hours = int(seconds) // 3600
    minutes = (int(seconds) % 3600) // 60
    secs = int(seconds) % 60
    return f"{hours} h {minutes} min {secs} s"

def interpret_result(video_id: int, threshold: float, list_of_categories: List[str], topk_a: int):
    db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    result = {}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            db_manager.connect()

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            SELECT id FROM detections
            WHERE video_id = %s AND confidence >= %s;
        """, (video_id, CONFIDENCE_THRESHOLD))
        valid_detection_ids = set(row[0] for row in cur.fetchall())
        cur.close()
        conn.close()

        all_logits = db_manager.get_anomaly_recognition_data_by_video_id(video_id)
        logits_per_video_binary_map = [entry for entry in all_logits if entry['detection_id'] in valid_detection_ids]

        for data in logits_per_video_binary_map:
            detection_id = int(data['detection_id'])
            logits_tensor = torch.tensor(np.frombuffer(data['logits_per_video'], dtype=np.float32))
            topk = min(topk_a, logits_tensor.shape[0])
            top_scores, top_indices = logits_tensor.topk(topk)

            anomalies = []
            for score, index in zip(top_scores, top_indices):
                if score.item() >= threshold:
                    anomalies.append({"label": list_of_categories[index.item()], "score": score.item()})

            if anomalies:
                result[detection_id] = anomalies

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        db_manager.close()
    return result

def get_all_videos():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT v.id, v.video_path
        FROM detections d
        JOIN videos v ON d.video_id = v.id
        ORDER BY v.id;
    """)
    videos = [{"video_id": row[0], "video_path": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return videos

def evaluate_results(results, scenes, categories):
    def get_gt_activities_for_video(path):
        for scene_data in scenes.values():
            for label_type in ["normal", "abnormal"]:
                for video_entry in scene_data[label_type]:
                    if video_entry["path"] == path:
                        return [anomaly["activity"].strip().lower()
                                for obj in video_entry["objects"].values()
                                for anomaly in obj.get("anomalies", []) if "activity" in anomaly]
        return []

    tp = fp = fn = tn = 0
    cat_set = set(c.strip().lower() for c in categories)

    for r in results:
        path = r["result"]["path"]
        detected_acts = {
            label.strip().lower()
            for obj in r["result"]["objects"].values()
            for anomaly in obj["anomalies"]
            for label in (anomaly["type_of_anomaly"] if isinstance(anomaly["type_of_anomaly"], list) else [anomaly["type_of_anomaly"]])
        }
        gt_acts = set(get_gt_activities_for_video(path)).intersection(cat_set)
        for cat in cat_set:
            if cat in detected_acts and cat in gt_acts: tp += 1
            elif cat in detected_acts: fp += 1
            elif cat in gt_acts: fn += 1
            else: tn += 1

    prec = tp / (tp + fp) if (tp + fp) > 0 else 0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
    return {
        "true_positives": tp, "false_positives": fp, "false_negatives": fn, "true_negatives": tn,
        "precision": prec, "recall": rec, "f1_score": f1
    }

def safe_parse(value):
    return value if value != "-" else "unset"

def parse_annotation_line(line: str):
    parts = [safe_parse(p) for p in re.split(r'[,\s]+', line.strip(), maxsplit=6)]  # maxsplit=6, lebo už nie je object_id

    if len(parts) >= 7:
        scene = parts[0]
        scenario = parts[1]
        part = parts[2]
        na_type = parts[3]  # 'n' for normal, 'a' for abnormal
        start = parts[4]
        end = parts[5]
        activity = parts[6]

        try:
            scene_num = int(scene)
            scenario_num = int(scenario)
            
            if part == "-":
                part_num = "unset"
            elif part.isdigit():
                part_num = int(part)
            else:
                part_num = part

            start_frame = int(float(start)) if start != "unset" else "unset"
            end_frame = int(float(end)) if end != "unset" else "unset"

            return {
                "scene": scene_num,
                "scenario": scenario_num,
                "part": part_num,
                "normal_abnormal": na_type,
                "start": start_frame,
                "end": end_frame,
                "activity": activity
            }
        except ValueError:
            return None
    return None


def load_scenes(video_root_path: str) -> dict[str, dict[str, list[dict]]]:
    temp_result = defaultdict(lambda: {"abnormal": [], "normal": []})

    for root, _, files in os.walk(video_root_path):
        for file in files:
            if file == "annotations.txt":
                annotation_path = os.path.join(root, file)

                scene_match = re.search(r"Scene(\d+)", root)
                if not scene_match:
                    continue
                scene_number = int(scene_match.group(1))
                scene_key = f"scene_{scene_number}"

                video_entries = {}  # (scene_num, scenario_num, label, part) -> object anomalies

                with open(annotation_path, 'r') as f:
                    lines = f.readlines()

                for line in lines:
                    parsed = parse_annotation_line(line)
                    if parsed:
                        scene_num = parsed["scene"]
                        scenario_num = parsed["scenario"]
                        part_num = parsed["part"]
                        na_type = parsed["normal_abnormal"]
                        start = parsed["start"]
                        end = parsed["end"]
                        activity = parsed["activity"]

                        label = "normal" if na_type == "n" else "abnormal"
                        key = (scene_num, scenario_num, label, part_num)

                        if key not in video_entries:
                            video_entries[key] = {}

                        # Generovanie nového object_id ak treba
                        next_object_id = str(len(video_entries[key]) + 1)

                        # Vytvor objekt pre nové object_id
                        video_entries[key][next_object_id] = {
                            "name": "person",
                            "anomalies": []
                        }

                        # Zapíš anomáliu do objektu
                        video_entries[key][next_object_id]["anomalies"].append({
                            "start": start,
                            "end": end,
                            "activity": activity
                        })

                # vytvoríme video entries
                for (scene_num, scenario_num, label, part_num), objects in video_entries.items():
                    if (isinstance(part_num, int) or part_num in ["fire", "fog", "smoke"]) and part_num != "unset":
                        video_filename = f"{label}_scene_{scene_num}_scenario_{scenario_num}_{part_num}.mp4"
                    else:
                        video_filename = f"{label}_scene_{scene_num}_scenario_{scenario_num}.mp4"

                    video_path = os.path.join(root.replace("annotations", ""), video_filename)

                    video_info = {
                        "path": video_path,
                        "objects": objects
                    }

                    temp_result[scene_key][label].append(video_info)

    # zoradenie
    sorted_result = {}
    for scene_key in sorted(temp_result.keys(), key=lambda k: int(k.split('_')[1])):
        sorted_result[scene_key] = {
            "abnormal": sorted(temp_result[scene_key]["abnormal"], key=lambda x: x["path"]),
            "normal": sorted(temp_result[scene_key]["normal"], key=lambda x: x["path"]),
        }

    return sorted_result

def get_activities_for_scenes(scenes: dict, CATEGORIES: list[str]) -> dict[str, list[str]]:
    category_set = set(c.lower() for c in CATEGORIES)
    scene_to_activities = {}

    for scene_key, scene_data in scenes.items():
        activities = set()

        for label_type in ["normal", "abnormal"]:
            for video_entry in scene_data[label_type]:
                for obj in video_entry["objects"].values():
                    for anomaly in obj.get("anomalies", []):
                        if "activity" in anomaly:
                            activity = anomaly["activity"].strip().lower()
                            if activity in category_set:
                                activities.add(activity)

        scene_to_activities[scene_key] = sorted(activities)

    return scene_to_activities

def get_gt_activities_for_scene(path: str, scenes: dict, categories: list[str]) -> list[str]:
    # Extrahuj názov scény zo súborovej cesty (napr. Scene1)
    match = re.search(r"/Scene(\d+)/", path)

    if not match:
        return []

    scene_number = match.group(1)  # napr. "1"
    target_scene = f"scene_{scene_number}"  # → "scene_1"
    categories_set = set(c.strip().lower() for c in categories)
    activities = []

    for scene_key, scene_data in scenes.items():
        if target_scene in scene_key.lower():  # napr. 'scene1' in 'scene_1'
            for label_type in ["normal", "abnormal"]:
                for video_entry in scene_data[label_type]:
                    for obj in video_entry["objects"].values():
                        for anomaly in obj.get("anomalies", []):
                            if "activity" in anomaly:
                                act = anomaly["activity"].strip().lower()
                                if act in categories_set:
                                    activities.append(act)
        return activities
    return []

def main():
    videos = get_all_videos()
    scenes = load_scenes(DATASET_PATH)

    scene_results = defaultdict(list)
    scene_categories = get_activities_for_scenes(scenes, CATEGORIES)

    for video in videos:
        vid = video["video_id"]
        vpath = re.sub(r'^.*(?=/UBnormal)', '../..', video["video_path"])
        match = re.search(r"/Scene(\d+)/", vpath)
        if not match: continue
        scene_key = f"scene_{match.group(1)}"
        cats = scene_categories.get(scene_key, [])
        anomalies = interpret_result(vid, THRESHOLD, cats, TOP_K)

        obj_map = {
            str(i + 1): {"name": "person", "anomalies": [{"type_of_anomaly": [a["label"] for a in lst[:TOP_K]]}]}
            for i, (did, lst) in enumerate(anomalies.items())
        }

        scene_results[scene_key].append({
            "video_id": vid,
            "result": {"path": vpath, "objects": obj_map}
        })

    evaluation_by_scene = {
        scene: evaluate_results(results, scenes, scene_categories.get(scene, []))
        for scene, results in scene_results.items()
    }

    print(json.dumps(evaluation_by_scene, indent=2))

if __name__ == "__main__":
    main()