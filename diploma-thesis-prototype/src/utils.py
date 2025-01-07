import cv2
import os
from threading import Thread
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from yolo_handler import YOLOHandler
from video_processor import process_segment
from queue import Queue

def split_video(video_path, num_segments):
    """Rozdelí video na rovnomerné segmenty podľa počtu snímok (frames)."""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Získa počet všetkých snímok
    fps = cap.get(cv2.CAP_PROP_FPS)  # Získa FPS
    cap.release()

    segment_length = total_frames // num_segments  # Počet snímok na segment
    segments = []

    for i in range(num_segments):
        start_frame = i * segment_length
        end_frame = (i + 1) * segment_length if i < num_segments - 1 else total_frames
        segments.append((start_frame, end_frame))

    return segments

# def process_segment(video_path, start_frame, end_frame, output_path):
#     """Spracuje segment videa a uloží ho do súboru."""
#     cap = cv2.VideoCapture(video_path)
#     cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)  # Nastaví na začiatok segmentu
#     frames = []

#     for frame_idx in range(start_frame, end_frame):
#         ret, frame = cap.read()
#         if not ret:
#             break
#         frames.append(frame)

#     # Uloží segment ako video
#     if frames:
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#         out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (frames[0].shape[1], frames[0].shape[0]))
#         for frame in frames:
#             out.write(frame)
#         out.release()
    
#     cap.release()

# def save_segments_parallel(video_path, segments, output_dir):
#     """Paralelne uloží segmenty videa ako samostatné súbory pomocou vlákien."""
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     threads = []
#     for i, (start_frame, end_frame) in enumerate(segments):
#         output_path = os.path.join(output_dir, f"segment_{i + 1}.mp4")
#         thread = Thread(target=process_segment, args=(video_path, start_frame, end_frame, output_path))
#         threads.append(thread)
#         thread.start()

#     for thread in threads:
#         thread.join()  # Čaká na dokončenie všetkých vlákien

# def save_segments_sequential(video_path, segments, output_dir):
#     """Sekvenčne uloží segmenty videa ako samostatné súbory."""
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     for i, (start_frame, end_frame) in enumerate(segments):
#         output_path = os.path.join(output_dir, f"segment_{i + 1}.mp4")
#         process_segment(video_path, start_frame, end_frame, output_path)

def process_segments_parallel(video_path, segments, output_dir, model_path, classes_to_detect):
    """Paralelne spracuje segmenty videa a vráti detekcie pre každý segment."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    threads = []
    results_queue = Queue()  # This queue will collect results from threads

    # Spustí vlákna, kde každé vlákno bude mať svoj vlastný YOLOHandler
    for i, (start_frame, end_frame) in enumerate(segments):
        # https://docs.ultralytics.com/guides/yolo-thread-safe-inference/#why-should-each-thread-have-its-own-yolo-model-instance
        yolo_handler = YOLOHandler(model_path, classes_to_detect=classes_to_detect)
        # The lambda function is used to pass the correct arguments to the target function
        thread = Thread(target=process_segment_and_store_results, args=(video_path, start_frame, end_frame, yolo_handler, results_queue))
        threads.append(thread)
        thread.start()

    # Čaká na dokončenie všetkých vlákien
    for thread in threads:
        thread.join()

    # Collecting all detections from the queue
    all_detections = []
    while not results_queue.empty():
        # print(results_queue.get())
        all_detections.append(results_queue.get())

    return all_detections

def process_segment_and_store_results(video_path, start_frame, end_frame, yolo_handler, results_queue):
    """Wrapper function to process segment and store results in a queue."""
    detections = process_segment(video_path, start_frame, end_frame, yolo_handler)
    results_queue.put(detections)  # Put detections into the queue

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