import argparse
import time
from utils import split_video, process_segments_parallel, DetectionInterruptedError
from database_manager import DatabaseManager

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

    # Initialization of the database manager
    db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    
    try:
        db_manager.connect()
        db_manager.create_tables()
        video_id = db_manager.insert_video(args.video_path)

        start_time = time.time()

        segments = split_video(args.video_path, args.num_segments)

        try:
            print("\nThe detection has started.")
            
            if args.processing_mode == 'parallel':
                all_detections = process_segments_parallel(
                    args.video_path, segments, args.output_dir, args.model_path, args.classes_to_detect, db_manager, video_id
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
