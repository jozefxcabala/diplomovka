import cv2
import os
from threading import Thread, Event
from queue import Queue
from yolo_handler import YOLOHandler
from video_processor import process_segment

class DetectionInterruptedError(Exception):
    pass

# Split video into num_segment due to parallel processing
def split_video(video_path, num_segments):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    segment_length = total_frames // num_segments
    segments = []

    for i in range(num_segments):
        start_frame = i * segment_length
        end_frame = (i + 1) * segment_length if i < num_segments - 1 else total_frames
        segments.append((start_frame, end_frame))

    return segments

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

def print_detections(all_detections):
  for i, detections in enumerate(all_detections):
      print(f"Segment {i + 1} of detection:")
      for detection in detections:
          print(f"Frame ID: {detection['frame_id']}, Track ID: {detection.get('track_id', 'N/A')}, Confidence: {detection['confidence']:.2f}, BBox: {detection['bbox']}")
