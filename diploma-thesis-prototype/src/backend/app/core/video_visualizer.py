import cv2
import os
from backend.app.core.database_manager import DatabaseManager

def show_anomalies_in_video(video_id: int):
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()

    video_path = db.fetch_video_path(video_id)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    anomalies = db.fetch_anomalies_by_video_id(video_id)

    # Zoznam rozsahov kde sa má zobraziť červený rám
    anomaly_frame_ranges = []
    for anomaly in anomalies:
        anomaly_frame_ranges.append((anomaly["start_frame"], anomaly["end_frame"]))

    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    output_path = f"../data/output/{video_id}/final_output.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    current_frame = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Over, či aktuálny frame patrí do niektorej z anomálnych sekvencií
        for start, end in anomaly_frame_ranges:
            if start <= current_frame <= end:
                # 🔴 Rám okolo celého obrázka (hrúbka 6)
                cv2.rectangle(frame, (0, 0), (width-1, height-1), (0, 0, 255), 6)
                break  # ak už je v niektorej anomálii, nemusíme overovať ďalšie

        out.write(frame)
        current_frame += 1

    cap.release()
    out.release()
    db.close()
    print(f"✅ Saved to {output_path}")
