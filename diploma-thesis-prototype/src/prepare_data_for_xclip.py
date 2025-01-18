import os
import cv2
from database_manager import DatabaseManager

def fetch_detections_and_bounding_boxes(video_id, db_manager):
    detections = db_manager.fetch_detections_by_video_id(video_id)
    all_bounding_boxes = {}

    for detection in detections:
        detection_id = detection['id']
        bounding_boxes = db_manager.fetch_bounding_boxes(detection_id)
        all_bounding_boxes[detection_id] = bounding_boxes

    return detections, all_bounding_boxes

def crop_video_for_detection(video_path, detection, bounding_boxes, output_dir, video_id, debug_flag=False):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Chyba pri otvorení videa: {video_path}")
        return
    else:
        print(len(bounding_boxes), " - ", detection['id'])

    output_video_path = os.path.join(output_dir, f"video_{video_id}_detection_{detection['id']}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Použitie XVID codec
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)


    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
    
    # Nastavujeme nové rozmery na základe výrezu
    x, y, w, h = bounding_boxes[0]['bbox']  # Používame len prvý bounding box na testovanie
    x_offset, y_offset = 20, 20  # Môžeš nastaviť vlastné hodnoty offsetu
    cropped_width = min(frame_width, int(x) + int(w) + x_offset) - max(0, int(x) - x_offset)
    cropped_height = min(frame_height, int(y) + int(h) + y_offset) - max(0, int(y) - y_offset)

    out = cv2.VideoWriter(output_video_path, fourcc, fps, (cropped_width, cropped_height))
    if not out.isOpened():
        print(f"Chyba pri vytváraní VideoWriter pre {output_video_path}.")
        return

    # Spracovanie snímkov
    for frame_idx in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
        ret, frame = cap.read()
        if not ret:
            break
        
        # Skontroluj, či sa bbox zhoduje s aktuálnym frame_idx
        for bbox in bounding_boxes:
            if bbox['frame_id'] == frame_idx:  # Porovnanie frame_id s aktuálnym frame_idx
                x, y, w, h = bbox['bbox']
                x_offset, y_offset = 20, 20

                # print(x, " - ", y, " - ", w, " - ", h)

                x1 = max(0, int(x) - x_offset)
                y1 = max(0, int(y) - y_offset)
                x2 = min(frame_width, int(x) + int(w) + x_offset)
                y2 = min(frame_height, int(y) + int(h) + y_offset)

                # print(x1, " - ", y1, " - ", x2, " - ", y2)

                cropped_frame = frame[y1:y2, x1:x2]
                out.write(cropped_frame)
                break
              

    print("AHOJ")
    cap.release()
    out.release()
    cv2.destroyAllWindows()

def prepare_data_for_clip(video_id, video_path, db_manager, output_dir, debug_flag=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    detections, all_bounding_boxes = fetch_detections_and_bounding_boxes(video_id, db_manager)

    if debug_flag:
        detections = detections[:1]

    for detection in detections:
        detection_id = detection['id']
        
        # TODO potom zmazat
        if float(detection['confidence']) < 0.70:
            continue
        
        bounding_boxes = all_bounding_boxes.get(detection_id, [])
        
        if not bounding_boxes:
            print(f"Žiadne bounding boxy pre detekciu {detection_id}. Preskakujem...")
            continue
        
        crop_video_for_detection(video_path, detection, bounding_boxes, output_dir, video_id, debug_flag)

        break

if __name__ == "__main__":
    db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db_manager.connect()

    video_id = 36
    video_path = '../data/input/uvoz2.mp4'
    output_dir = '../data/output/xclip-data'

    prepare_data_for_clip(video_id, video_path, db_manager, output_dir, debug_flag=False)

    db_manager.close()
