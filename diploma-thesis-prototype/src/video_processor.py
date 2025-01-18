import cv2

# This function, `process_segment`, processes a segment of a video and performs object detection or tracking using a YOLO handler.
# It includes the following features:
# - Opens the video file and sets the frame position to the start of the segment.
# - Loops through frames from `start_frame` to `end_frame`, and processes every nth frame based on the `skip_frames` argument.
# - Performs either object detection or tracking for each frame using the YOLO handler, depending on the `tracking` flag.
# - For each detection, it collects information such as class ID, bounding box, confidence, and track ID (if tracking is enabled).
# - Stops processing if the `stop_event` is set, and returns a list of detections within the specified frame range.
def process_segment(video_path, start_frame, end_frame, yolo_handler, stop_event, skip_frames=True, num_of_skip_frames=5, tracking=True, confidence_threshold=0.25):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)  # Set on start of segment
    detections = []

    for frame_idx in range(start_frame, end_frame):
        if stop_event.is_set():
          print(f"Thread for segment {start_frame}-{end_frame} finished.")
          break

        ret, frame = cap.read()
        if not ret:
            break
        
        # Process every nth frame
        if skip_frames == True and (frame_idx % num_of_skip_frames != 0): 
            continue
        
        if tracking:
            frame_detections = yolo_handler.track(frame, confidence_threshold=confidence_threshold)
        else:
            frame_detections = yolo_handler.detect(frame, confidence_threshold=confidence_threshold)

        if frame_detections:
          for detection in frame_detections:
              class_id = detection.get('class_id')
              bbox = detection.get('bbox')
              confidence = detection.get('confidence')
              track_id = detection.get('track_id') if tracking else None

              if bbox and confidence is not None:
                  detections.append({
                      'class_id': class_id,
                      'frame_id': frame_idx,
                      'bbox': bbox,
                      'confidence': confidence,
                      'track_id': track_id
                  })

    cap.release()
    return detections