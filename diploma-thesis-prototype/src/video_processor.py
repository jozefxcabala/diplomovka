import cv2

def process_video(video_path, output_path, yolo_handler, tracking=True):
    cap = cv2.VideoCapture(video_path)
    
    # Získanie parametrov pôvodného videa
    # frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Nastavenie VideoWriter na uloženie výstupného videa
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Použitie formátu MP4
    # out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    processed_frames = 0
    skip_frames = False
    num_of_skip_frames = 3
    all_detections = []  # Zoznam detekcií pre všetky snímky

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            if processed_frames == 0:
                print("\nChyba: Video sa nepodarilo načítať alebo je poškodené.")
            else:
                print("\nSpracovanie videa ukončené (koniec videa).")
            break

        if frame is None:
            print("\nChyba: Rámec je prázdny (None).")
            break
        
        # Preskoč snímky
        if skip_frames == True and (processed_frames % num_of_skip_frames != 0):  # Spracovať každú tretiu snímku
            processed_frames += 1
            continue
        
        # Detekcia objektov na aktuálnom frame
        detections = None
        if tracking:
            detections = yolo_handler.track(frame, confidence_threshold=0.01)
        else:
            detections = yolo_handler.detect(frame, confidence_threshold=0.01)

        if detections:
          for detection in detections:
              bbox = detection.get('bbox')
              confidence = detection.get('confidence')
              track_id = detection.get('track_id') if tracking else None

              if bbox and confidence is not None:
                  # Pridaj detekciu do zoznamu all_detections
                  all_detections.append({
                      'bbox': bbox,
                      'confidence': confidence,
                      'track_id': track_id
                  })

                  # x1, y1, x2, y2 = map(int, bbox)
                  # label = (
                  #     f"ID {track_id}: {confidence:.2f}" if tracking
                  #     else f"Person: {confidence:.2f}"
                  # )
                  # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                  # cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Uloženie aktuálneho frame do výstupného videa
        # out.write(frame)

        # Aktualizácia priebehu
        processed_frames += 1
        progress = (processed_frames / total_frames) * 100
        print(f"Spracované: {progress:.2f}%", end="\r")

    cap.release()
    # out.release()

    return all_detections

def process_segment(video_path, start_frame, end_frame, yolo_handler, tracking=True):
    """Spracuje segment videa a vráti detekcie."""
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)  # Nastaví na začiatok segmentu
    detections = []

    skip_frames = True
    num_of_skip_frames = 3

    for frame_idx in range(start_frame, end_frame):
        ret, frame = cap.read()
        if not ret:
            break
        
        if skip_frames == True and (frame_idx % num_of_skip_frames != 0):  # Spracovať každú tretiu snímku
            continue
        
        # Detekcia objektov na aktuálnom frame
        if tracking:
            frame_detections = yolo_handler.track(frame, confidence_threshold=0.01)
        else:
            frame_detections = yolo_handler.detect(frame, confidence_threshold=0.01)

        if frame_detections:
          for detection in frame_detections:
              bbox = detection.get('bbox')
              confidence = detection.get('confidence')
              track_id = detection.get('track_id') if tracking else None

              if bbox and confidence is not None:
                  # Pridaj detekciu do zoznamu all_detections
                  detections.append({
                      'frame_id': frame_idx,
                      'bbox': bbox,
                      'confidence': confidence,
                      'track_id': track_id
                  })

    cap.release()
    return detections