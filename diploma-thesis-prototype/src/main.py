import argparse
import time
from utils import split_video, process_segments_parallel, process_segments_sequential, print_detections, DetectionInterruptedError

def main():
    # Nastavenie argumentov príkazového riadku
    parser = argparse.ArgumentParser(description="YOLO video processing with segment-based detection.")
    parser.add_argument("--video_path", type=str, required=True, help="Path to the input video.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to store processed segments.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the YOLO model.")
    parser.add_argument("--num_segments", type=int, default=8, help="Number of segments to split the video into.")
    parser.add_argument("--processing_mode", type=str, choices=["parallel", "sequential"], default="parallel",
                        help="Processing mode: parallel or sequential.")
   # https://gist.githubusercontent.com/rcland12/dc48e1963268ff98c8b2c4543e7a9be8/raw/43a947ccbfbcba2b404e36bb7aee7332b5fd0c89/yolo_classes.json
    parser.add_argument("--classes_to_detect", type=int, nargs="+", default=[0],
                        help="List of YOLO class IDs to detect (default is person class: [0]).")

    args = parser.parse_args()

    # Začiatok merania času
    start_time = time.time()

    # Rozdelenie videa na segmenty
    segments = split_video(args.video_path, args.num_segments)

    try:
        print("\nDetekcia bola zacata.")

        if args.processing_mode == 'parallel':
            all_detections = process_segments_parallel(
                args.video_path, segments, args.output_dir, args.model_path, args.classes_to_detect
            )
        else:
            all_detections = process_segments_sequential(
                args.video_path, segments, args.output_dir, args.model_path, args.classes_to_detect
            )

        print_detections(all_detections)

    except DetectionInterruptedError as e:
        print("\nDetekcia bola manuálne prerušená. Ukončujem program.")
    except KeyboardInterrupt:
        print("\nDetekcia bola manuálne prerušená. Ukončujem program.")
    except Exception as e:
        print(f"Vyskytla sa neočakávaná chyba: {e}")
    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Program ukončený. Trvalo to {elapsed_time:.2f} sekúnd.")

if __name__ == "__main__":
    main()
