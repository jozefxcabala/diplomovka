import cv2
import os
from threading import Thread, Event
from queue import Queue
from yolo_handler import YOLOHandler
from video_processor import process_segment

class DetectionInterruptedError(Exception):
    pass

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

def process_segments_parallel(video_path, segments, output_dir, model_path, classes_to_detect):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    threads = []
    results_queue = Queue()
    stop_event = Event()

    try:
        for i, (start_frame, end_frame) in enumerate(segments):
            yolo_handler = YOLOHandler(model_path, classes_to_detect=classes_to_detect)
            thread = Thread(
                target=process_segment_and_store_results,
                args=(video_path, start_frame, end_frame, yolo_handler, results_queue, stop_event),
                daemon=True  # Automaticky ukončí vlákna pri ukončení programu
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    except KeyboardInterrupt:
        print("\nDetekcia bola prerušená. Ukončujem vlákna...")
        stop_event.set()
        for thread in threads:
            thread.join()
        raise DetectionInterruptedError("Detekcia bola manuálne prerušená.")
    finally:
        print("Všetky vlákna ukončené.")

    all_detections = []
    while not results_queue.empty():
        all_detections.append(results_queue.get())

    return all_detections

def process_segment_and_store_results(video_path, start_frame, end_frame, yolo_handler, results_queue, stop_event):
    try:
        detections = process_segment(video_path, start_frame, end_frame, yolo_handler, stop_event, True)
        results_queue.put(detections)
    except Exception as e:
        print(f"Chyba pri spracovaní segmentu {start_frame}-{end_frame}: {e}")

def process_segments_sequential(video_path, segments, output_dir, model_path, classes_to_detect):
    """Sekvenčne spracuje segmenty videa a vráti detekcie pre každý segment."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    yolo_handler = YOLOHandler(model_path, classes_to_detect=classes_to_detect)

    all_detections = []
    for i, (start_frame, end_frame) in enumerate(segments):
        detections = process_segment(video_path, start_frame, end_frame, yolo_handler)
        all_detections.append(detections)

    return all_detections

def print_detections(all_detections):
  for i, detections in enumerate(all_detections):
      print(f"Segment {i + 1} detekcie:")
      for detection in detections:
          print(f"Frame ID: {detection['frame_id']}, Track ID: {detection.get('track_id', 'N/A')}, Confidence: {detection['confidence']:.2f}, BBox: {detection['bbox']}")
