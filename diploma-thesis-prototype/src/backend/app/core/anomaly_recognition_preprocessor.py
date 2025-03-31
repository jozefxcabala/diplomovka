import os
import cv2
from backend.app.core.database_manager import DatabaseManager
import argparse
import time
from multiprocessing import Pool
import signal
from typing import Dict, List, Tuple

# This script is designed to prepare video data for XCLIP action recognition by processing video segments.
# The main tasks of this script include:
# - Fetching video detections and bounding boxes from a database.
# - Cropping video frames based on bounding boxes, applying offsets, and handling significant size changes in bounding boxes.
# - Using the `multiprocessing` module to parallelize the cropping of frames for multiple detections.
# - Handling manual interruption of the program, gracefully terminating threads when a `KeyboardInterrupt` or a custom `DetectionInterruptedError` is raised.
# The program can be customized with command-line arguments, such as:
# - `video_id`: The ID of the video to process.
# - `video_path`: The path to the input video file.
# - `output_dir`: The directory where cropped videos will be saved.
# - `size_threshold`: The threshold for detecting significant changes in bounding box size.
# - `offset_x` and `offset_y`: Offsets for bounding box cropping along the x and y axes.
# It processes each video segment based on the start and end frames, performs object detection or tracking, and stores the results in the output directory.

class DetectionInterruptedError(Exception):
    pass

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def create_bb_map(bounding_boxes): 
    bb_map = {}

    for bb in bounding_boxes:
        bb_map[int(bb['frame_id'])] = list(map(int, bb['bbox']))

    return bb_map


def find_max_bounding_box(size_treshold, frame_bbox_map: Dict[int, List[Tuple[str, str, str, str]]]) -> Tuple[int, int, int, int]:
    min_x1 = float('+inf')
    min_y1 = float('+inf')
    max_x2 = float('-inf')
    max_y2 = float('-inf')

    for frame_id, bbox in frame_bbox_map.items():
        try:
            x1, y1, x2, y2 = map(int, bbox)
        except ValueError:
            raise ValueError(f"The bounding box contains non-convertible values in frame {frame_id}: {bbox}")
        finally:
            min_x1 = min(min_x1, x1)
            min_y1 = min(min_y1, y1)
            max_x2 = max(max_x2, x2)
            max_y2 = max(max_y2, y2)
    
    return min_x1, min_y1, max_x2, max_y2

def fetch_detections_and_bounding_boxes(video_id, db_manager):
    detections = db_manager.fetch_detections_by_video_id(video_id)
    all_bounding_boxes = {}

    for detection in detections:
        detection_id = detection['id']
        bounding_boxes = db_manager.fetch_bounding_boxes_by_detection_id(detection_id)
        all_bounding_boxes[detection_id] = create_bb_map(bounding_boxes)

    return detections, all_bounding_boxes

def crop_video_for_detection(args):
    input_video_path, detection, max_bb, output_dir, video_id, offset_x, offset_y, size_threshold = args
    cap = cv2.VideoCapture(input_video_path)
    output_video_path = os.path.join(output_dir, f"{video_id}_{detection['id']}.mp4")
    
    init_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
    init_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    x1, y1, x2, y2 = map(int, max_bb)
        
    x1 = max(0, x1 - offset_x)
    y1 = max(0, y1 - offset_y)
    x2 = min(init_width, x2 + offset_x)
    y2 = min(init_height, y2 + offset_y)
    
    fps = cap.get(cv2.CAP_PROP_FPS) 
    width = abs(x2-x1)
    height = abs(y2-y1)
        
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    detection_start_frame = detection['start_frame']
    detection_end_frame = detection['end_frame']

    cap.set(cv2.CAP_PROP_POS_FRAMES, detection_start_frame)
    
    for frame_idx in range(detection_start_frame, detection_end_frame + 1):
        ret, frame = cap.read()
        if not ret:
            break 
        
        cropped_frame = frame[y1:y2, x1:x2]
        
        out.write(cropped_frame)
            
    cap.release()
    out.release()

def prepare_data_for_xclip(video_id, video_path, db_manager, output_dir, offset_x, offset_y, size_threshold):
    detections, all_bounding_boxes = fetch_detections_and_bounding_boxes(video_id, db_manager)

    args_list = []
    for detection in detections:
        detection_id = detection['id']
        bounding_boxes = all_bounding_boxes.get(detection_id, [])
        max_bb = find_max_bounding_box(size_threshold, bounding_boxes)
        
        if not bounding_boxes:
            print(f"No bounding boxes for detection {detection_id}. Skipping...")
            continue
        
        args_list.append((video_path, detection, max_bb, output_dir, video_id, offset_x, offset_y, size_threshold))

    # Parallel processing using multiprocessing Pool
    try:
        with Pool(initializer=init_worker) as pool:
            pool.map(crop_video_for_detection, args_list)
    except KeyboardInterrupt:
        print("\nDetection was interrupted. Terminating threads...")
        pool.terminate()
        raise DetectionInterruptedError("The detection was manually interrupted.")
    finally:
        print("All threads have been terminated.")

def main(video_id, video_path, output_dir, offset_x, offset_y, size_threshold):
    db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db_manager.connect()
    
    start_time = time.time()

    try:
        print("The program for preparing data for XCLIP action recognition has started.")

        prepare_data_for_xclip(video_id, video_path, db_manager, output_dir, offset_x, offset_y, size_threshold)

    except DetectionInterruptedError as e:
        print("\nThe detection was manually interrupted. Shutting down the program.")
    except KeyboardInterrupt:
        print("\nThe detection was manually interrupted. Shutting down the program.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"Program finished. It took {elapsed_time:.2f} seconds.")

        db_manager.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare video data for analysis.")
    parser.add_argument('--video_id', required=True, type=int, help="ID of the video to process.")
    parser.add_argument('--video_path', required=True, type=str, help="Path to the input video file.")
    parser.add_argument('--output_dir', required=True, type=str, help="Directory where cropped videos will be saved.")
    parser.add_argument('--size_threshold', required=True, type=int, help="Threshold for bounding box size change.")
    parser.add_argument('--offset_x', required=True, type=int, help="Offset for bounding box cropping (x-axis).")
    parser.add_argument('--offset_y', required=True, type=int, help="Offset for bounding box cropping (y-axis).")
    
    args = parser.parse_args()

    main(args.video_id, args.video_path, args.output_dir, args.offset_x, args.offset_y, args.size_threshold)
