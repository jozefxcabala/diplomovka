from backend.app.core.xclip_handler import XCLIPHandler
import time
import argparse
import json
from backend.app.core.database_manager import DatabaseManager
from multiprocessing import Pool
import os
import torch

def save_results_to_db(results, video_id, db_manager: DatabaseManager):
    try:
        db_manager.connect()
        for detection_id, logits_per_video in results:
            logits_binary = logits_per_video.numpy().tobytes()
            db_manager.insert_anomaly_recognition_data(video_id, detection_id, logits_binary)
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        db_manager.close()

def fetch_video_segments(video_id, db_manager: DatabaseManager):
    try:
        db_manager.connect()
        detections = db_manager.fetch_detections_by_video_id_and_duration(video_id, 50)
        videos = [(f"../{detection['video_object_detection_path']}", detection['id']) for detection in detections]
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        db_manager.close()
        return videos
    
def analyze_video_task(args):
    video_path, list_of_categories, detection_id = args
    handler = XCLIPHandler(list_of_categories)
    return (detection_id, handler.analyze_video(video_path, batch_size=32))

def main(video_id, categories_json):
    print(f"The XCLIP - Action Recognition program has started.")

    db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    
    start_time = time.time()

    # Load categories from the provided JSON file
    # with open(categories_json, 'r') as f:
    #     list_of_categories = json.load(f)
    list_of_categories = categories_json

    # Initialize XCLIP handler
    handler = XCLIPHandler(list_of_categories)
    
    # Analyze video and get results
    results = []
    videos = fetch_video_segments(video_id, db_manager)

    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    # Use multiprocessing Pool for parallel processing
    num_processes = os.cpu_count()
    with Pool(processes=min(len(videos), num_processes)) as pool:
        results = pool.map(analyze_video_task, [(video_path, list_of_categories, detection_id) for video_path, detection_id in videos])
    
    save_results_to_db(results, video_id, db_manager)
    
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Program finished. It took {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run XCLIP Action Recognition")
    parser.add_argument('--video_id', required=True, type=int, help="ID of video source in database")
    parser.add_argument('--categories_json', required=True, type=str, help="Path to the JSON file containing categories")
    
    args = parser.parse_args()

    main(args.video_id, args.categories_json)