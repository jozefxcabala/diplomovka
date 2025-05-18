#!/bin/bash

#!/bin/bash

# This script extracts the key parameter values from a list of JSON result files containing top F1-score experiment results.
#
# Functionality:
# - Defines a list of specific result JSON files.
# - Iterates through each file.
# - Uses `jq` to extract and display selected request parameters such as threshold, confidence threshold, top_k, etc.
#
# Useful for reviewing configurations that led to the best performing results.

echo "📋 Extracting parameters from top F1 score result files..."

# List of specific result files
files=(
  "find_best_parameters/experiment_result_34_20250508_033222.json"
  "find_best_parameters/experiment_result_31_20250508_031856.json"
  "find_best_parameters/experiment_result_28_20250508_030445.json"
  "find_best_parameters/experiment_result_43_20250508_041414.json"
  "find_best_parameters/experiment_result_40_20250508_040036.json"
)

# Iterate through each file and print selected parameters
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