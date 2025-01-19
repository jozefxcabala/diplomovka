# This script is responsible for processing video segments for object detection using YOLO.
# The main tasks include:
# - Splitting the video into smaller segments for parallel processing using the `split_video` function.
# - Handling object detection and tracking within each segment.
# - Managing detections and bounding boxes, storing results in a database, and handling interruptions.
# 
# The `process_segments_parallel` function manages multiple threads that process video segments in parallel.
# Each thread performs detection or tracking on frames within the specified segment range, stores the results, and writes bounding boxes to the database.
# 
# The script can run in parallel mode, with the `parallel` mode utilizing Python's `Thread` to process video segments concurrently for improved performance.
# The program also includes error handling and graceful termination in case of manual interruptions.
# It also ensures that all threads are properly joined and terminated after processing.

import argparse
import time
from video_processor import split_video
from database_manager import DatabaseManager
import cv2
import os
from threading import Thread, Event
from queue import Queue
from yolo_handler import YOLOHandler

class DetectionInterruptedError(Exception):
    pass

def process_segments_parallel(video_path, segments, output_dir, model_path, classes_to_detect, db_manager, video_id):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    threads = []
    results_queue = Queue()
    stop_event = Event()

    # Create threads and divide data to process
    try:
        for i, (start_frame, end_frame) in enumerate(segments):
            yolo_handler = YOLOHandler(model_path, classes_to_detect=classes_to_detect)
            thread = Thread(
                target=process_segment_and_store_results,
                args=(video_path, start_frame, end_frame, yolo_handler, results_queue, stop_event, db_manager, video_id),
                daemon=True  # It will automatically terminate threads when the program ends.
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    except KeyboardInterrupt:
        print("\nDetection was interrupted. Terminating threads...")
        stop_event.set()
        for thread in threads:
            thread.join()
        raise DetectionInterruptedError("The detection was manually interrupted.")
    finally:
        print("All threads have been terminated.")

    all_detections = []

    # Get all results from treads to one all_detection list and return
    while not results_queue.empty():
        all_detections.append(results_queue.get())

    return all_detections

def process_segment_and_store_results(video_path, start_frame, end_frame, yolo_handler, results_queue, stop_event, db_manager, video_id):
    try:
        detections = process_segment(video_path, start_frame, end_frame, yolo_handler, stop_event, True, 5, True, 0.25)

        # Get connection to db from connection_pool
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        detection_map = {}  # track_id -> detection_id

        for detection in detections:
            if 'class_id' not in detection or 'confidence' not in detection or 'bbox' not in detection:
                print(f"Detection with ID ${detection} is missing key. Skipping...")
                continue 

            # Check if detection for this track_id exists
            track_id = detection.get('track_id')

            # if not, add new detection for this track_id
            if track_id not in detection_map:
                start_frame = detection['frame_id']
                end_frame = detection['frame_id']

                detection_id = db_manager.insert_detection(
                    video_id=video_id,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    class_id=detection['class_id'],
                    confidence=detection['confidence'],
                    track_id=track_id
                )

                detection_map[track_id] = detection_id
            else:
               # if exists, update end frame for this detecion
                detection_id = detection_map[track_id]
                current_end_frame = db_manager.fetch_detection_end_frame(detection_id)

                if detection['frame_id'] > current_end_frame:
                    db_manager.update_detection_end_frame(detection_id, detection['frame_id'])

            db_manager.insert_bounding_box(detection_id, detection['frame_id'], detection['bbox'])

        db_manager.release_connection(conn)

        results_queue.put(detections)
    except Exception as e:
        print(f"Error processing segment {start_frame}-{end_frame}: {e}")

def process_segment(video_path, start_frame, end_frame, yolo_handler, stop_event, skip_frames=True, num_of_skip_frames=5, tracking=True, confidence_threshold=0.25):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)  # Set on start of segment
    detections = []

    for frame_idx in range(start_frame, end_frame):
        if stop_event.is_set():
          print(f"Thread for segment {start_frame}-{end_frame} finished.")
          break

        ret, frame = cap.read()
        if not ret:
            break
        
        # Process every nth frame
        if skip_frames == True and (frame_idx % num_of_skip_frames != 0): 
            continue
        
        if tracking:
            frame_detections = yolo_handler.track(frame, confidence_threshold=confidence_threshold)
        else:
            frame_detections = yolo_handler.detect(frame, confidence_threshold=confidence_threshold)

        if frame_detections:
          for detection in frame_detections:
              class_id = detection.get('class_id')
              bbox = detection.get('bbox')
              confidence = detection.get('confidence')
              track_id = detection.get('track_id') if tracking else None

              if bbox and confidence is not None:
                  detections.append({
                      'class_id': class_id,
                      'frame_id': frame_idx,
                      'bbox': bbox,
                      'confidence': confidence,
                      'track_id': track_id
                  })

    cap.release()
    return detections


def main(video_path, num_segments, processing_mode, output_dir, model_path, classes_to_detect):
    # Initialization of the database manager
    db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    
    try:
        db_manager.connect()
        db_manager.create_tables()
        video_id = db_manager.insert_video(video_path)

        start_time = time.time()

        segments = split_video(video_path, num_segments)

        try:
            print("\nThe detection has started.")
            
            if processing_mode == 'parallel':
                all_detections = process_segments_parallel(
                    video_path, segments, output_dir, model_path, classes_to_detect, db_manager, video_id
                )

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

    except Exception as e:
        print(f"Database error: {e}")
    
    finally:
        db_manager.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YOLO video processing with segment-based detection.")
    parser.add_argument("--video_path", type=str, required=True, help="Path to the input video.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to store processed segments.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the YOLO model.")
    parser.add_argument("--num_segments", type=int, default=8, help="Number of segments to split the video into.")
    parser.add_argument("--processing_mode", type=str, choices=["parallel", "sequential"], default="parallel",
                        help="Processing mode: parallel or sequential.")
    parser.add_argument("--classes_to_detect", type=int, nargs="+", default=[0],
                        help="List of YOLO class IDs to detect (default is person class: [0]).")

    args = parser.parse_args()

    main(args.video_path, args.num_segments, args.processing_mode, args.output_dir, args.model_path, args.classes_to_detect)