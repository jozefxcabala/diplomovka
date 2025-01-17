import cv2
from database_manager import DatabaseManager

skip_frames = False
num_of_skip_frames = 5

def assign_bounding_boxes_to_video(db_manager, video_id, video_path, output_video_path):
    """Priradí bounding boxy pre všetky detekcie v danom videu a uloží celé video."""
    # Získame všetky detekcie pre dané video_id
    detections = db_manager.fetch_detections_by_video_id(video_id)
    
    if not detections:
        print(f"Žiadne detekcie pre video s ID {video_id}.")
        return
    
    print(f"Priraďujem bounding boxy pre všetky detekcie v videu ID {video_id}.")
    
    # Načítať video
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Overenie, či sú rámce validné
    if total_frames <= 0:
        print("Chyba: Video nemá žiadne rámce.")
        return

    # Zabezpečíme, že bounding boxy sú priradené k správnym rámcom pre všetky detekcie
    all_bounding_boxes = {}
    for detection in detections:
        detection_id = detection['id']
        bounding_boxes = db_manager.fetch_bounding_boxes(detection_id)
        all_bounding_boxes[detection_id] = {bbox['frame_id']: bbox['bbox'] for bbox in bounding_boxes}

    # Načítame prvý rámec, aby sme zistili rozmery videa (šírka a výška)
    ret, frame = cap.read()
    if not ret:
        print("Chyba pri čítaní videa.")
        return

    # Získame rozmery videa
    height, width, _ = frame.shape

    # Nastavenie VideoWriter pre uloženie videa
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Kódovanie pre mp4
    out = cv2.VideoWriter(output_video_path, fourcc, 30.0, (width, height))

    # Pre každý rámec vo videu
    for frame_id in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break
        
        if skip_frames == True and (frame_id % num_of_skip_frames != 0):  # Spracovať každú n snímku
            continue
        
        # Pre každú detekciu, priradiť bounding boxy k rámcom
        for detection in detections:
            detection_id = detection['id']
            bbox = all_bounding_boxes.get(detection_id, {}).get(frame_id)

            if bbox:
                # Kreslenie bounding boxu na rámec
                x1, y1, x2, y2 = map(int, bbox)  # Prevod bounding boxu na celé čísla
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Nakreslíme zelený obdĺžnik

                # Pridanie textu (frame_id, track_id, detection_id) na obrázok
                label = f"Frame: {frame_id}, Track ID: {detection['track_id']}, Detection ID: {detection['id']}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Pridanie čísla frame_id do rohu videa
        cv2.putText(frame, f"Frame: {frame_id}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Uloženie rámca (aj keď nemá bounding box, bude uložený)
        out.write(frame)

    # Ukončujeme po dokončení
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Video bolo uložené do: {output_video_path}")

# Iniciujeme pripojenie k databáze a volanie funkcie
db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
db_manager.connect()

video_id = 33  # Zadaj ID videa, pre ktoré chceš spracovať detekcie
video_path = "../data/input/uvoz2.mp4"  # Zadaj cestu k videu
output_video_path = "../data/output/uvoz2_with_bboxes.mp4"  # Cesta k uloženému videu

assign_bounding_boxes_to_video(db_manager, video_id, video_path, output_video_path)

db_manager.close()
