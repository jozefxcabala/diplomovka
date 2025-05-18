# This script contains helper functions.

import os
from backend.app.core.database_manager import DatabaseManager

# The `print_detections_from_object_detection_processor` function prints details of detections from multiple segments,
# including frame ID, track ID (if available), confidence, and the bounding box coordinates.
# It helps in reviewing and logging detection results for debugging or analysis.
def print_detections_from_object_detection_processor(all_detections):
  for i, detections in enumerate(all_detections):
      print(f"Segment {i + 1} of detection:")
      for detection in detections:
          print(f"Frame ID: {detection['frame_id']}, Track ID: {detection.get('track_id', 'N/A')}, Confidence: {detection['confidence']:.2f}, BBox: {detection['bbox']}")

# The `display_results_from_anomaly_recognition` function prints the results of anomaly recognition.
# It displays the descriptions of detected anomalies along with their probabilities, filtering results based on a specified probability threshold.
# This function helps in visualizing and analyzing the outcomes of anomaly detection in batches, making it easier to identify high-probability anomalies.
def display_results_from_anomaly_recognition(videos, list_of_categories, probability_threshold):
    for detection_id, video in videos:
        print(f"Detection ID {detection_id}:")
        for idx, result in enumerate(video):
            print(f"Batch {idx+1}:")
            for i, prob in enumerate(result[0]):
                description = list_of_categories[i]
                probability = prob.item() * 100  # Convert to percentage
                if probability > probability_threshold:
                    print(f"Description: {description} - Probability: {probability:.2f}%")
            print("------------")

def create_folders(path):
    os.makedirs(path, exist_ok=True)

def show_anomalies_in_video(video_id):
    results = []
    try:
        db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
        db_manager.connect()
        results = db_manager.fetch_anomalies_by_video_id(video_id)
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        db_manager.close()
        print(f"I FIND OUT THESE ANOMALIES IN VIDEO: {results}")

# db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
# db_manager.connect()

# db_manager.drop_tables()