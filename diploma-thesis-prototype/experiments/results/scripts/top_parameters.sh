#!/bin/bash

echo "📋 Extracting parameters from top F1 score result files..."

# Zoznam konkrétnych súborov
files=(
  "find_best_parameters/experiment_result_34_20250508_033222.json"
  "find_best_parameters/experiment_result_31_20250508_031856.json"
  "find_best_parameters/experiment_result_28_20250508_030445.json"
  "find_best_parameters/experiment_result_43_20250508_041414.json"
  "find_best_parameters/experiment_result_40_20250508_040036.json"
)

# Iterácia cez každý súbor a výpis požadovaných parametrov
for file in "${files[@]}"; do
  echo -e "\n📄 $file"
  jq '.request_data | {
    threshold,
    confidence_threshold,
    top_k,
    batch_size,
    frame_sample_rate,
    skip_frames,
    num_of_skip_frames
  }' "$file"
done