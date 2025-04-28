# This script contains a helper functions for interaction with video.

import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip

# The `split_video` function divides the video into `num_segments` parts for parallel processing,
# based on the total number of frames, to enable more efficient processing.
def split_video(video_path, num_segments):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    segment_length = total_frames // num_segments

    if segment_length < 1000:
        segment_length = total_frames
        num_segments = 1

    segments = []

    for i in range(num_segments):
        start_frame = i * segment_length
        end_frame = (i + 1) * segment_length if i < num_segments - 1 else total_frames
        segments.append((start_frame, end_frame))

    return segments

def compress_video(input_path, output_path, bitrate="500k", preset="ultrafast"):
    input_video = VideoFileClip(input_path)
    input_video.write_videofile(output_path, preset=preset, bitrate=bitrate)