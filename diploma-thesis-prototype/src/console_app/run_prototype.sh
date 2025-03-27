#!/bin/bash

# Parse the video_path argument
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --video_path) video_path="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Check if the video_path variable is set
if [ -z "$video_path" ]; then
    echo "Error: --video_path argument is required"
    exit 1
fi

# Run the Python script with the provided video path
python main.py --video_path "$video_path"
