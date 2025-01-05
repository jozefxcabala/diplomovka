import cv2
import time

def process_video(video_path, output_path, yolo_handler, tracking=True):
    cap = cv2.VideoCapture(video_path)
    
    # Získanie parametrov pôvodného videa
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Nastavenie VideoWriter na uloženie výstupného videa
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Použitie formátu MP4
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    start_time = time.time()  # Začiatok merania času
    processed_frames = 0

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

        # Detekcia objektov na aktuálnom frame
        detections = None
        if tracking:
            detections = yolo_handler.track(frame, confidence_threshold=0.01)
        else:
            detections = yolo_handler.detect(frame, confidence_threshold=0.01)

        # Kreslenie detekcií na frame
        if detections:
            for detection in detections:
                bbox = detection.get('bbox')
                confidence = detection.get('confidence')
                track_id = detection.get('track_id') if tracking else None

                if bbox and confidence is not None:
                    x1, y1, x2, y2 = map(int, bbox)
                    label = (
                        f"ID {track_id}: {confidence:.2f}" if tracking
                        else f"Person: {confidence:.2f}"
                    )
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Uloženie aktuálneho frame do výstupného videa
        out.write(frame)

        # Aktualizácia priebehu
        processed_frames += 1
        progress = (processed_frames / total_frames) * 100
        elapsed_time = time.time() - start_time
        print(f"Spracované: {progress:.2f}% - Uplynulý čas: {elapsed_time:.2f} s", end="\r")

    cap.release()
    out.release()

    # Celkový čas spracovania
    total_time = time.time() - start_time
    print(f"\nSpracovanie dokončené za {total_time:.2f} sekúnd.")
