import cv2

def process_video(video_path, output_path, yolo_handler):
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Detekcia objektov na aktuálnom frame
        detections = yolo_handler.detect(frame, confidence_threshold=0.2)

        # Zobrazíme detekcie (voliteľné)
        for detection in detections:
            x1, y1, x2, y2 = map(int, detection['bbox'])
            confidence = detection['confidence']
            label = f"Person: {confidence:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow("Detections", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def save_clip(frame, output_path):
    pass