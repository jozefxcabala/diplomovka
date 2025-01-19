import argparse
import time

from object_detection_processor import main as object_detection_processor
from anomaly_recognition_preprocessor import main as anomaly_recognition_preprocessor
from anomaly_recognition import main as anomaly_recognition
from helpers import create_folders

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare video data for analysis.")
    parser.add_argument('--video_path', required=True, type=str, help="Path to the input video file.")
    
    args = parser.parse_args()

    start_time = time.time()

    try:
        print("THE PROTOTYPE has started.")
        video_id = object_detection_processor(args.video_path, 8, 'parallel', '../data/models/yolo11n.pt', 0)
        create_folders(f'../data/output/{video_id}/anomaly_recognition_preprocessor')
        anomaly_recognition_preprocessor(video_id, args.video_path, f'../data/output/{video_id}/anomaly_recognition_preprocessor', 50, 200, 200)
        anomaly_recognition(args.video_path, "../data/input/list-of-categories.json", 5) # TODO prerobit aby to namiesto video_path bralo video_id a na zaklade toho si fetchlo vsetky detections - kde uvidi aj mena suborov ktore ma spracovat (dorobit parallel)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"THE PROTOTYPE finished. It took {elapsed_time:.2f} seconds.")

    