#!/bin/bash

python main.py --video_path ../data/input/street3m.mp4 --output_dir ../data/output/clips --model_path ../data/models/yolo11n.pt --num_segments 8 --processing_mode parallel --classes_to_detect 0

