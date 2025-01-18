#!/bin/bash

python visualize_bb_from_yolo.py --video_id 36  --video_path "../data/input/uvoz2.mp4" --output_video_path "../data/output/uvoz2_with_bboxes.mp4" --skip_frames True --num_of_skip_frames 5
