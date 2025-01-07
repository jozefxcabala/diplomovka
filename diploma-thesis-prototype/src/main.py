from video_processor import process_video
from utils import split_video, process_segments_parallel, process_segments_sequential

import time

def main():
    video_path = "../data/input/street3m.mp4"
    output_path = "../data/output/clips/street_output.mp4"
    output_dir = "../data/output/clips"
    model_path = "../data/models/yolo11n.pt"
    num_segments = 8
    processing_mode = "parallel"
    # processing_mode = "sequential"

    # Triedy na detekciu (len 'person', ktorá zodpovedá triede [0])
    # https://gist.githubusercontent.com/rcland12/dc48e1963268ff98c8b2c4543e7a9be8/raw/43a947ccbfbcba2b404e36bb7aee7332b5fd0c89/yolo_classes.json
    classes_to_detect = [0]  # YOLO trieda pre 'person'

    start_time = time.time()

    segments = split_video(video_path, num_segments)


    try:
        if processing_mode == 'parallel':
            # save_segments_parallel(video_path, segments, output_dir)
            all_detections = process_segments_parallel(video_path, segments, output_dir, model_path, classes_to_detect)
        else:
            # save_segments_sequential(video_path, segments, output_dir)
            all_detections = process_segments_sequential(video_path, segments, output_dir, model_path, classes_to_detect)
        # process_video(video_path, output_path, yolo)

        for i, detections in enumerate(all_detections):
            print(f"Segment {i + 1} detekcie:")
            for detection in detections:
                print(f"Frame ID: {detection['frame_id']}, Track ID: {detection.get('track_id', 'N/A')}, Confidence: {detection['confidence']:.2f}, BBox: {detection['bbox']}")

    except KeyboardInterrupt:
        print("\nDetekcia bola manuálne prerušená. Ukončujem program.")
    except Exception as e:
        print(f"Vyskytla sa neočakávaná chyba: {e}")
    finally:
        end_time = time.time()  # Konec merania času
        elapsed_time = end_time - start_time
        print(f"Program ukončený. Trvalo to {elapsed_time:.2f} sekúnd.")

if __name__ == "__main__":
    main()
