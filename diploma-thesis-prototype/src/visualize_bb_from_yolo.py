import cv2
import argparse
from database_manager import DatabaseManager

"""It assigns bounding boxes for all detections in the given video and saves the entire video."""
def assign_bounding_boxes_to_video(db_manager, video_id, video_path, output_video_path, skip_frames, num_of_skip_frames):
    
    detections = db_manager.fetch_detections_by_video_id(video_id)
    
    if not detections:
        print(f"No detections for the video with ID {video_id}.")
        return
    
    print(f"I am assigning bounding boxes for all detections in the video with ID {video_id}.")
    
    # load video
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # set parameter for output video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  

    # Setting up VideoWriter to save the video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    # Check if video was loaded correctly
    if total_frames <= 0:
        print(f"Error: The video with ID ${video_id} has no frames.")
        return

    # Assign bounding boxes to the correct detections.
    all_bounding_boxes = {}
    for detection in detections:
        detection_id = detection['id']
        bounding_boxes = db_manager.fetch_bounding_boxes_by_detection_id(detection_id)
        all_bounding_boxes[detection_id] = {bbox['frame_id']: bbox['bbox'] for bbox in bounding_boxes}

    # Assign the bounding box to each frame in the video if it contains any detection.
    for frame_id in range(total_frames):
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Process every nth frame
        if skip_frames == True and (frame_id % num_of_skip_frames != 0):
            continue
        
        for detection in detections:
            detection_id = detection['id']
            bbox = all_bounding_boxes.get(detection_id, {}).get(frame_id)

            # Create bb for frame
            if bbox:
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                label = f"Track ID: {detection['track_id']}, Frame: {frame_id}, Detection ID: {detection['id']}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Adding the frame_id number to the corner of the video
        cv2.putText(frame, f"Frame: {frame_id}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"The video has been saved to: {output_video_path}")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Assign bounding boxes to detections in a video.")
    parser.add_argument('--video_id', required=True, type=int, help="The ID of the video to process.")
    parser.add_argument('--video_path', required=True, type=str, help="The path to the input video file.")
    parser.add_argument('--output_video_path', required=True, type=str, help="The path where the output video will be saved.")
    parser.add_argument('--skip_frames', type=bool, default=True, help="Whether to skip frames.")
    parser.add_argument('--num_of_skip_frames', type=int, default=5, help="The number of frames to skip.")

    args = parser.parse_args()

    # Initialize connection to the database and call the function
    db_manager = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db_manager.connect()

    assign_bounding_boxes_to_video(
        db_manager,
        args.video_id,
        args.video_path,
        args.output_video_path,
        args.skip_frames,
        args.num_of_skip_frames
    )

    db_manager.close()