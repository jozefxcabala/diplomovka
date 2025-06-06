"""
result_interpreter.py

This script interprets anomaly recognition results by mapping logits to category labels and
saving those exceeding a threshold to the database.

Functions:
- get_logits_per_video: retrieves logits for each detection from the database.
- get_probs: converts logits to probabilities using softmax.
- save_anomalies: saves top-k high-confidence anomalies to the database.
- main: orchestrates the result interpretation pipeline.
"""

import time
import argparse
import torch
import numpy as np
from backend.app.core.database_manager import DatabaseManager
import json

def get_logits_per_video(db_manager: DatabaseManager, video_id):
    try:
        db_manager.connect()
        logits_per_video_binary_map = db_manager.get_anomaly_recognition_data_by_video_id(video_id)
        logits_per_video_map = []
        for data in logits_per_video_binary_map:
            logits_tensor = torch.tensor(np.frombuffer(data['logits_per_video'], dtype=np.float32))
            logits_per_video_map.append({
                'detection_id': data['detection_id'],
                'logits_per_video': logits_tensor
            })
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        db_manager.close()
        return logits_per_video_map
    

def get_probs(logits):
    result = []
    for data in logits:
            result.append({
                'detection_id': data['detection_id'],
                'logits_per_video': data['logits_per_video'].softmax(dim=0) * 100
            })
    return result

def save_anomalies(threshold, list_of_categories, db_manager: DatabaseManager, logits, topk_a):
    try:
        db_manager.connect()
        for value in logits:
            logits_tensor = value['logits_per_video']
            detection_id = int(value['detection_id'])

            topk = min(topk_a, logits_tensor.shape[0])
            top_scores, top_indices = logits_tensor.topk(topk)

            anomalies = []
            for score, index in zip(top_scores, top_indices):
                if score.item() >= threshold:
                    anomalies.append({
                        "label": list_of_categories[index.item()],
                        "score": score.item()
                    })

            if anomalies:
                db_manager.insert_detection_anomalies(detection_id, anomalies)

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        db_manager.close()

def main(video_id, threshold, categories_json, topk):
    print(f"The result interpreter program has started.")

    # Initialize database connection
    db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")

    list_of_categories = categories_json

    start_time = time.time()
    
    # Retrieve raw logits for each detection
    logits_per_video = get_logits_per_video(db_manager, video_id)
    # probs = get_probs(logits_per_video)
    
    # Save top-k anomalies that exceed the threshold
    save_anomalies(threshold, list_of_categories, db_manager, logits_per_video, topk)
    
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Print execution time summary
    print(f"Program finished. It took {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run Result Interpreter")
    parser.add_argument('--video_id', required=True, type=int, help="ID of video source in database")
    parser.add_argument('--threshold', required=True, type=int, help="Threshold when anomaly is considered like detected")
    parser.add_argument('--categories_json', required=True, type=str, help="Path to the JSON file containing categories")
    
    args = parser.parse_args()

    main(args.video_id, args.threshold, args.categories_json)