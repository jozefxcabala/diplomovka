import time
import argparse
import torch
import numpy as np
from database_manager import DatabaseManager

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
    

def main(video_id):
    print(f"The result interpreter program has started.")

    db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    
    start_time = time.time()

    logits_per_video = get_logits_per_video(db_manager, video_id)
    print("LOGITS: ", logits_per_video)
    
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Program finished. It took {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run Result Interpreter")
    parser.add_argument('--video_id', required=True, type=int, help="ID of video source in database")
    
    args = parser.parse_args()

    main(args.video_id)