import os
import re
from collections import defaultdict

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

def load_analyzed_filenames_with_objects_and_anomalies_from_annotations(video_root_path: str) -> dict[str, dict[str, list[dict]]]:
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

def evaluate_results(all_results, scenes, categories):
    def get_gt_activities_for_video(path):
        for scene_data in scenes.values():
            for label_type in ["normal", "abnormal"]:
                for video_entry in scene_data[label_type]:
                    if video_entry["path"] == path:
                        activities = []
                        for obj in video_entry["objects"].values():
                            for anomaly in obj.get("anomalies", []):
                                if "activity" in anomaly:
                                    activities.append(anomaly["activity"].strip().lower())
                        return activities
        return []

    tp = 0
    fp = 0
    fn = 0
    tn = 0
    detailed_results = []

    all_videos = all_results["normal_results"] + all_results["abnormal_results"]
    categories_set = set(c.strip().lower() for c in categories)

    for video_result in all_videos:
        video_path = video_result["result"]["path"]
        detected_objects = video_result["result"]["objects"]

        detected_activities = set()
        for obj in detected_objects.values():
            for anomaly in obj.get("anomalies", []):
                if isinstance(anomaly, dict) and "type_of_anomaly" in anomaly:
                    if isinstance(anomaly["type_of_anomaly"], list):
                        for label in anomaly["type_of_anomaly"]:
                            detected_activities.add(label.strip().lower())
                    else:
                        detected_activities.add(anomaly["type_of_anomaly"].strip().lower())

        all_gt_activities = set(a.strip().lower() for a in get_gt_activities_for_video(video_path))
        gt_activities = all_gt_activities.intersection(categories_set)

        for category in categories_set:
            detected = category in detected_activities
            expected = category in gt_activities

            if detected and expected:
                tp += 1
                decision = "TP"
            elif detected and not expected:
                fp += 1
                decision = "FP"
            elif not detected and expected:
                fn += 1
                decision = "FN"
            else:
                tn += 1
                decision = "TN"

            detailed_results.append({
                "video": os.path.basename(video_path),
                "category": category,
                "detected": detected,
                "expected": expected,
                "decision": decision
            })

    # print("Detailed results: ", detailed_results)

    return tp, fp, fn, tn