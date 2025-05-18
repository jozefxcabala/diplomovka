from ultralytics import YOLO

# This class, `YOLOHandler`, is designed to handle object detection and tracking using the YOLO model from the `ultralytics` library.
# It includes methods for:
# - Initializing the YOLO model with a specified path and setting the classes to detect.
# - Detecting objects in a given frame, filtering results by a confidence threshold, and returning the bounding boxes and associated class IDs.
# - Tracking objects across frames, leveraging the YOLO model's tracking capabilities with the "bytetrack" tracker.
# The class allows customization of the detection process by specifying which object classes to detect and setting a confidence threshold for filtering low-confidence detections.
class YOLOHandler:
    def __init__(self, model_path: str, classes_to_detect=None, verbose=False):
        self.classes_to_detect = classes_to_detect if classes_to_detect is not None else []
        self.verbose = verbose
        self.model = YOLO(model_path)

    def detect(self, frame, confidence_threshold=0.5):
        # you can add save=True to save model
        results = self.model(frame, classes=self.classes_to_detect, verbose=self.verbose) 
        filtered_results = []

        for result in results[0].boxes:
            class_id = int(result.cls[0]) 
            confidence = float(result.conf[0])

            if confidence >= confidence_threshold:
                filtered_results.append({
                    'class_id': class_id,
                    'confidence': confidence,
                    'bbox': result.xyxy[0].tolist()
                })

        return filtered_results
    
    # https://docs.ultralytics.com/modes/track/#persisting-tracks-loop
    def track(self, frame, confidence_threshold=0.5):
      results = self.model.track(source=frame, classes=self.classes_to_detect, verbose=self.verbose, tracker="bytetrack.yaml", persist=True)

      filtered_results = []
      if results and results[0].boxes: 
          for result in results[0].boxes:
              class_id = int(result.cls[0]) if result.cls is not None else None
              confidence = float(result.conf[0]) if result.conf is not None else None
              track_id = int(result.id[0]) if result.id is not None else None
              bbox = result.xyxy[0].tolist() if result.xyxy is not None else None

              if confidence is not None and confidence >= confidence_threshold and bbox is not None:
                  filtered_results.append({
                      'class_id': class_id,
                      'confidence': confidence,
                      'bbox': bbox,
                      'track_id': track_id
                  })

      return filtered_results




