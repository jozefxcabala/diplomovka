import os
import cv2
from database_manager import DatabaseManager

def create_bb_map(bounding_boxes): 
    bb_map = {}

    for bb in bounding_boxes:
        bb_map[int(bb['frame_id'])] = list(map(int, bb['bbox']))

    return bb_map

def fetch_detections_and_bounding_boxes(video_id, db_manager):
    detections = db_manager.fetch_detections_by_video_id(video_id)
    all_bounding_boxes = {}

    for detection in detections:
        detection_id = detection['id']
        bounding_boxes = db_manager.fetch_bounding_boxes(detection_id)
        all_bounding_boxes[detection_id] = create_bb_map(bounding_boxes)

    return detections, all_bounding_boxes

def crop_video_for_detection(input_video_path, detection, frame_bbox_map, output_dir, video_id):
    # Otvorte vstupné video
    cap = cv2.VideoCapture(input_video_path)
    output_video_path = os.path.join(output_dir, f"video_{video_id}_detection_{detection['id']}.mp4")
    
    # Získajte vlastnosti videa
    fps = cap.get(cv2.CAP_PROP_FPS)  # snímková frekvencia
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # šírka rámu
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # výška rámu
        
    # Inicializácia výstupného video zapisovača (rozlíšenie podľa výrezu)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    frame_count = 0  # Počítadlo snímok
    out = None

    offset_x=200
    offset_y=200

    prev_bbox = None
    size_threshold = 50
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break  # Koniec videa
        
        # Skontrolujte, či frame_id existuje v mape
        if frame_count in frame_bbox_map or(frame_count > int(detection['start_frame']) and frame_count < int(detection['end_frame'])):
            bbox = frame_bbox_map.get(frame_count, False)

            # Vykonajte výrez rámu podľa bbox
            if bbox:
                x1, y1, x2, y2 = map(int, bbox)
            else: 
                x1, y1, x2, y2 = prev_bbox

            if prev_bbox and (abs(prev_bbox[2] - x2) > size_threshold or abs(prev_bbox[3] - y2) > size_threshold):
                    print(f"Veľkosť bboxu sa zmenila výrazne, použijem predchádzajúce rozmery.")
                    x1, y1, x2, y2 = prev_bbox  # Použijeme predchádzajúci bounding box pre pozíciu a veľkosť
            else:
                prev_bbox = (x1, y1, x2, y2)  # Ulož predchádzajúci bounding box
            
            # Zohľadnite offsety, ale zabezpečte, že neprekročia rozmery videa
            x1 = max(0, x1 - offset_x)
            y1 = max(0, y1 - offset_y)
            x2 = min(width, x2 + offset_x)
            y2 = min(height, y2 + offset_y)
            
            cropped_frame = frame[y1:y2, x1:x2]
            
            # Vytvorte čierny rámec s pôvodnou veľkosťou videa
            black_frame = frame.copy()
            black_frame[:] = 0  # Nastavenie rámu na čiernu farbu

            # Vložte výrez do čierneho rámu
            cropped_height, cropped_width = cropped_frame.shape[:2]
            black_frame[y1:y1+cropped_height, x1:x1+cropped_width] = cropped_frame
            
            # Nastavte výstupný video zapisovač s pôvodným rozlíšením
            if out is None:
                out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
            
            # Uložte upravený rám do výstupného videa
            out.write(black_frame)
        
        frame_count += 1
    
    # Uvoľnite objekty
    cap.release()
    if out:
        out.release()


def prepare_data_for_clip(video_id, video_path, db_manager, output_dir, debug_flag=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    detections, all_bounding_boxes = fetch_detections_and_bounding_boxes(video_id, db_manager)

    if debug_flag:
        detections = detections[:1]

    for detection in detections:
        detection_id = detection['id']
        
        # TODO potom zmazat
        if float(detection['confidence']) < 0.80:
            continue
        
        bounding_boxes = all_bounding_boxes.get(detection_id, [])
        
        if not bounding_boxes:
            print(f"Žiadne bounding boxy pre detekciu {detection_id}. Preskakujem...")
            continue
        
        crop_video_for_detection(video_path, detection, bounding_boxes, output_dir, video_id)

if __name__ == "__main__":
    db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db_manager.connect()

    video_id = 36
    video_path = '../data/input/uvoz2.mp4'
    output_dir = '../data/output/xclip-data'

    prepare_data_for_clip(video_id, video_path, db_manager, output_dir, debug_flag=False)

    db_manager.close()
