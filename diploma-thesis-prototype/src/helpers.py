# This script contains helper functions.

# The `print_detections_from_object_detection_processor` function prints details of detections from multiple segments,
# including frame ID, track ID (if available), confidence, and the bounding box coordinates.
# It helps in reviewing and logging detection results for debugging or analysis.
def print_detections_from_object_detection_processor(all_detections):
  for i, detections in enumerate(all_detections):
      print(f"Segment {i + 1} of detection:")
      for detection in detections:
          print(f"Frame ID: {detection['frame_id']}, Track ID: {detection.get('track_id', 'N/A')}, Confidence: {detection['confidence']:.2f}, BBox: {detection['bbox']}")