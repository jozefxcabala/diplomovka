from xclip_handler import XCLIPHandler
import time
import argparse
import json
from helpers import display_results_from_anomaly_recognition

def main(video_path, categories_json, probability_threshold):
    print(f"The XCLIP - Action Recognition program has started.")

    start_time = time.time()

    # Load categories from the provided JSON file
    with open(categories_json, 'r') as f:
        list_of_categories = json.load(f)

    # Initialize XCLIP handler
    handler = XCLIPHandler(list_of_categories)
    
    # Analyze video and get results
    results = handler.analyze_video(video_path, batch_size=32)
    
    # Display results with the given threshold
    display_results_from_anomaly_recognition(results, list_of_categories, probability_threshold)
    
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Program finished. It took {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run XCLIP Action Recognition")
    parser.add_argument('--video_path', required=True, type=str, help="Path to the video file")
    parser.add_argument('--categories_json', required=True, type=str, help="Path to the JSON file containing categories")
    parser.add_argument('--probability_threshold', required=True, type=float, help="Probability threshold for displaying results")
    
    args = parser.parse_args()

    main(args.video_path, args.categories_json, args.probability_threshold)