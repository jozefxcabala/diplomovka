import os
import cv2
from database_manager import DatabaseManager
import argparse
import time

def create_bb_map(bounding_boxes): 
    bb_map = {}

    # Create a map of frame_id to bounding box coordinates
    for bb in bounding_boxes:
        bb_map[int(bb['frame_id'])] = list(map(int, bb['bbox']))

    return bb_map

def fetch_detections_and_bounding_boxes(video_id, db_manager):
    # Fetch detections for the given video_id from the database
    detections = db_manager.fetch_detections_by_video_id(video_id)
    all_bounding_boxes = {}

    # Fetch bounding boxes for each detection
    for detection in detections:
        detection_id = detection['id']
        bounding_boxes = db_manager.fetch_bounding_boxes_by_detection_id(detection_id)
        all_bounding_boxes[detection_id] = create_bb_map(bounding_boxes)

    return detections, all_bounding_boxes

def crop_video_for_detection(input_video_path, detection, frame_bbox_map, output_dir, video_id, offset_x, offset_y, size_threshold):
    # Open the input video
    cap = cv2.VideoCapture(input_video_path)
    output_video_path = os.path.join(output_dir, f"video_{video_id}_detection_{detection['id']}.mp4")
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS) 
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
    # Initialize output video writer (resolution according to crop)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    frame_count = 0  # Frame counter

    prev_bbox = None
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break 
        
        # Check if frame_id exists in the map or within the detection range
        if frame_count in frame_bbox_map or (frame_count > int(detection['start_frame']) and frame_count < int(detection['end_frame'])):
            bbox = frame_bbox_map.get(frame_count, False)

            # Perform crop based on the bounding box, if it is skipped frame use previous crop
            if bbox:
                x1, y1, x2, y2 = map(int, bbox)
            else: 
                x1, y1, x2, y2 = prev_bbox

            # Check if bounding box coordinations do not change significantly
            if prev_bbox and (abs(prev_bbox[2] - x2) > size_threshold or abs(prev_bbox[3] - y2) > size_threshold):
                # print(f"Bounding box size changed significantly, using previous dimensions.")
                x1, y1, x2, y2 = prev_bbox 
            else:
                prev_bbox = (x1, y1, x2, y2)
            
            # Account for offsets but ensure they do not exceed video dimensions
            x1 = max(0, x1 - offset_x)
            y1 = max(0, y1 - offset_y)
            x2 = min(width, x2 + offset_x)
            y2 = min(height, y2 + offset_y)
            
            cropped_frame = frame[y1:y2, x1:x2]
            
            # Create a black frame with the original video size
            black_frame = frame.copy()
            black_frame[:] = 0  # Set frame to black

            # Insert the cropped frame into the black frame
            cropped_height, cropped_width = cropped_frame.shape[:2]
            black_frame[y1:y1+cropped_height, x1:x1+cropped_width] = cropped_frame
            
            out.write(black_frame)
        
        frame_count += 1
    
    cap.release()
    out.release()


def prepare_data_for_xclip(video_id, video_path, db_manager, output_dir, offset_x, offset_y, size_threshold):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    detections, all_bounding_boxes = fetch_detections_and_bounding_boxes(video_id, db_manager)

    for detection in detections:
        detection_id = detection['id']
        
        bounding_boxes = all_bounding_boxes.get(detection_id, [])
        
        if not bounding_boxes:
            print(f"No bounding boxes for detection {detection_id}. Skipping...")
            continue
        
        crop_video_for_detection(video_path, detection, bounding_boxes, output_dir, video_id, offset_x, offset_y, size_threshold)

if __name__ == "__main__":
    # Parsing command-line arguments
    parser = argparse.ArgumentParser(description="Prepare video data for analysis.")
    parser.add_argument('--video_id', required=True, type=int, help="ID of the video to process.")
    parser.add_argument('--video_path', required=True, type=str, help="Path to the input video file.")
    parser.add_argument('--output_dir', required=True, type=str, help="Directory where cropped videos will be saved.")
    parser.add_argument('--size_threshold', required=True, type=int, help="Threshold for bounding box size change.")
    parser.add_argument('--offset_x', required=True, type=int, help="Offset for bounding box cropping (x-axis).")
    parser.add_argument('--offset_y', required=True, type=int, help="Offset for bounding box cropping (y-axis).")
    
    args = parser.parse_args()

    db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db_manager.connect()

    start_time = time.time()

    print("The program for preparing data for XCLIP action recognition has started.")

    prepare_data_for_xclip(args.video_id, args.video_path, db_manager, args.output_dir, args.offset_x, args.offset_y, args.size_threshold)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Program finished. It took {elapsed_time:.2f} seconds.")

    db_manager.close()