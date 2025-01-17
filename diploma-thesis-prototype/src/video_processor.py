import cv2

def process_segment(video_path, start_frame, end_frame, yolo_handler, stop_event, tracking=True):
    """Spracuje segment videa a vráti detekcie."""
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)  # Nastaví na začiatok segmentu
    detections = []

    skip_frames = False
    num_of_skip_frames = 5

    for frame_idx in range(start_frame, end_frame):
        if stop_event.is_set():
          print(f"Vlákno pre segment {start_frame}-{end_frame} ukončené.")
          break

        ret, frame = cap.read()
        if not ret:
            break
        
        if skip_frames == True and (frame_idx % num_of_skip_frames != 0):  # Spracovať každú n snímku
            continue
        
        if tracking:
            frame_detections = yolo_handler.track(frame, confidence_threshold=0.8)
        else:
            frame_detections = yolo_handler.detect(frame, confidence_threshold=0.8)

        if frame_detections:
          for detection in frame_detections:
              class_id = detection.get('class_id')
              bbox = detection.get('bbox')
              confidence = detection.get('confidence')
              track_id = detection.get('track_id') if tracking else None

              if bbox and confidence is not None:
                  # Pridaj detekciu do zoznamu all_detections
                  detections.append({
                      'class_id': class_id,
                      'frame_id': frame_idx,
                      'bbox': bbox,
                      'confidence': confidence,
                      'track_id': track_id
                  })

    cap.release()
    return detections