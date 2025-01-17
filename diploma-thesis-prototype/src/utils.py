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

def process_segments_parallel(video_path, segments, output_dir, model_path, classes_to_detect, db_manager, video_id):
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
                args=(video_path, start_frame, end_frame, yolo_handler, results_queue, stop_event, db_manager, video_id),
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

def process_segment_and_store_results(video_path, start_frame, end_frame, yolo_handler, results_queue, stop_event, db_manager, video_id):
    try:
        # Spracovanie segmentu a získanie detekcií
        detections = process_segment(video_path, start_frame, end_frame, yolo_handler, stop_event, True)

        # Získanie pripojenia z poolu
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Mapovanie track_id na existujúcu detekciu
        detection_map = {}  # track_id -> detection_id

        for detection in detections:
            if 'class_id' not in detection or 'confidence' not in detection or 'bbox' not in detection:
                print(f"Detekcia chýba kľúč: {detection}")
                continue  # Ak nie je prítomný class_id alebo iné, preskočíme túto detekciu

            # Skontrolujeme, či už existuje detekcia pre tento track_id
            track_id = detection.get('track_id')

            if track_id not in detection_map:
                # Ak detekcia pre tento track_id neexistuje, vložíme novú detekciu
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
                # Ak detekcia pre tento track_id už existuje, aktualizujeme end_frame
                detection_id = detection_map[track_id]
                # Ak je tento frame nový a je neskôr než aktuálny end_frame, aktualizujeme end_frame
                current_end_frame = db_manager.fetch_detection_end_frame(detection_id)
                if detection['frame_id'] > current_end_frame:
                    db_manager.update_detection_end_frame(detection_id, detection['frame_id'])

            # Uloženie bounding boxu
            db_manager.insert_bounding_box(detection_id, detection['frame_id'], detection['bbox'])

        # Vrátenie pripojenia späť do poolu
        db_manager.release_connection(conn)

        results_queue.put(detections)
    except Exception as e:
        print(f"Chyba pri spracovaní segmentu {start_frame}-{end_frame}: {e}")

# TODO dorobit podla parallel
def process_segments_sequential(video_path, segments, output_dir, model_path, classes_to_detect, db_manager):
    """Sekvenčne spracuje segmenty videa a vráti detekcie pre každý segment."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    yolo_handler = YOLOHandler(model_path, classes_to_detect=classes_to_detect)

    all_detections = []
    for i, (start_frame, end_frame) in enumerate(segments):
        detections = process_segment(video_path, start_frame, end_frame, yolo_handler)

        # Získanie pripojenia z poolu
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Uloženie detekcií a bounding boxov do DB
        for detection in detections:
            if 'class_id' not in detection or 'confidence' not in detection or 'bbox' not in detection:
                print(f"Detekcia chýba kľúč: {detection}")
                continue  # Ak nie je prítomný class_id alebo iné, preskočíme túto detekciu
            # else:
            #     print(f"Detekcia: {detection}")

            # Vkladanie detekcie
            detection_id = db_manager.insert_detection(
                video_id=1,  # Predpokladáme, že video_id je 1, uprav podľa potreby
                start_frame=detection['frame_id'],
                end_frame=detection['frame_id'],
                class_id=detection['class_id'],
                confidence=detection['confidence'],
                track_id=detection['track_id']
            )

            # Uloženie bounding boxu
            db_manager.insert_bounding_box(detection_id, detection['frame_id'], detection['bbox'])

        # Vrátenie pripojenia späť do poolu
        db_manager.release_connection(conn)

        all_detections.append(detections)

    return all_detections


def print_detections(all_detections):
  for i, detections in enumerate(all_detections):
      print(f"Segment {i + 1} detekcie:")
      for detection in detections:
          print(f"Frame ID: {detection['frame_id']}, Track ID: {detection.get('track_id', 'N/A')}, Confidence: {detection['confidence']:.2f}, BBox: {detection['bbox']}")
